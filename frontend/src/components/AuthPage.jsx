import React, { useState } from "react";
import { Mail, Lock, User, Building2, Eye, EyeOff, ArrowRight, ShieldCheck, HeartPulse } from "lucide-react";
import { auth } from "../firebase";
import { signInWithEmailAndPassword, createUserWithEmailAndPassword, updateProfile } from "firebase/auth";
import API_URL from "../api";

export default function AuthPage({ onLogin }) {
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Form fields
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [centerName, setCenterName] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const resetFields = () => {
    setError("");
    setFullName("");
    setEmail("");
    setPassword("");
    setConfirmPassword("");
    setCenterName("");
  };

  const switchMode = (m) => {
    resetFields();
    setMode(m);
  };

  const generateMockJWT = (email, name) => {
    const header = { alg: "HS256", typ: "JWT" };
    const payload = {
      sub: "mock_" + btoa(email).replace(/[^a-zA-Z0-9]/g, "").slice(0, 15),
      email: email,
      name: name || email.split("@")[0],
      exp: Math.floor(Date.now() / 1000) + 86400 // 24 hours
    };
    
    const toBase64 = (obj) => {
      // Use standard encoding safely
      return btoa(JSON.stringify(obj))
        .replace(/=/g, "")
        .replace(/\+/g, "-")
        .replace(/\//g, "_");
    };

    const headerB64 = toBase64(header);
    const payloadB64 = toBase64(payload);
    const signatureB64 = "mock_signature_part";
    
    return `${headerB64}.${payloadB64}.${signatureB64}`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Validation
    if (mode === "register") {
      if (!fullName.trim()) return setError("Please enter your full name");
      if (password.length < 6) return setError("Password must be at least 6 characters");
      if (password !== confirmPassword) return setError("Passwords do not match");
    }
    if (!email.trim()) return setError("Please enter your email");
    if (!password) return setError("Please enter your password");

    const isMockFirebase = !import.meta.env.VITE_FIREBASE_API_KEY || 
                           import.meta.env.VITE_FIREBASE_API_KEY.includes("DummyKey") || 
                           import.meta.env.VITE_FIREBASE_API_KEY === "";

    setLoading(true);
    try {
      let idToken;
      let syncUid;
      let syncEmail = email;
      let syncName = fullName;

      if (isMockFirebase) {
        // Offline mock authentication mode
        idToken = generateMockJWT(email, fullName || email.split("@")[0]);
        syncUid = "mock_" + btoa(email).replace(/[^a-zA-Z0-9]/g, "").slice(0, 15);
      } else {
        // Real Firebase Auth
        let userCredential;
        if (mode === "login") {
          userCredential = await signInWithEmailAndPassword(auth, email, password);
        } else {
          userCredential = await createUserWithEmailAndPassword(auth, email, password);
          await updateProfile(userCredential.user, {
            displayName: fullName
          });
        }
        const fbUser = userCredential.user;
        idToken = await fbUser.getIdToken();
        syncUid = fbUser.uid;
        syncEmail = fbUser.email;
        syncName = fullName || fbUser.displayName || fbUser.email.split("@")[0];
      }

      // Sync user data with local backend DB to persist center_name / full_name
      const syncRes = await fetch(`${API_URL}/api/auth/sync`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${idToken}`
        },
        body: JSON.stringify({
          uid: syncUid,
          email: syncEmail,
          full_name: syncName,
          center_name: centerName || null
        }),
      });

      const syncData = await syncRes.json();

      if (!syncRes.ok) {
        throw new Error(syncData.detail || "Failed to sync user with local DB");
      }

      // Store token & user info
      localStorage.setItem("poshanai_token", idToken);
      localStorage.setItem("poshanai_user", JSON.stringify(syncData));
      onLogin(idToken, syncData);
    } catch (err) {
      console.error(err);
      let errMsg = err.message;
      if (err.code === "auth/invalid-credential" || err.code === "auth/user-not-found" || err.code === "auth/wrong-password") {
        errMsg = "Invalid email or password";
      } else if (err.code === "auth/email-already-in-use") {
        errMsg = "An account with this email already exists";
      } else if (err.code === "auth/weak-password") {
        errMsg = "Password is too weak. Must be at least 6 characters.";
      }
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #020617 100%)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "24px",
      position: "relative",
      overflow: "hidden"
    }}>
      {/* Decorative blurred orbs */}
      <div style={{
        position: "absolute", top: "-120px", left: "-80px",
        width: "400px", height: "400px", borderRadius: "50%",
        background: "radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)",
        filter: "blur(60px)", pointerEvents: "none"
      }} />
      <div style={{
        position: "absolute", bottom: "-100px", right: "-60px",
        width: "350px", height: "350px", borderRadius: "50%",
        background: "radial-gradient(circle, rgba(168,85,247,0.12) 0%, transparent 70%)",
        filter: "blur(60px)", pointerEvents: "none"
      }} />

      {/* Main Card */}
      <div style={{
        background: "rgba(30, 41, 59, 0.55)",
        backdropFilter: "blur(24px)",
        WebkitBackdropFilter: "blur(24px)",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: "24px",
        boxShadow: "0 25px 60px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.03)",
        width: "100%",
        maxWidth: "460px",
        padding: "40px 36px 36px",
        animation: "fadeInUp 0.4s ease",
        position: "relative",
        zIndex: 1
      }}>
        {/* Logo & Branding */}
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
          <div style={{
            width: "64px", height: "64px", borderRadius: "18px",
            background: "linear-gradient(135deg, #6366f1, #a855f7)",
            display: "flex", alignItems: "center", justifyContent: "center",
            margin: "0 auto 16px", boxShadow: "0 8px 24px rgba(99,102,241,0.3)"
          }}>
            <HeartPulse size={30} color="#fff" />
          </div>
          <h1 style={{
            fontSize: "1.65rem", fontWeight: "800", letterSpacing: "-0.5px",
            background: "linear-gradient(135deg, #ffffff, #a5b4fc)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent"
          }}>
            PoshanAI
          </h1>
          <p style={{ color: "#64748b", fontSize: "0.85rem", marginTop: "6px" }}>
            AI-Powered Child Malnutrition Detection
          </p>
        </div>

        {/* Tab Switcher */}
        <div style={{
          display: "flex", background: "rgba(15,23,42,0.5)", borderRadius: "12px",
          padding: "4px", marginBottom: "28px", border: "1px solid rgba(255,255,255,0.06)"
        }}>
          {["login", "register"].map((m) => (
            <button
              key={m}
              onClick={() => switchMode(m)}
              style={{
                flex: 1, padding: "10px 0", borderRadius: "9px", border: "none",
                background: mode === m ? "linear-gradient(135deg, #6366f1, #4f46e5)" : "transparent",
                color: mode === m ? "#fff" : "#64748b",
                fontWeight: "600", fontSize: "0.9rem", cursor: "pointer",
                transition: "all 0.25s ease",
                boxShadow: mode === m ? "0 4px 12px rgba(99,102,241,0.25)" : "none"
              }}
            >
              {m === "login" ? "Sign In" : "Create Account"}
            </button>
          ))}
        </div>

        {/* Error Banner */}
        {error && (
          <div style={{
            background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)",
            borderRadius: "10px", padding: "10px 14px", marginBottom: "18px",
            color: "#f87171", fontSize: "0.85rem", fontWeight: "500",
            display: "flex", alignItems: "center", gap: "8px"
          }}>
            <ShieldCheck size={16} /> {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {mode === "register" && (
            <InputField
              icon={<User size={17} color="#6366f1" />}
              placeholder="Full Name"
              value={fullName}
              onChange={setFullName}
              type="text"
            />
          )}

          <InputField
            icon={<Mail size={17} color="#6366f1" />}
            placeholder="Email Address"
            value={email}
            onChange={setEmail}
            type="email"
          />

          <InputField
            icon={<Lock size={17} color="#6366f1" />}
            placeholder="Password"
            value={password}
            onChange={setPassword}
            type={showPassword ? "text" : "password"}
            suffix={
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{ background: "none", border: "none", cursor: "pointer", color: "#64748b", display: "flex", padding: "4px" }}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            }
          />

          {mode === "register" && (
            <>
              <InputField
                icon={<Lock size={17} color="#a855f7" />}
                placeholder="Confirm Password"
                value={confirmPassword}
                onChange={setConfirmPassword}
                type={showPassword ? "text" : "password"}
              />
              <InputField
                icon={<Building2 size={17} color="#06b6d4" />}
                placeholder="Anganwadi Center Name (optional)"
                value={centerName}
                onChange={setCenterName}
                type="text"
              />
            </>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              background: loading
                ? "rgba(99,102,241,0.4)"
                : "linear-gradient(135deg, #6366f1, #4f46e5)",
              border: "none", color: "#fff", padding: "14px 0",
              borderRadius: "12px", fontWeight: "700", fontSize: "0.95rem",
              cursor: loading ? "not-allowed" : "pointer",
              display: "flex", alignItems: "center", justifyContent: "center", gap: "10px",
              boxShadow: "0 6px 20px rgba(99,102,241,0.3)",
              transition: "all 0.25s ease", marginTop: "4px"
            }}
          >
            {loading ? (
              <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span className="auth-spinner" /> {mode === "login" ? "Signing in..." : "Creating account..."}
              </span>
            ) : (
              <>
                {mode === "login" ? "Sign In" : "Create Account"}
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        {/* Footer */}
        <p style={{ textAlign: "center", color: "#475569", fontSize: "0.78rem", marginTop: "24px", lineHeight: "1.5" }}>
          Built for <strong style={{ color: "#a78bfa" }}>Anganwadi & ICDS</strong> workers across India
        </p>
      </div>

      {/* Global animations */}
      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .auth-spinner {
          width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.3);
          border-top-color: #fff; border-radius: 50%;
          animation: spin 0.6s linear infinite; display: inline-block;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

// ── Internal: Styled Input Field ─────────────────────────────────────────────

function InputField({ icon, placeholder, value, onChange, type = "text", suffix }) {
  const [focused, setFocused] = useState(false);

  return (
    <div style={{
      display: "flex", alignItems: "center", gap: "12px",
      background: "rgba(15, 23, 42, 0.6)",
      border: `1px solid ${focused ? "rgba(99,102,241,0.5)" : "rgba(255,255,255,0.08)"}`,
      borderRadius: "12px", padding: "0 14px",
      transition: "all 0.25s ease",
      boxShadow: focused ? "0 0 0 3px rgba(99,102,241,0.15)" : "none"
    }}>
      <div style={{ flexShrink: 0, display: "flex" }}>{icon}</div>
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        style={{
          flex: 1, background: "transparent", border: "none", outline: "none",
          color: "#f8fafc", padding: "13px 0", fontSize: "0.92rem",
          fontFamily: "'Outfit', sans-serif"
        }}
      />
      {suffix && <div style={{ flexShrink: 0 }}>{suffix}</div>}
    </div>
  );
}
