# Core TOML Parsing Functions - Implementation Plan

## Test Strategy

### Test Scenarios
1. **TOML File Parsing**
   - Given a valid TOML configuration file
   - When `raw_toml_parse(filename)` is called
   - Then it returns a dictionary with native TOML data types preserved

2. **Error Handling for Missing Files**
   - Given a non-existent TOML file path
   - When `raw_toml_parse(filename)` is called
   - Then it raises `ConfigNotFound` exception

3. **Error Handling for Syntax Errors**
   - Given a TOML file with syntax errors
   - When `raw_toml_parse(filename)` is called
   - Then it raises `ConfigParseError` exception with file path and error details

4. **Main Entry Point Function**
   - Given a TOML configuration file
   - When `load_toml_config(filename)` is called
   - Then it returns structured configuration matching `load_config()` output format

5. **Data Type Preservation**
   - Given a TOML file with boolean, integer, and string values
   - When parsed through TOML functions
   - Then native Python types are preserved (True/False, int, str)

### Test Implementation
- Add test cases to `tests/unit/test_configloader.py`
- Create temporary TOML test files for parsing
- Test error conditions with invalid files
- Verify data type preservation

## Implementation Approach

### 1. Functions to Implement

**File**: `botocore/configloader.py`

#### `raw_toml_parse(config_filename)`
- Parse TOML file using Python 3.11+ `tomllib`
- Handle file path expansion (expandvars, expanduser)
- Raise `ConfigNotFound` for missing files
- Raise `ConfigParseError` for syntax errors
- Return raw parsed dictionary

#### `load_toml_config(config_filename)`
- Main entry point matching `load_config()` signature
- Call `raw_toml_parse()` then `build_toml_profile_map()`
- Return structured configuration

#### `build_toml_profile_map(parsed_toml_config)`
- Convert TOML structure to match INI profile format
- Handle TOML dot notation: `[profile.name]` → `profiles['name']`
- Handle `[sso-session.name]` and `[services.name]` sections
- Apply type conversion for backward compatibility

#### `_convert_toml_types(config_dict)`
- Convert TOML native types for backward compatibility
- Preserve boolean, integer, string types
- Handle any special conversions needed

### 2. Implementation Pattern
Follow existing patterns from `raw_config_parse()`:
- File path handling
- Error handling with try/catch
- Return dictionary structure

### 3. TOML Structure Mapping
```python
# TOML input:
[profile.dev]
region = "us-west-2"
output = "json"
use_fips = true
timeout = 30

# Should map to:
{
    "profiles": {
        "dev": {
            "region": "us-west-2",
            "output": "json", 
            "use_fips": True,
            "timeout": 30
        }
    }
}
```

## Acceptance Criteria Mapping

1. **TOML File Parsing** → Test with valid TOML file
2. **Error Handling for Missing Files** → Test with non-existent file
3. **Error Handling for Syntax Errors** → Test with malformed TOML
4. **Main Entry Point Function** → Test `load_toml_config()` output structure
5. **Data Type Preservation** → Test boolean, integer, string preservation

## Risk Assessment
- **Medium Risk**: New parsing logic separate from INI
- **Compatibility**: Must maintain same output structure as INI parsing
- **Error Handling**: Must use existing exception classes consistently
