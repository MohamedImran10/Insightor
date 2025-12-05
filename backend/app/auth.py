"""
Firebase Auth Module - Handles JWT token verification and user authentication
Provides dependency injection for protected endpoints
"""

import logging
from typing import Optional

import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer

logger = logging.getLogger(__name__)

security = HTTPBearer()


class FirebaseAuth:
    """
    Firebase authentication handler
    Verifies ID tokens and extracts user information
    """
    
    _instance = None
    
    def __new__(cls, credentials_path: Optional[str] = None):
        """Singleton pattern for Firebase app initialization"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Firebase Admin SDK
        
        Args:
            credentials_path: Path to Firebase service account JSON
                            If None, uses GOOGLE_APPLICATION_CREDENTIALS env var
        """
        if self._initialized:
            return
        
        try:
            logger.info("🔐 Initializing Firebase Admin SDK")
            
            # Initialize Firebase (uses environment variables by default)
            if credentials_path:
                creds = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(creds)
            else:
                # Uses GOOGLE_APPLICATION_CREDENTIALS environment variable
                firebase_admin.initialize_app()
            
            self._initialized = True
            logger.info("✅ Firebase Admin SDK initialized")
        
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase: {str(e)}")
            raise
    
    async def verify_token(self, token: str) -> dict:
        """
        Verify Firebase ID token and return decoded claims
        
        Args:
            token: Firebase ID token from Authorization header
        
        Returns:
            Dictionary with decoded token claims including 'uid', 'email', etc.
        
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Remove "Bearer " prefix if present
            if token.startswith("Bearer "):
                token = token[7:]
            
            # Verify token
            decoded_token = auth.verify_id_token(token)
            logger.info(f"✅ Token verified for user {decoded_token.get('uid')[:8]}...")
            return decoded_token
        
        except firebase_admin.auth.InvalidIdTokenError:
            logger.warning("⚠️  Invalid ID token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        except firebase_admin.auth.ExpiredIdTokenError:
            logger.warning("⚠️  Expired ID token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired"
            )
        except Exception as e:
            logger.error(f"❌ Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    async def get_user_id(self, credentials = Depends(security)) -> str:
        """
        Dependency injection function to extract user_id from request
        Use this in endpoint definitions like:
        
        @app.get("/protected")
        async def protected_endpoint(user_id: str = Depends(firebase_auth.get_user_id)):
            ...
        
        Args:
            credentials: HTTP Bearer token from Authorization header
        
        Returns:
            User ID (uid) from decoded token
        
        Raises:
            HTTPException: If authentication fails
        """
        token = credentials.credentials
        decoded_token = await self.verify_token(token)
        return decoded_token.get("uid")
    
    async def get_user_info(self, credentials = Depends(security)) -> dict:
        """
        Extract complete user info from token
        
        Args:
            credentials: HTTP Bearer token
        
        Returns:
            Dictionary with user info (uid, email, name, email_verified, etc.)
        """
        token = credentials.credentials
        decoded_token = await self.verify_token(token)
        
        return {
            "uid": decoded_token.get("uid"),
            "email": decoded_token.get("email"),
            "name": decoded_token.get("name"),
            "email_verified": decoded_token.get("email_verified"),
            "iss": decoded_token.get("iss"),
            "aud": decoded_token.get("aud")
        }


# Global Firebase instance
firebase_auth: Optional[FirebaseAuth] = None


def initialize_firebase(credentials_path: Optional[str] = None) -> FirebaseAuth:
    """
    Initialize Firebase globally (call once on app startup)
    
    Args:
        credentials_path: Path to Firebase service account JSON
    
    Returns:
        FirebaseAuth instance
    """
    global firebase_auth
    firebase_auth = FirebaseAuth(credentials_path)
    return firebase_auth


def get_firebase_auth() -> FirebaseAuth:
    """Get global Firebase instance"""
    if firebase_auth is None:
        raise RuntimeError("Firebase not initialized. Call initialize_firebase() on app startup.")
    return firebase_auth
