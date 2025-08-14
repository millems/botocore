# Refactor Session Config Loading - Implementation Plan

## Test Strategy

### Test Scenarios

#### 1. Helper Method Creation
- **Input**: Session instance with various config file states
- **Expected**: `_load_config_with_fallback()` returns same structure as current implementation
- **Test Cases**:
  - TOML file exists and is valid
  - INI file exists and is valid  
  - Both files exist (TOML should take priority)
  - Neither file exists (should return default)
  - TOML file invalid, INI file valid (should fallback)

#### 2. TOML Priority Behavior
- **Input**: Both TOML and INI files present
- **Expected**: TOML config loaded, INI ignored
- **Test Cases**:
  - Different values in TOML vs INI files
  - Verify TOML values are returned

#### 3. INI Fallback Behavior  
- **Input**: TOML file missing/invalid, INI file present
- **Expected**: INI config loaded successfully
- **Test Cases**:
  - TOML file doesn't exist
  - TOML file has parse errors
  - INI file loads correctly

#### 4. Default Fallback Behavior
- **Input**: Neither TOML nor INI files exist
- **Expected**: Returns `{'profiles': {}}`
- **Test Cases**:
  - No config files present
  - Both files have ConfigNotFound errors

#### 5. Error Handling Preservation
- **Input**: Various error conditions
- **Expected**: Same exceptions as original implementation
- **Test Cases**:
  - ConfigNotFound exceptions propagated correctly
  - Other exceptions (parse errors) handled same way

#### 6. Behavioral Compatibility
- **Input**: All existing test scenarios
- **Expected**: Identical behavior to original implementation
- **Test Cases**:
  - Run all existing full_config tests
  - Verify no behavioral changes

## Implementation Plan

### Phase 1: Create Helper Method
1. **Add `_load_config_with_fallback()` method** to Session class
2. **Implement clean fallback logic** using iteration pattern
3. **Preserve exact error handling** from original implementation
4. **Return same data structures** as current code

### Phase 2: Update full_config Property
1. **Replace duplicated try/catch blocks** with helper method call
2. **Keep warning logic unchanged** in full_config property
3. **Keep credentials merging logic unchanged** in full_config property
4. **Maintain same caching behavior** (self._config)

### Phase 3: Validation and Testing
1. **Run existing test suite** to ensure no regressions
2. **Add specific tests** for helper method behavior
3. **Verify performance** is not impacted
4. **Check code coverage** is maintained

## Implementation Structure

### Helper Method Design
```python
def _load_config_with_fallback(self):
    """Load configuration with TOML->INI->default fallback.
    
    Returns:
        dict: Configuration dictionary with same structure as current implementation
    """
    # Try TOML first, then INI, then default
    loaders = [
        (self.get_config_variable('config_file_toml'), botocore.configloader.load_toml_config),
        (self.get_config_variable('config_file'), botocore.configloader.load_config)
    ]
    
    for config_file, loader_func in loaders:
        try:
            return loader_func(config_file)
        except ConfigNotFound:
            continue
    
    return {'profiles': {}}
```

### Updated full_config Property
```python
@property
def full_config(self):
    if self._config is None:
        # Warning logic (unchanged)
        toml_file = self.get_config_variable('config_file_toml')
        ini_file = self.get_config_variable('config_file')
        
        toml_explicitly_set = (
            os.environ.get('AWS_CONFIG_FILE_TOML') or
            self._session_instance_vars.get('config_file_toml') is not None
        )
        if toml_explicitly_set and ini_file:
            logger.warning(
                "Both AWS_CONFIG_FILE_TOML and INI environment variables are set. "
                "Using TOML configuration."
            )
        
        # Use helper method for config loading
        self._config = self._load_config_with_fallback()
        
        # Credentials merging logic (unchanged)
        # ... existing credentials merging code ...
    
    return self._config
```

## Risk Mitigation

### Behavioral Changes Risk
- **Risk**: Refactoring changes existing behavior
- **Mitigation**: Comprehensive test suite validation, exact logic preservation

### Performance Impact Risk
- **Risk**: Helper method adds overhead
- **Mitigation**: Minimal method call overhead, same logic complexity

### Error Handling Risk
- **Risk**: Exception handling changes
- **Mitigation**: Preserve exact same try/catch behavior in helper method

## Success Criteria

1. **Code Quality**: Elimination of duplicated try/catch blocks
2. **Maintainability**: Cleaner, more readable fallback logic
3. **Compatibility**: All existing tests pass without changes
4. **Functionality**: Identical behavior to original implementation
5. **Performance**: No measurable performance impact
