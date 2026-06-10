import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// Fallback configuration for easy local developer setup
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyDummyKeyForDevPoshanAI12345",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "poshan-ai-dev.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "poshan-ai-dev",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "poshan-ai-dev.appspot.com",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "123456789012",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:123456789012:web:abcdef1234567890"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
