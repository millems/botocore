# ABOUTME: Test TOML import strategy with module-level imports and graceful fallback
# ABOUTME: Validates import behavior, availability flags, and error handling for TOML libraries
import tempfile
from unittest import mock

import pytest
import botocore.exceptions


class TestTOMLImportStrategy:
    def test_toml_available_flag_exists(self):
        """Test that TOML_AVAILABLE flag is defined in configloader module."""
        import botocore.configloader
        assert hasattr(botocore.configloader, 'TOML_AVAILABLE')
        assert isinstance(botocore.configloader.TOML_AVAILABLE, bool)

    def test_raw_toml_parse_unavailable_error(self):
        """Test clear error when TOML unavailable."""
        import botocore.configloader
        
        with mock.patch.object(botocore.configloader, 'TOML_AVAILABLE', False):
            with pytest.raises(botocore.exceptions.ConfigParseError) as exc_info:
                botocore.configloader.raw_toml_parse('test.toml')
            
            # Check the error details in kwargs
            error_msg = exc_info.value.kwargs['error']
            assert 'TOML support requires' in error_msg
            assert 'pip install tomli' in error_msg

    def test_existing_toml_functionality_preserved(self):
        """Test that existing TOML parsing functionality is preserved."""
        import botocore.configloader
        
        # Skip if TOML not available
        if not botocore.configloader.TOML_AVAILABLE:
            pytest.skip("TOML not available")
        
        toml_content = '''
[profile.test]
region = "us-east-1"
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(toml_content)
            f.flush()
            
            result = botocore.configloader.raw_toml_parse(f.name)
            assert 'profile' in result
            assert 'test' in result['profile']
            assert result['profile']['test']['region'] == 'us-east-1'

    def test_performance_improvement_no_inline_imports(self):
        """Test that raw_toml_parse no longer has inline imports."""
        import inspect
        import botocore.configloader
        
        # Get the source code of raw_toml_parse
        source = inspect.getsource(botocore.configloader.raw_toml_parse)
        
        # Should not contain inline import statements
        assert 'import tomllib' not in source
        assert 'import tomli' not in source
        
        # Should check TOML_AVAILABLE flag
        assert 'TOML_AVAILABLE' in source
