# Improve TOML Import Strategy - Implementation Plan

## Test Strategy

### Test Scenarios

#### 1. Module-Level Import Success (Python 3.11+)
- **Input**: Python 3.11+ environment
- **Expected**: `tomllib` imported, `TOML_AVAILABLE = True`
- **Test Cases**:
  - Import configloader module successfully
  - Verify TOML_AVAILABLE flag is True
  - Verify tomllib is available for use

#### 2. Fallback Import Success (Python 3.9-3.10 with tomli)
- **Input**: Python 3.9-3.10 environment with tomli installed
- **Expected**: `tomli` imported as `tomllib`, `TOML_AVAILABLE = True`
- **Test Cases**:
  - Mock sys.version_info to simulate older Python
  - Mock successful tomli import
  - Verify TOML_AVAILABLE flag is True

#### 3. Graceful Import Failure (Python 3.9-3.10 without tomli)
- **Input**: Python 3.9-3.10 environment without tomli
- **Expected**: Module loads successfully, `TOML_AVAILABLE = False`
- **Test Cases**:
  - Mock sys.version_info to simulate older Python
  - Mock ImportError for tomli
  - Verify module imports without error
  - Verify TOML_AVAILABLE flag is False

#### 4. Clear Error Messages
- **Input**: TOML parsing attempted when libraries unavailable
- **Expected**: Clear ConfigParseError with installation instructions
- **Test Cases**:
  - Call raw_toml_parse() when TOML_AVAILABLE is False
  - Verify ConfigParseError is raised
  - Verify error message includes installation instructions

#### 5. Performance Improvement
- **Input**: Multiple TOML parsing operations
- **Expected**: Import overhead eliminated after first module load
- **Test Cases**:
  - Verify imports happen only once at module level
  - Multiple calls to raw_toml_parse() don't repeat imports

#### 6. Backward Compatibility
- **Input**: Existing TOML parsing functionality
- **Expected**: All existing behavior preserved
- **Test Cases**:
  - Run all existing TOML tests
  - Verify same error types and messages
  - Verify same parsing results

## Implementation Plan

### Phase 1: Add Module-Level Imports
1. **Add TOML import block** at module level in configloader.py
2. **Follow MD5_AVAILABLE pattern** for consistency
3. **Set TOML_AVAILABLE flag** based on import success
4. **Handle ImportError gracefully** to avoid module load failures

### Phase 2: Update raw_toml_parse Function
1. **Add availability check** at function start
2. **Provide clear error message** with installation instructions
3. **Remove inline import logic** from function body
4. **Preserve all other functionality** unchanged

### Phase 3: Testing and Validation
1. **Write unit tests** for import behavior
2. **Test error message clarity** and helpfulness
3. **Validate performance improvement** through profiling
4. **Run existing test suite** to ensure no regressions

## Implementation Structure

### Module-Level Import Block
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

### Updated raw_toml_parse Function
```python
def raw_toml_parse(config_filename):
    """Parse a TOML config file and return the raw parsed contents.
    
    :param config_filename: The path to the TOML config file
    :returns: A dict with the parsed TOML contents, normalized to match INI format
    :raises: ConfigNotFound, ConfigParseError
    """
    if not TOML_AVAILABLE:
        raise botocore.exceptions.ConfigParseError(
            path=config_filename,
            error="TOML support requires Python 3.11+ or tomli package. "
                  "Install with: pip install tomli"
        )
    
    if config_filename is None:
        raise botocore.exceptions.ConfigNotFound(path="None")
    
    # ... rest of function unchanged
```

## Risk Mitigation

### Module Import Failure Risk
- **Risk**: Module fails to import when tomli unavailable
- **Mitigation**: Graceful ImportError handling with TOML_AVAILABLE flag

### Behavioral Changes Risk
- **Risk**: Error messages or timing changes
- **Mitigation**: Preserve exact same error types and comprehensive testing

### Performance Regression Risk
- **Risk**: Module-level imports add startup overhead
- **Mitigation**: Imports only happen once, net performance improvement

## Success Criteria

1. **Performance**: Elimination of repeated import overhead
2. **Usability**: Clear error messages with installation guidance
3. **Reliability**: Module loads successfully even without tomli
4. **Compatibility**: All existing tests pass without changes
5. **Code Quality**: Cleaner, more maintainable import strategy
