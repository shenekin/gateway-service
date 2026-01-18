"""
Unit tests for JWT import fix
Tests to ensure JWT module can be imported and used correctly
"""

import pytest
import sys
from unittest.mock import Mock, patch


class TestJWTImportFix:
    """Test cases for JWT import fix"""
    
    def test_import_jwt_module(self):
        """
        Test that jwt module can be imported
        
        This test verifies the fix for:
        ModuleNotFoundError: No module named 'jwt'
        """
        try:
            import jwt
            assert jwt is not None
        except ModuleNotFoundError as e:
            if "jwt" in str(e).lower():
                pytest.fail(f"JWT module import failed: {e}. Install PyJWT package.")
            else:
                raise
    
    def test_jwt_decode_function_exists(self):
        """Test that jwt.decode function exists"""
        import jwt
        
        assert hasattr(jwt, 'decode')
        assert callable(jwt.decode)
    
    def test_jwt_exceptions_exist(self):
        """Test that JWT exception classes exist"""
        import jwt
        
        assert hasattr(jwt, 'ExpiredSignatureError')
        assert hasattr(jwt, 'InvalidTokenError')
        assert issubclass(jwt.ExpiredSignatureError, Exception)
        assert issubclass(jwt.InvalidTokenError, Exception)
    
    def test_import_auth_middleware_no_error(self):
        """Test that auth middleware can be imported without JWT import error"""
        try:
            from app.middleware.auth import AuthMiddleware
            assert AuthMiddleware is not None
        except ModuleNotFoundError as e:
            if "jwt" in str(e).lower():
                pytest.fail(f"JWT import error in auth middleware: {e}")
            else:
                raise
    
    def test_auth_middleware_initialization(self):
        """Test that AuthMiddleware can be initialized"""
        from app.middleware.auth import AuthMiddleware
        
        with patch('app.middleware.auth.get_settings') as mock_settings:
            mock_settings.return_value = Mock()
            middleware = AuthMiddleware()
            
            assert middleware is not None
            assert hasattr(middleware, 'authenticate_jwt')
            assert hasattr(middleware, 'authenticate_api_key')
    
    def test_jwt_decode_with_hs256(self):
        """Test JWT decode with HS256 algorithm"""
        import jwt
        
        # Create a test token
        secret = "test-secret-key"
        payload = {"user_id": "123", "sub": "123"}
        token = jwt.encode(payload, secret, algorithm="HS256")
        
        # Decode the token
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        
        assert decoded["user_id"] == "123"
        assert decoded["sub"] == "123"
    
    def test_jwt_decode_expired_token(self):
        """Test JWT decode with expired token raises ExpiredSignatureError"""
        import jwt
        from datetime import datetime, timedelta
        
        secret = "test-secret-key"
        payload = {
            "user_id": "123",
            "exp": datetime.utcnow() - timedelta(seconds=1)  # Expired
        }
        token = jwt.encode(payload, secret, algorithm="HS256")
        
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, secret, algorithms=["HS256"])
    
    def test_jwt_decode_invalid_token(self):
        """Test JWT decode with invalid token raises InvalidTokenError"""
        import jwt
        
        secret = "test-secret-key"
        invalid_token = "invalid.token.here"
        
        with pytest.raises(jwt.InvalidTokenError):
            jwt.decode(invalid_token, secret, algorithms=["HS256"])
    
    def test_jwt_decode_wrong_secret(self):
        """Test JWT decode with wrong secret raises InvalidTokenError"""
        import jwt
        
        secret = "test-secret-key"
        payload = {"user_id": "123"}
        token = jwt.encode(payload, secret, algorithm="HS256")
        
        wrong_secret = "wrong-secret"
        
        with pytest.raises(jwt.InvalidTokenError):
            jwt.decode(token, wrong_secret, algorithms=["HS256"])
    
    def test_auth_middleware_jwt_authentication(self):
        """Test AuthMiddleware JWT authentication functionality"""
        import jwt
        from app.middleware.auth import AuthMiddleware
        from unittest.mock import Mock, AsyncMock
        
        # Create test token
        secret = "test-secret"
        payload = {
            "sub": "user123",
            "user_id": "user123",
            "username": "testuser",
            "roles": ["user"]
        }
        token = jwt.encode(payload, secret, algorithm="HS256")
        
        # Mock settings
        settings = Mock()
        settings.jwt_secret_key = secret
        settings.jwt_algorithm = "HS256"
        settings.api_key_enabled = True
        settings.api_key_header = "X-API-Key"
        
        # Mock request
        request = Mock()
        credentials = Mock()
        credentials.credentials = token
        request.headers = {}
        
        middleware = AuthMiddleware()
        middleware.settings = settings
        
        # Mock security
        middleware.security = AsyncMock(return_value=credentials)
        
        # Test authentication
        import asyncio
        result = asyncio.run(middleware.authenticate_jwt(request))
        
        assert result is not None
        assert result.user_id == "user123"
    
    def test_pyjwt_package_version(self):
        """Test that PyJWT package is the correct version"""
        try:
            import jwt
            # PyJWT should have __version__ attribute
            if hasattr(jwt, '__version__'):
                version = jwt.__version__
                # Should be 2.x.x
                assert version.startswith('2.')
        except AttributeError:
            # If __version__ doesn't exist, that's okay
            # Just verify jwt module works
            assert jwt is not None

