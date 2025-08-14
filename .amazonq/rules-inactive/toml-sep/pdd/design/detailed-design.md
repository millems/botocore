# TOML Configuration Support - Detailed Design

## Overview

This document provides the detailed technical design for implementing TOML configuration file support in botocore, as specified in the SEP. The implementation adds native data type support (boolean, integer, array) while maintaining full backward compatibility with existing INI configuration files.

## Requirements Summary

From the requirements clarification phase:

1. **Separate TOML parsing** - No reuse of INI parsing components
2. **Backward compatibility** - Match existing data types when returning from session methods
3. **Python 3.11+ focus** - Initial implementation for Python 3.11+, later support for 3.9-3.10
4. **Strict error handling** - Fail fast in all error scenarios
5. **Array conversion** - Config provider handles array conversion to match INI format
6. **Direct integration** - Integrate into `full_config` property with logging warnings

## Architecture

### High-Level Design

```
Session.full_config
├── Check for TOML file (config_file_toml)
│   ├── If exists: load_toml_config() → return TOML config
│   └── If not exists: fallback to INI loading
├── Log warnings for environment variable conflicts
└── Maintain same caching behavior (self._config)
```

### Component Integration

```
botocore/
├── session.py
│   └── Session.full_config (modified)
├── configloader.py
│   ├── load_toml_config() (new)
│   ├── raw_toml_parse() (new)
│   └── build_toml_profile_map() (new)
└── configprovider.py
    └── BOTOCORE_DEFAUT_SESSION_VARIABLES (modified)
```

## Detailed Design

### 1. Environment Variable Support

**File**: `botocore/configprovider.py`

Add `config_file_toml` to the session variables:

```python
BOTOCORE_DEFAUT_SESSION_VARIABLES = {
    # ... existing variables ...
    'config_file_toml': (None, 'AWS_CONFIG_FILE_TOML', None, None),
}
```

### 2. Session Integration

**File**: `botocore/session.py`

Modify the `full_config` property:

```python
@property
def full_config(self):
    """Return the parsed config file.
    
    The ``get_config`` method returns the config associated with the
    specified profile.  This property returns the contents of the
    **entire** config file.
    
    :rtype: dict
    """
    if self._config is None:
        # Check for TOML configuration first
        toml_file = self.get_config_variable('config_file_toml')
        ini_file = self.get_config_variable('config_file')
        
        # Log warning if both environment variables are set
        if toml_file and ini_file:
            logger.warning(
                "Both AWS_CONFIG_FILE_TOML and INI environment variables are set. "
                "Using TOML configuration."
            )
        
        try:
            if toml_file:
                self._config = botocore.configloader.load_toml_config(toml_file)
            else:
                # Check for default TOML file location
                default_toml = os.path.expanduser('~/.aws/config.toml')
                if os.path.exists(default_toml):
                    self._config = botocore.configloader.load_toml_config(default_toml)
                else:
                    # Fallback to existing INI logic
                    config_file = self.get_config_variable('config_file')
                    self._config = botocore.configloader.load_config(config_file)
        except ConfigNotFound:
            self._config = {'profiles': {}}
        
        # Credentials file merging logic (unchanged)
        try:
            cred_file = self.get_config_variable('credentials_file')
            cred_profiles = botocore.configloader.raw_config_parse(cred_file)
            for profile in cred_profiles:
                cred_vars = cred_profiles[profile]
                if profile not in self._config['profiles']:
                    self._config['profiles'][profile] = cred_vars
                else:
                    self._config['profiles'][profile].update(cred_vars)
        except ConfigNotFound:
            pass
    
    return self._config
```

### 3. TOML Parsing Implementation

**File**: `botocore/configloader.py`

#### 3.1 Main Entry Point

```python
def load_toml_config(config_filename):
    """Parse a TOML config with profiles.
    
    This will parse a TOML config file and map top level profiles
    into a top level "profiles" key, similar to load_config() for INI files.
    
    :param config_filename: The path to the TOML config file
    :returns: A dict with the same structure as load_config()
    :raises: ConfigNotFound, ConfigParseError
    """
    parsed = raw_toml_parse(config_filename)
    return build_toml_profile_map(parsed)
```

#### 3.2 TOML File Parsing

```python
def raw_toml_parse(config_filename):
    """Parse a TOML config file and return the raw parsed contents.
    
    :param config_filename: The path to the TOML config file
    :returns: A dict with the parsed TOML contents
    :raises: ConfigNotFound, ConfigParseError
    """
    import sys
    
    # Python 3.11+ has built-in tomllib
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        try:
            import tomli as tomllib
        except ImportError:
            raise ConfigParseError(
                path=config_filename,
                error="TOML support requires Python 3.11+ or tomli package"
            )
    
    if config_filename is None:
        raise ConfigNotFound(path="None")
    
    path = os.path.expandvars(config_filename)
    path = os.path.expanduser(path)
    
    if not os.path.isfile(path):
        raise ConfigNotFound(path=_unicode_path(path))
    
    try:
        with open(path, 'rb') as f:
            config = tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError) as e:
        raise ConfigParseError(path=_unicode_path(path), error=e)
    
    return config
```

#### 3.3 TOML Profile Map Building

```python
def build_toml_profile_map(parsed_toml_config):
    """Convert parsed TOML config into the standard profile map structure.
    
    Handles TOML dot notation syntax:
    - [profile.name] → profiles['name']
    - [sso-session.name] → sso_sessions['name'] 
    - [services.name] → services['name']
    
    :param parsed_toml_config: Raw parsed TOML config dict
    :returns: Structured config dict matching INI format
    """
    profiles = {}
    sso_sessions = {}
    services = {}
    final_config = {}
    
    for key, values in parsed_toml_config.items():
        if key == 'profile':
            # Handle [profile] table with sub-tables
            for profile_name, profile_config in values.items():
                profiles[profile_name] = _convert_toml_types(profile_config)
        elif key == 'sso-session':
            # Handle [sso-session] table with sub-tables
            for session_name, session_config in values.items():
                sso_sessions[session_name] = _convert_toml_types(session_config)
        elif key == 'services':
            # Handle [services] table with sub-tables
            for service_name, service_config in values.items():
                services[service_name] = _convert_toml_types(service_config)
        else:
            # Top-level sections (non-profile)
            final_config[key] = _convert_toml_types(values)
    
    final_config['profiles'] = profiles
    final_config['sso_sessions'] = sso_sessions
    final_config['services'] = services
    
    return final_config
```

#### 3.4 Data Type Conversion

```python
def _convert_toml_types(config_dict):
    """Convert TOML native types to formats expected by existing code.
    
    Handles backward compatibility by converting:
    - TOML arrays to appropriate format for sigv4a_signing_region_set
    - Preserves native boolean and integer types for other properties
    
    :param config_dict: Dictionary with TOML native types
    :returns: Dictionary with converted types for backward compatibility
    """
    converted = {}
    
    for key, value in config_dict.items():
        if key == 'sigv4a_signing_region_set' and isinstance(value, list):
            # Convert TOML array to comma-separated string for backward compatibility
            converted[key] = ','.join(value)
        else:
            # Preserve native types for boolean, integer, and string values
            converted[key] = value
    
    return converted
```

### 4. Error Handling

All TOML parsing functions implement strict error handling:

- **Syntax errors**: Raise `ConfigParseError` with clear error messages
- **Missing files**: Raise `ConfigNotFound` when `AWS_CONFIG_FILE_TOML` is set
- **Missing library**: Raise `ConfigParseError` for Python < 3.11 without tomli

### 5. Data Type Mapping

| TOML Type | Python Type | Backward Compatibility |
|-----------|-------------|----------------------|
| `true`/`false` | `True`/`False` | Compatible with `ensure_boolean()` |
| `3600` | `3600` (int) | Compatible with `int()` conversion |
| `["us-east-1", "us-west-2"]` | `"us-east-1,us-west-2"` | Converted for `sigv4a_signing_region_set` |
| `"string"` | `"string"` | Direct compatibility |

### 6. File Discovery Logic

1. **Environment variable set**: Use `AWS_CONFIG_FILE_TOML` exclusively
2. **No environment variable**: Check `~/.aws/config.toml`, fallback to INI
3. **Both variables set**: Log warning, use TOML
4. **TOML parsing fails**: Fail fast, no INI fallback

## Testing Strategy

### Unit Tests
- TOML parsing with various data types
- Section syntax handling (dot notation)
- Error conditions (syntax errors, missing files)
- Data type conversion accuracy
- Environment variable precedence

### Integration Tests  
- End-to-end configuration loading
- Credentials file merging with TOML config
- Session behavior with TOML vs INI files
- Client creation with TOML configuration

### Compatibility Tests
- Existing INI files continue working
- Mixed TOML/INI environments
- All existing configuration properties work with TOML

## Implementation Phases

### Phase 1: Core TOML Support (Python 3.11+)
- Add environment variable support
- Implement TOML parsing functions
- Modify Session.full_config property
- Basic error handling and logging

### Phase 2: Data Type Conversion
- Implement backward compatibility layer
- Handle array conversion for sigv4a_signing_region_set
- Ensure all existing code paths work

### Phase 3: Python 3.9-3.10 Support
- Add conditional tomli import
- Handle import errors gracefully
- Maintain same functionality across versions

### Phase 4: Testing and Validation
- Comprehensive test suite
- Performance validation
- Documentation updates

## Risk Mitigation

### Array Data Type Incompatibility
- **Risk**: `sigv4a_signing_region_set` expects comma-separated string
- **Mitigation**: Convert TOML arrays to comma-separated strings in `_convert_toml_types()`

### TOML Section Syntax Incompatibility  
- **Risk**: Dot notation vs space-separated parsing
- **Mitigation**: Separate parsing logic in `build_toml_profile_map()`

### Third-Party Plugin Compatibility
- **Risk**: Plugins may expect specific data types
- **Mitigation**: Maintain existing data types through conversion layer

## Success Criteria

1. **Functional**: All TOML configuration features work as specified in SEP
2. **Compatible**: Existing INI files and code continue working unchanged
3. **Performant**: No significant performance impact on configuration loading
4. **Maintainable**: Clean separation between TOML and INI parsing logic
5. **Testable**: Comprehensive test coverage for all scenarios
