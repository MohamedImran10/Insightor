"""
Firebase Auth Middleware - Extracts and verifies Firebase ID tokens from Authorization header
"""

import logging
import os
import json
from typing import Optional
from fastapi import Request, HTTPException, status
import firebase_admin
from firebase_admin import auth, credentials

logger = logging.getLogger(__name__)

# Track if Firebase has been initialized
_firebase_initialized = False


def ensure_firebase_initialized():
    """Ensure Firebase Admin SDK is initialized before verifying tokens"""
    global _firebase_initialized
    
    if _firebase_initialized:
        return True
    
    # Check if already initialized by another module
    try:
        firebase_admin.get_app()
        _firebase_initialized = True
        logger.info("✅ Firebase already initialized by another module")
        return True
    except ValueError:
        pass  # App not initialized yet
    
    try:
        # Import settings from config (this loads from .env file)
        from app.config import settings
        
        # Try to initialize from environment variable (JSON string) - for production
        firebase_json = settings.firebase_credentials_json or os.getenv('FIREBASE_CREDENTIALS_JSON')
        if firebase_json:
            logger.info("🔍 Found FIREBASE_CREDENTIALS_JSON, attempting to initialize...")
            cred_dict = json.loads(firebase_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            _firebase_initialized = True
            logger.info("✅ Firebase initialized from FIREBASE_CREDENTIALS_JSON")
            return True
        
        # Try to initialize from file path - for local development
        firebase_path = settings.firebase_credentials_path or os.getenv('FIREBASE_CREDENTIALS_PATH')
        logger.info(f"🔍 FIREBASE_CREDENTIALS_PATH = {firebase_path}")
        
        if firebase_path:
            # Check if file exists
            if os.path.exists(firebase_path):
                logger.info(f"📁 Firebase credentials file found at: {firebase_path}")
                cred = credentials.Certificate(firebase_path)
                firebase_admin.initialize_app(cred)
                _firebase_initialized = True
                logger.info(f"✅ Firebase initialized from file: {firebase_path}")
                return True
            else:
                logger.error(f"❌ Firebase credentials file NOT found at: {firebase_path}")
        else:
            logger.warning("⚠️ FIREBASE_CREDENTIALS_PATH not set")
        
        logger.warning("⚠️ No Firebase credentials found - check FIREBASE_CREDENTIALS_PATH or FIREBASE_CREDENTIALS_JSON")
        return False
        
    except Exception as e:
        logger.error(f"❌ Firebase initialization failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


class FirebaseAuthMiddleware:
    """Middleware to extract and verify Firebase tokens"""
    
    def __init__(self, firebase_enabled: bool = True):
        """
        Initialize middleware
        
        Args:
            firebase_enabled: Whether Firebase auth is enabled
        """
        self.firebase_enabled = firebase_enabled
    
    async def verify_token(self, authorization_header: Optional[str]) -> dict:
        """
        Verify Firebase ID token from Authorization header
        
        Args:
            authorization_header: Authorization header value (Bearer <token>)
        
        Returns:
            Dictionary with decoded token claims
        
        Raises:
            HTTPException: If token is invalid or missing
        """
        if not self.firebase_enabled:
            # If Firebase disabled, return default user
            logger.debug("Firebase disabled, using default user")
            return {"uid": "default_user", "email": "demo@example.com"}
        
        if not authorization_header:
            logger.warning("Missing Authorization header")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization header"
            )
        
        # Extract token from "Bearer <token>"
        try:
            scheme, token = authorization_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authorization scheme")
        except ValueError:
            logger.warning("Invalid Authorization header format")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header format. Use: Bearer <token>"
            )
        
        # Ensure Firebase is initialized before verifying token
        if not ensure_firebase_initialized():
            logger.error("Firebase not initialized, cannot verify token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication service not available"
            )
        
        # Verify token with Firebase
        try:
            decoded_token = auth.verify_id_token(token)
            user_id = decoded_token.get("uid")
            email = decoded_token.get("email", "")
            
            logger.info(f"✅ Token verified for user {user_id}")
            
            return {
                "uid": user_id,
                "email": email,
                "email_verified": decoded_token.get("email_verified", False),
                "name": decoded_token.get("name", ""),
            }
        
        except firebase_admin.auth.InvalidIdTokenError:
            logger.warning("Invalid Firebase ID token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired Firebase token"
            )
        except firebase_admin.auth.ExpiredIdTokenError:
            logger.warning("Expired Firebase ID token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firebase token has expired"
            )
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )


# Global middleware instance
firebase_middleware: Optional[FirebaseAuthMiddleware] = None


def initialize_auth_middleware(firebase_enabled: bool = True):
    """Initialize auth middleware globally"""
    global firebase_middleware
    firebase_middleware = FirebaseAuthMiddleware(firebase_enabled=firebase_enabled)
    logger.info(f"🔐 Auth middleware initialized (Firebase: {'enabled' if firebase_enabled else 'disabled'})")
    
    # Initialize Firebase immediately if enabled
    if firebase_enabled:
        logger.info("🔥 Attempting to initialize Firebase Admin SDK...")
        if ensure_firebase_initialized():
            logger.info("✅ Firebase Admin SDK ready")
        else:
            logger.warning("⚠️ Firebase Admin SDK initialization failed - auth will not work")
    
    return firebase_middleware


def get_auth_middleware() -> FirebaseAuthMiddleware:
    """Get global auth middleware instance"""
    if firebase_middleware is None:
        raise RuntimeError("Auth middleware not initialized")
    return firebase_middleware
