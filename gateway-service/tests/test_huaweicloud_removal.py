"""
Unit tests to verify Huawei Cloud adapter has been removed
"""

import pytest
from pathlib import Path


class TestHuaweiCloudRemoval:
    """Test cases to verify Huawei Cloud adapter removal"""
    
    def test_huaweicloud_module_not_importable(self):
        """
        Test that Huawei Cloud adapter module cannot be imported
        
        This test verifies that app.adapters.huaweicloud module has been removed
        """
        with pytest.raises(ModuleNotFoundError, match="No module named 'app.adapters.huaweicloud'"):
            from app.adapters.huaweicloud import HuaweiCloudAdapter
    
    def test_huaweicloud_not_in_adapters_init(self):
        """Test that HuaweiCloudAdapter is not exported from adapters __init__"""
        from app.adapters import __all__
        
        assert "HuaweiCloudAdapter" not in __all__
    
    def test_no_huaweicloud_file_exists(self):
        """Test that Huawei Cloud adapter file has been deleted"""
        huaweicloud_file = Path(__file__).parent.parent / "app" / "adapters" / "huaweicloud.py"
        
        assert not huaweicloud_file.exists(), "Huawei Cloud adapter file should not exist"
    
    def test_adapters_init_empty(self):
        """Test that adapters __init__ is empty or has no Huawei Cloud references"""
        import inspect
        from app.adapters import __init__ as adapters_init
        
        source = inspect.getsource(adapters_init)
        assert "HuaweiCloudAdapter" not in source
        assert "from app.adapters.huaweicloud" not in source

