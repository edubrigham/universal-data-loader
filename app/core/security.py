"""
Security-related functions and dependencies for the API.
"""

import os
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

# Define the header where the API key is expected
API_KEY_HEADER = APIKeyHeader(name="x-api-key", auto_error=False)

# This would be securely stored, e.g., in a secrets manager. For this app, we use an env var.
API_SECRET_KEY = os.getenv("API_SECRET_KEY")

async def get_api_key(api_key_header: str = Security(API_KEY_HEADER)):
    """
    Dependency that checks for and validates the API key from the header.
    
    Raises:
        HTTPException: If the API key is missing or invalid.
    """
    if not API_SECRET_KEY:
        # If the server has no key configured, we should not allow any access.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API secret key not configured on the server."
        )
        
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="API key is missing."
        )

    if api_key_header != API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key."
        )
    
    return api_key_header 