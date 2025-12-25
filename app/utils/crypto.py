"""
Cryptographic utilities for JWT and API key handling
"""

import hashlib
import hmac
from typing import Optional
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


class CryptoUtils:
    """Cryptographic utility functions"""
    
    @staticmethod
    def hash_api_key(api_key: str, salt: Optional[str] = None) -> str:
        """
        Hash API key for storage
        
        Args:
            api_key: Plain API key
            salt: Optional salt for hashing
            
        Returns:
            Hashed API key
        """
        if salt:
            combined = f"{api_key}:{salt}"
        else:
            combined = api_key
        
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def verify_api_key(api_key: str, hashed_key: str, salt: Optional[str] = None) -> bool:
        """
        Verify API key against hash
        
        Args:
            api_key: Plain API key to verify
            hashed_key: Stored hash
            salt: Optional salt used for hashing
            
        Returns:
            True if key matches, False otherwise
        """
        computed_hash = CryptoUtils.hash_api_key(api_key, salt)
        return hmac.compare_digest(computed_hash, hashed_key)
    
    @staticmethod
    def generate_rsa_key_pair() -> tuple[str, str]:
        """
        Generate RSA key pair for JWT signing
        
        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem.decode(), public_pem.decode()
    
    @staticmethod
    def load_private_key(key_path: str) -> Optional[bytes]:
        """
        Load private key from file
        
        Args:
            key_path: Path to private key file
            
        Returns:
            Private key bytes or None if file not found
        """
        try:
            with open(key_path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None
    
    @staticmethod
    def load_public_key(key_path: str) -> Optional[bytes]:
        """
        Load public key from file
        
        Args:
            key_path: Path to public key file
            
        Returns:
            Public key bytes or None if file not found
        """
        try:
            with open(key_path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

