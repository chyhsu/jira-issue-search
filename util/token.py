import requests
import json
from typing import Optional, Dict, Any
from scheme.token import TokenInfo, UserInfo
from util.logger import get_logger

# Constants equivalent to the Go code
TOKEN_INFO_PATTERN = "{}/oauth/tokeninfo?access_token={}"
HEADER_X_QNAP_APP_ID = "X-QNAP-APP-ID"
DEFAULT_TIMEOUT = 5  # seconds
logger = get_logger(__name__)

class TokenError(Exception):
    """Exception raised for token-related errors."""
    pass


class Token:
    def __init__(self, auth_url: str, app_id: str):
        """
        Initialize the Token service.
        
        Args:
            auth_url: The OAuth authentication URL
            app_id: The application ID for the API
        """
        self.auth_url = auth_url
        self.app_id = app_id
    
    def get_token_info(self, access_token: str) -> (TokenInfo | str):
        """
        Get token information from the OAuth server.
        
        Args:
            access_token: The access token to validate
            
        Returns:
            (TokenInfo | None, str): A tuple containing the token information and an error message
            
        Raises:
            TokenError: If access_token is empty or if there's an error in the request
        """
        if not access_token:
            return  "access token is empty"
        
        uri = TOKEN_INFO_PATTERN.format(self.auth_url, access_token)
        
        try:
            response = requests.get(
                uri,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    HEADER_X_QNAP_APP_ID: self.app_id
                },
                timeout=DEFAULT_TIMEOUT
            )
            
            # Ensure the request was successful
            response.raise_for_status()
            
            # Parse the JSON response
            result_dict = response.json()
            
            # Check for error in the response
            if result_dict.get("error"):
                return f"error in token info response"
      
            # Create TokenInfo object from response
            token_info = TokenInfo(
                client_id=result_dict.get("client_id"),
                scope=result_dict.get("scope"),
                expires_in=result_dict.get("expires_in"),
                user=UserInfo(
                    id=result_dict.get("user_id"),
                    email=result_dict.get("user").get("email"),
                    display_name=result_dict.get("user").get("display_name"),
                )
            )
            
            return token_info
            
        except requests.RequestException as e:
            logger.error(f"Failed to get token info: {e}")
            return f"failed to get token info"
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse token info response: {e}")
            return f"failed to parse token info response"


def create_token_service(auth_url: str, app_id: str) -> Token:
    """
    Create a new Token service instance.
    
    Args:
        auth_url: The OAuth authentication URL
        app_id: The application ID for the API
        
    Returns:
        A new Token service instance
        
    Raises:
        TokenError: If auth_url is empty
    """
    if not auth_url:
        raise TokenError("auth URL is empty")
    
    return Token(auth_url, app_id)
