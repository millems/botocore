# Configuration Loading Analysis

## Current Configuration Loading Flow

Based on the code analysis, here's how configuration loading currently works:

### 1. Session.full_config Property
```python
@property
def full_config(self):
    if self._config is None:
        try:
            config_file = self.get_config_variable('config_file')
            self._config = botocore.configloader.load_config(config_file)
        except ConfigNotFound:
            self._config = {'profiles': {}}
        # ... credentials file merging logic
    return self._config
```

### 2. Configuration Loading Chain
1. `load_config(config_filename)` - Main entry point
2. `raw_config_parse(config_filename)` - Parses INI file using `configparser.RawConfigParser`
3. `build_profile_map(parsed_ini_config)` - Converts parsed INI to structured format

### 3. Section Parsing Logic
The `_parse_section(key, values)` function uses `shlex.split(key)` to parse section names:
- `[profile test]` → `["profile", "test"]` → `{"test": values}`
- `[sso-session my-sso]` → `["sso-session", "my-sso"]` → `{"my-sso": values}`
- `[services s3]` → `["services", "s3"]` → `{"s3": values}`

### 4. Output Structure
The final configuration structure is:
```python
{
    'profiles': {
        'default': {...},
        'profile-name': {...}
    },
    'sso_sessions': {
        'session-name': {...}
    },
    'services': {
        'service-name': {...}
    },
    # Other top-level sections
}
```

## TOML Implementation Requirements

Based on the requirements clarification and current architecture:

### 1. Integration Point
- Modify `Session.full_config` property to check for TOML files first
- Use `get_config_variable('config_file_toml')` for TOML file discovery
- Maintain same caching behavior with `self._config`

### 2. TOML Parsing Functions Needed
- `load_toml_config(config_filename)` - Main TOML entry point
- `raw_toml_parse(config_filename)` - Parse TOML with native types
- `build_toml_profile_map(parsed_toml_config)` - Convert to standard structure

### 3. Section Syntax Differences
- **INI**: `[profile test]` → parsed with `shlex.split()`
- **TOML**: `[profile.test]` → requires dot notation parsing
- Need separate parsing logic for TOML sections

### 4. Data Type Handling
- **Boolean**: TOML `true`/`false` → Python `True`/`False`
- **Integer**: TOML `3600` → Python `3600`
- **Array**: TOML `["us-east-1", "us-west-2"]` → Python list
- **String**: TOML `"value"` → Python `"value"`

### 5. Error Handling
- Strict TOML parsing with no INI fallback
- Clear error messages for syntax errors
- Fail fast for missing files when `AWS_CONFIG_FILE_TOML` is set

## Implementation Strategy

1. **Add TOML environment variable** to `BOTOCORE_DEFAUT_SESSION_VARIABLES`
2. **Create TOML parsing functions** in `configloader.py`
3. **Modify Session.full_config** to check TOML first
4. **Implement data type conversion** for backward compatibility
5. **Add logging warnings** for environment variable conflicts
