import time
import json
import urllib.request
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os

# Load .env file if present (for local dev)
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(dotenv_path):
    try:
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")
    except Exception as e:
        print(f"Failed to manually load .env file: {e}")


security = HTTPBearer()

# Cache for Google's public certificates
GOOGLE_CERTS_URL = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
_public_keys = {}
_keys_expiry = 0


def get_google_public_keys():
    global _public_keys, _keys_expiry
    now = time.time()
    if not _public_keys or now > _keys_expiry:
        try:
            with urllib.request.urlopen(GOOGLE_CERTS_URL, timeout=5) as response:
                _public_keys = json.loads(response.read().decode("utf-8"))
                _keys_expiry = now + 3600
        except Exception as e:
            print(f"Failed to fetch Google public keys: {e}")
            if not _public_keys:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication server communication error"
                )
    return _public_keys


def verify_firebase_token(token: str) -> dict:
    project_id = os.getenv("FIREBASE_PROJECT_ID", "poshan-ai-dev")

    try:
        # Decode header without verification to inspect the token type
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        # If there's no `kid` in the header it's our mock JWT – decode claims only
        if not kid:
            payload = jwt.get_unverified_claims(token)
            if payload.get("exp", 0) < time.time():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            uid = payload.get("sub")
            if not uid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing subject"
                )
            return {
                "uid": uid,
                "email": payload.get("email", ""),
                "name": payload.get("name", "")
            }

        # Real Firebase RS256 token – verify fully against Google's public keys
        public_keys = get_google_public_keys()
        public_key = public_keys.get(kid)
        if not public_key:
            # Keys may have rotated; force refresh once and retry
            _public_keys.clear()
            public_keys = get_google_public_keys()
            public_key = public_keys.get(kid)
            if not public_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: unknown signing key"
                )

        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=project_id,
            issuer=f"https://securetoken.google.com/{project_id}"
        )

        uid = payload.get("sub") or payload.get("user_id")
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing uid"
            )

        return {
            "uid": uid,
            "email": payload.get("email", ""),
            "name": payload.get("name", "") or payload.get("display_name", "")
        }

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials or token expired: {str(e)}"
        )


def get_current_firebase_user(cred: HTTPAuthorizationCredentials = Depends(security)):
    return verify_firebase_token(cred.credentials)
