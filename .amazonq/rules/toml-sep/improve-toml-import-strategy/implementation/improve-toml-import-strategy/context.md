# Improve TOML Import Strategy - Implementation Context

## Task Overview
Replace the current inline import strategy for TOML libraries with a cleaner module-level import approach that provides better error handling and performance. This will eliminate repeated import logic and provide clearer error messages when TOML support is unavailable.

## Project Structure
- **Repository**: botocore (AWS SDK for Python core library)
- **Language**: Python
- **Target File**: `botocore/configloader.py`
- **Testing Framework**: pytest (detected from existing test structure)

## Requirements Summary
Based on the code task description:

### Technical Requirements
1. Move TOML import logic to module level in `botocore/configloader.py`
2. Create a `TOML_AVAILABLE` flag to track library availability
3. Provide clear error messages when TOML support is unavailable
4. Maintain backward compatibility with Python 3.9-3.10 using tomli
5. Support Python 3.11+ built-in tomllib
6. Ensure error messages are helpful for users missing dependencies
7. Avoid import errors during module loading when tomli is unavailable

### Acceptance Criteria
- Module-level import success for Python 3.11+ (tomllib)
- Fallback import success for Python 3.9-3.10 with tomli
- Graceful import failure when tomli unavailable
- Clear error messages with installation instructions
- Performance improvement through eliminated import overhead
- Backward compatibility preservation

## Implementation Paths
- **Primary File**: `botocore/configloader.py` - Module-level imports and raw_toml_parse function
- **Import Strategy**: Module-level import block with version checking
- **Error Handling**: Clear ConfigParseError messages for missing dependencies

## Dependencies
- Python 3.11+ built-in `tomllib` module
- Optional `tomli` package for Python 3.9-3.10
- Existing `ConfigParseError` exception class
- Current TOML parsing functionality

## Existing Documentation
- **Project Structure**: Python project with pytest testing framework
- **Test Organization**: tests/unit/ and tests/integration/ directories
- **No DEVELOPMENT.md found**: Using generic Python best practices

## Current Implementation Analysis
The current implementation in `botocore/configloader.py` performs inline imports within `raw_toml_parse()`:

**Current Structure (lines 297-307):**
```python
# Python 3.11+ has built-in tomllib
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        raise botocore.exceptions.ConfigParseError(
            path=config_filename,
            error="TOML support requires Python 3.11+ or tomli package"
        )
```

**Current Issues:**
1. Import logic executed on every function call
2. Version checking repeated unnecessarily  
3. ImportError handling duplicated
4. Performance overhead from repeated imports
5. Less clear error messages

## Existing Patterns
Found similar pattern in `botocore/compat.py` with `MD5_AVAILABLE`:

```python
try:
    hashlib.md5(usedforsecurity=False)
    MD5_AVAILABLE = True
except (AttributeError, ValueError):
    MD5_AVAILABLE = False

def get_md5(*args, **kwargs):
    if MD5_AVAILABLE:
        return hashlib.md5(*args, **kwargs)
    else:
        raise MD5UnavailableError()
```

## Refactoring Strategy
- Follow the MD5_AVAILABLE pattern for consistency
- Move import logic to module level with graceful fallback
- Create TOML_AVAILABLE flag for availability checking
- Update raw_toml_parse() to check flag before parsing
- Provide helpful error messages for missing dependencies
- Ensure module can be imported even when TOML libraries unavailable

**Proposed Module-Level Import:**
```python
# TOML library imports with graceful fallback
try:
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        import tomli as tomllib
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False
    tomllib = None
```

**Proposed Updated Function:**
```python
def raw_toml_parse(config_filename):
    if not TOML_AVAILABLE:
        raise botocore.exceptions.ConfigParseError(
            path=config_filename,
            error="TOML support requires Python 3.11+ or tomli package. "
                  "Install with: pip install tomli"
        )
    # ... rest of function unchanged
```

## Key Challenge
Ensure the module can be imported successfully even when tomli is not available, while providing clear guidance to users when TOML functionality is needed but unavailable.
