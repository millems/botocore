# TOML Environment Variable Support - Implementation Plan

## Test Strategy

### Test Scenarios
1. **Environment Variable Registration**
   - Given `AWS_CONFIG_FILE_TOML` environment variable is set to a file path
   - When `session.get_config_variable('config_file_toml')` is called
   - Then it returns the environment variable value

2. **Default Behavior**
   - Given no `AWS_CONFIG_FILE_TOML` environment variable is set
   - When `session.get_config_variable('config_file_toml')` is called
   - Then it returns None (default value)

3. **Session Integration**
   - Given the new variable is added to `BOTOCORE_DEFAUT_SESSION_VARIABLES`
   - When the session configuration system initializes
   - Then the variable is available through standard session methods

### Test Implementation
- Add test cases to `tests/unit/test_session.py`
- Follow existing patterns for environment variable testing
- Use session's `update_session_config_mapping` method for test setup

## Implementation Approach

### 1. Code Changes
**File**: `botocore/configprovider.py`
**Location**: `BOTOCORE_DEFAUT_SESSION_VARIABLES` dictionary

**Pattern to follow** (based on existing `config_file` entry):
```python
'config_file': (None, 'AWS_CONFIG_FILE', '~/.aws/config', None),
```

**New entry to add**:
```python
'config_file_toml': (None, 'AWS_CONFIG_FILE_TOML', None, None),
```

**Tuple format**: `(config_file_key, env_var_name, default_value, conversion_func)`
- `config_file_key`: None (not stored in config file)
- `env_var_name`: 'AWS_CONFIG_FILE_TOML'
- `default_value`: None (no default file location)
- `conversion_func`: None (no type conversion needed)

### 2. Implementation Steps
1. Locate the `BOTOCORE_DEFAUT_SESSION_VARIABLES` dictionary
2. Add the new `config_file_toml` entry following the existing pattern
3. Place it near the existing `config_file` entry for logical grouping

### 3. Testing Steps
1. Write unit tests in `tests/unit/test_session.py`
2. Test environment variable behavior
3. Test default value behavior
4. Test session integration
5. Run existing tests to ensure no regressions

## Acceptance Criteria Mapping

1. **Environment Variable Registration** → Test with env var set
2. **Default Behavior** → Test with no env var set  
3. **Integration with Session System** → Test session.get_config_variable() access

## Risk Assessment
- **Low Risk**: Simple dictionary addition following established pattern
- **No Breaking Changes**: Only adding new functionality
- **Backward Compatible**: Existing code unaffected
