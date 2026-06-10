// Central API configuration
// Reads from VITE_API_URL env variable.
// In development  → http://127.0.0.1:8000  (from .env.development)
// In production   → https://your-app.onrender.com (from .env.production)

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default API_URL;
