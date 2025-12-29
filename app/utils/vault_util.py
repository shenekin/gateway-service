"""
HashiCorp Vault utility for secret management
"""
import os
from typing import Optional, Dict, Any
import hvac
from app.settings import get_settings


class VaultUtil:
    """Utility class for interacting with HashiCorp Vault"""
    
    def __init__(self):
        """Initialize Vault client"""
        self.settings = get_settings()
        self.client: Optional[hvac.Client] = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to Vault and authenticate"""
        try:
            # Get Vault configuration from settings (preferred) or environment (fallback)
            vault_addr = self.settings.vault_addr if hasattr(self.settings, 'vault_addr') else os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
            vault_auth_method = self.settings.vault_auth_method if hasattr(self.settings, 'vault_auth_method') else os.getenv("VAULT_AUTH_METHOD", "approle")
            vault_timeout = self.settings.vault_timeout if hasattr(self.settings, 'vault_timeout') else int(os.getenv("VAULT_TIMEOUT", "5"))
            vault_verify = self.settings.vault_verify if hasattr(self.settings, 'vault_verify') else os.getenv("VAULT_VERIFY", "true").lower() == "true"
            
            # Create Vault client with timeout and SSL verification
            self.client = hvac.Client(
                url=vault_addr,
                timeout=vault_timeout,
                verify=vault_verify
            )
            
            # Authenticate based on method
            if vault_auth_method == "approle":
                # Get credentials from settings (preferred) or environment (fallback)
                role_id = self.settings.vault_role_id if hasattr(self.settings, 'vault_role_id') else os.getenv("VAULT_ROLE_ID")
                secret_id = self.settings.vault_secret_id if hasattr(self.settings, 'vault_secret_id') else os.getenv("VAULT_SECRET_ID")
                
                if not role_id or not secret_id:
                    raise ValueError("VAULT_ROLE_ID and VAULT_SECRET_ID must be set for approle authentication")
                
                # Authenticate with AppRole
                response = self.client.auth.approle.login(
                    role_id=role_id,
                    secret_id=secret_id
                )
                
                # Set token
                self.client.token = response['auth']['client_token']
                
            elif vault_auth_method == "token":
                # Get token from settings (preferred) or environment (fallback)
                vault_token = self.settings.vault_token if hasattr(self.settings, 'vault_token') else os.getenv("VAULT_TOKEN")
                if not vault_token:
                    raise ValueError("VAULT_TOKEN must be set for token authentication")
                self.client.token = vault_token
            
            else:
                raise ValueError(f"Unsupported Vault auth method: {vault_auth_method}")
            
            # Verify connection
            if not self.client.is_authenticated():
                raise ConnectionError("Failed to authenticate with Vault")
                
        except Exception as e:
            self.client = None
            error_msg = str(e)
            if "sealed" in error_msg.lower():
                raise ConnectionError(f"Vault is sealed. Please unseal Vault first: {error_msg}")
            raise ConnectionError(f"Failed to connect to Vault: {error_msg}")
    
    def read_secret(self, path: str) -> Dict[str, Any]:
        """
        Read secret from Vault
        
        Args:
            path: Secret path in Vault (e.g., "secret/jwt/hs256" or "jwt/hs256")
                  For KV v2, if path starts with "secret/", it will be stripped
                  as the mount point is already "secret"
            
        Returns:
            Secret data dictionary
        """
        if not self.client:
            raise ConnectionError("Vault client not initialized")
        
        try:
            # For KV v2, if path starts with "secret/", remove it
            # The mount point is already "secret", so we just need the sub-path
            if path.startswith("secret/"):
                path = path[len("secret/"):]
            
            # Read from KV v2 secrets engine
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            return response['data']['data']
        except Exception as e:
            raise ValueError(f"Failed to read secret from path '{path}': {str(e)}")
    
    def get_jwt_secret(self, algorithm: str = "HS256") -> str:
        """
        Get JWT secret key from Vault
        
        Args:
            algorithm: JWT algorithm (HS256 or RS256)
            
        Returns:
            JWT secret key
        """
        # Get path from settings (preferred) or environment (fallback)
        if algorithm == "HS256":
            path = self.settings.jwt_vault_hs256_path if hasattr(self.settings, 'jwt_vault_hs256_path') else os.getenv("JWT_VAULT_HS256_PATH", "secret/jwt/hs256")
        elif algorithm == "RS256":
            path = self.settings.jwt_vault_rs256_path if hasattr(self.settings, 'jwt_vault_rs256_path') else os.getenv("JWT_VAULT_RS256_PATH", "secret/jwt/rs256")
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        secret_data = self.read_secret(path)
        
        # Try common key names
        for key in ['secret', 'key', 'secret_key', 'jwt_secret', 'value']:
            if key in secret_data:
                return secret_data[key]
        
        # If no common key found, return first value
        if secret_data:
            return list(secret_data.values())[0]
        
        raise ValueError(f"No secret found in path '{path}'")
    
    def get_api_key(self, api_key_name: str = "gateway") -> str:
        """
        Get API key from Vault
        
        Args:
            api_key_name: API key name/identifier
            
        Returns:
            API key value
        """
        # Get base path from settings (preferred) or environment (fallback)
        base_path = self.settings.api_key_vault_path if hasattr(self.settings, 'api_key_vault_path') else os.getenv("API_KEY_VAULT_PATH", "secret/api-keys")
        path = f"{base_path}/{api_key_name}" if not base_path.endswith(api_key_name) else base_path
        secret_data = self.read_secret(path)
        
        # Try common key names
        for key in ['api_key', 'key', 'value', 'secret']:
            if key in secret_data:
                return secret_data[key]
        
        # If no common key found, return first value
        if secret_data:
            return list(secret_data.values())[0]
        
        raise ValueError(f"No API key found in path '{path}'")
    
    def is_connected(self) -> bool:
        """Check if Vault client is connected and authenticated"""
        return self.client is not None and self.client.is_authenticated()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check Vault health
        
        Returns:
            Health status dictionary
        """
        if not self.client:
            return {
                "status": "disconnected",
                "error": "Vault client not initialized"
            }
        
        try:
            health = self.client.sys.read_health_status()
            return {
                "status": "healthy" if health.get("initialized") else "uninitialized",
                "sealed": health.get("sealed", False),
                "standby": health.get("standby", False),
                "version": health.get("version", "unknown")
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
