"""
FastAPI dependencies for authentication
"""

import logging
from typing import Optional
from fastapi import Depends, Header, HTTPException, status
from app.auth_middleware import get_auth_middleware

logger = logging.getLogger(__name__)


async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Dependency to get current authenticated user
    
    Usage in endpoint:
    @app.get("/protected")
    async def protected_route(user: dict = Depends(get_current_user)):
        user_id = user.get("uid")
        ...
    
    Args:
        authorization: Authorization header from request
    
    Returns:
        User info dictionary with uid, email, etc.
    
    Raises:
        HTTPException: If not authenticated
    """
    middleware = get_auth_middleware()
    user_info = await middleware.verify_token(authorization)
    
    if not user_info.get("uid"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    return user_info


async def get_user_id(
    user: dict = Depends(get_current_user)
) -> str:
    """
    Dependency to get just the user ID
    
    Usage in endpoint:
    @app.get("/research")
    async def research(user_id: str = Depends(get_user_id)):
        ...
    
    Args:
        user: Current user from get_current_user
    
    Returns:
        User ID (uid)
    """
    return user.get("uid", "default_user")


async def get_user_email(
    user: dict = Depends(get_current_user)
) -> str:
    """
    Dependency to get user email
    
    Args:
        user: Current user from get_current_user
    
    Returns:
        User email address
    """
    return user.get("email", "")
