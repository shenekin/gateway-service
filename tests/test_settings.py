"""
Unit tests for settings module
"""

import pytest
from app.settings import Settings, get_settings


def test_settings_default_values():
    """Test settings default values"""
    settings = Settings()
    
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert settings.debug is False


def test_settings_cached():
    """Test settings caching"""
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2


def test_settings_trusted_proxy_list():
    """Test trusted proxy list parsing"""
    settings = Settings(trusted_proxies="127.0.0.1,localhost,192.168.1.1")
    
    proxy_list = settings.trusted_proxy_list
    assert len(proxy_list) == 3
    assert "127.0.0.1" in proxy_list
    assert "localhost" in proxy_list


def test_settings_allowed_origins_list():
    """Test allowed origins list parsing"""
    settings = Settings(allowed_origins="*")
    
    origins_list = settings.allowed_origins_list
    assert origins_list == ["*"]
    
    settings2 = Settings(allowed_origins="http://localhost:3000,http://example.com")
    origins_list2 = settings2.allowed_origins_list
    assert len(origins_list2) == 2

