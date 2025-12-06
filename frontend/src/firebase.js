import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { firebaseConfig } from "./config";

console.log("🔍 Firebase Config from config.js:", firebaseConfig);

// Validate config
const isValidConfig = (config) => {
  const requiredFields = ['apiKey', 'authDomain', 'projectId', 'appId'];
  const missingFields = requiredFields.filter(field => !config[field]);
  
  if (missingFields.length > 0) {
    console.error(`❌ Missing config fields: ${missingFields.join(', ')}`);
    return false;
  }
  
  console.log("✅ All required config fields present");
  return true;
};

// Initialize Firebase
let app;
let auth;

try {
  if (!isValidConfig(firebaseConfig)) {
    throw new Error("Firebase config is invalid or incomplete");
  }

  console.log("🚀 Initializing Firebase with config...");
  app = initializeApp(firebaseConfig);
  console.log("✅ Firebase App initialized successfully");
  
  console.log("🚀 Getting Auth instance...");
  auth = getAuth(app);
  console.log("✅ Firebase Auth initialized successfully");
  
} catch (error) {
  console.error("❌ Firebase initialization error:");
  console.error("  Message:", error.message);
  console.error("  Code:", error.code);
  console.error("  Full error:", error);
  
  // Create a mock auth object to prevent crashes
  console.warn("⚠️ Creating mock auth object as fallback");
  auth = {
    currentUser: null,
    _isMock: true
  };
}

export { auth };
export default app;
