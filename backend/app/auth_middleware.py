"""
Firebase Auth Middleware - Extracts and verifies Firebase ID tokens from Authorization header
"""

import logging
from typing import Optional
from fastapi import Request, HTTPException, status
import firebase_admin
from firebase_admin import auth

logger = logging.getLogger(__name__)


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
    return firebase_middleware


def get_auth_middleware() -> FirebaseAuthMiddleware:
    """Get global auth middleware instance"""
    if firebase_middleware is None:
        raise RuntimeError("Auth middleware not initialized")
    return firebase_middleware
