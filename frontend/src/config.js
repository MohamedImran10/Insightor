// Frontend configuration - uses environment variables for production

export const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyBxpszilq0JKzEsT9QgLPdU2Z0dEHhFu4s",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "research-agent-b7cb0.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "research-agent-b7cb0",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "research-agent-b7cb0.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "1076931863510",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:1076931863510:web:06ec9cbc55c4527abbba77",
};

export const apiBaseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

if (typeof window !== 'undefined') {
  console.log("✅ Config loaded - API URL:", apiBaseUrl);
}
