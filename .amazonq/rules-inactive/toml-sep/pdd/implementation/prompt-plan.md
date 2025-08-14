# Implementation Prompt Plan

## Checklist
- [ ] Prompt 1: Add TOML environment variable support to configprovider
- [ ] Prompt 2: Implement core TOML parsing functions in configloader
- [ ] Prompt 3: Add TOML section parsing with dot notation support
- [ ] Prompt 4: Implement data type conversion for backward compatibility
- [ ] Prompt 5: Integrate TOML support into Session.full_config property
- [ ] Prompt 6: Add comprehensive error handling and logging
- [ ] Prompt 7: Create unit tests for TOML parsing functions
- [ ] Prompt 8: Create integration tests for Session TOML support
- [ ] Prompt 9: Add Python 3.9-3.10 conditional import support
- [ ] Prompt 10: Wire everything together and validate end-to-end functionality

## Prompts

### Prompt 1: Add TOML environment variable support to configprovider
Add support for the `AWS_CONFIG_FILE_TOML` environment variable to the botocore configuration system. Modify the `BOTOCORE_DEFAUT_SESSION_VARIABLES` dictionary in `botocore/configprovider.py` to include the new `config_file_toml` variable that maps to the `AWS_CONFIG_FILE_TOML` environment variable.

The implementation should follow the existing pattern used for other configuration variables like `config_file`. Ensure the variable is properly integrated into the session variable system so it can be accessed via `session.get_config_variable('config_file_toml')`.

Create a simple test to verify the environment variable is properly registered and accessible through the session configuration system.

### Prompt 2: Implement core TOML parsing functions in configloader
Create the foundational TOML parsing functions in `botocore/configloader.py`. Implement three core functions:

1. `raw_toml_parse(config_filename)` - Parse TOML file and return raw contents with native types
2. `load_toml_config(config_filename)` - Main entry point matching `load_config()` signature  
3. `_convert_toml_types(config_dict)` - Convert TOML types for backward compatibility

Focus on Python 3.11+ support using the built-in `tomllib` module. Implement proper error handling that raises `ConfigNotFound` for missing files and `ConfigParseError` for syntax errors. The functions should handle file path expansion and validation consistent with existing INI parsing.

Include basic unit tests to verify TOML parsing works correctly with simple configuration files containing strings, booleans, and integers.

### Prompt 3: Add TOML section parsing with dot notation support
Implement `build_toml_profile_map(parsed_toml_config)` function in `botocore/configloader.py` to handle TOML's dot notation syntax for sections. The function should convert TOML table structures like `[profile.name]`, `[sso-session.name]`, and `[services.name]` into the standard configuration structure expected by botocore.

The output should match the structure produced by `build_profile_map()` for INI files:
- `profiles` dictionary containing profile configurations
- `sso_sessions` dictionary for SSO session configurations  
- `services` dictionary for service-specific configurations
- Other top-level sections preserved as-is

Create tests to verify the section parsing correctly handles various TOML table structures and produces the expected output format.

### Prompt 4: Implement data type conversion for backward compatibility
Enhance the `_convert_toml_types()` function to handle the specific backward compatibility requirement for `sigv4a_signing_region_set`. This property should convert TOML arrays like `["us-east-1", "us-west-2"]` to comma-separated strings like `"us-east-1,us-west-2"` to maintain compatibility with existing code.

Preserve native TOML types (boolean, integer) for other properties as they are already compatible with existing type conversion functions like `ensure_boolean()` and `int()`.

Add comprehensive tests to verify:
- Array properties are converted to comma-separated strings
- Boolean properties remain as native Python booleans
- Integer properties remain as native Python integers
- String properties remain unchanged
- Nested dictionaries are processed recursively

### Prompt 5: Integrate TOML support into Session.full_config property
Modify the `full_config` property in `botocore/session.py` to check for TOML configuration files before falling back to INI files. The implementation should:

1. Check for `AWS_CONFIG_FILE_TOML` environment variable first
2. If not set, check for default `~/.aws/config.toml` file
3. Fall back to existing INI logic if no TOML file found
4. Log warnings when both TOML and INI environment variables are set
5. Maintain the same caching behavior using `self._config`
6. Preserve existing credentials file merging logic

The integration should be seamless - existing code should continue working unchanged while new TOML files are automatically detected and used when present.

Create integration tests to verify the file discovery logic works correctly in various scenarios.

### Prompt 6: Add comprehensive error handling and logging
Implement robust error handling throughout the TOML parsing pipeline. Ensure all error conditions fail fast with clear, actionable error messages:

1. TOML syntax errors should raise `ConfigParseError` with file path and specific error details
2. Missing files should raise `ConfigNotFound` when `AWS_CONFIG_FILE_TOML` is explicitly set
3. Missing TOML library should raise `ConfigParseError` with helpful message about Python version requirements
4. Add appropriate logging for file discovery and parsing operations
5. Ensure error messages are consistent with existing INI parsing error formats

Add comprehensive error handling tests to verify all error conditions are properly caught and reported with useful messages.

### Prompt 7: Create unit tests for TOML parsing functions
Develop a comprehensive unit test suite for all TOML parsing functions in `tests/unit/test_configloader.py`. The tests should cover:

1. Basic TOML parsing with various data types (string, boolean, integer, array)
2. Section syntax handling with dot notation (`[profile.name]`, `[sso-session.name]`, `[services.name]`)
3. Data type conversion for backward compatibility
4. Error conditions (syntax errors, missing files, missing library)
5. File path expansion and validation
6. Edge cases like empty files, malformed sections, and special characters

Follow the existing test patterns in the configloader test file. Ensure tests are isolated and don't depend on external files or environment state.

### Prompt 8: Create integration tests for Session TOML support
Create integration tests in `tests/integration/` to verify end-to-end TOML configuration loading through the Session class. The tests should cover:

1. TOML file discovery with and without environment variables
2. Precedence logic (TOML over INI when both exist)
3. Credentials file merging with TOML configuration
4. Session behavior with various TOML configuration scenarios
5. Client creation using TOML-loaded configuration
6. Warning logging when both environment variables are set

Use temporary files and controlled environments to ensure tests are reliable and don't interfere with each other.

### Prompt 9: Add Python 3.9-3.10 conditional import support
Extend the TOML parsing implementation to support Python 3.9 and 3.10 by adding conditional imports for the `tomli` library. Modify `raw_toml_parse()` to:

1. Check Python version and use `tomllib` for 3.11+
2. Fall back to `tomli` for Python 3.9-3.10
3. Raise clear error messages when `tomli` is not available
4. Maintain identical functionality across all supported Python versions

Add tests to verify the conditional import logic works correctly and provides appropriate error messages when dependencies are missing.

### Prompt 10: Wire everything together and validate end-to-end functionality
Perform final integration and validation of the complete TOML configuration support implementation. This includes:

1. Verify all components work together seamlessly
2. Run comprehensive tests across all supported Python versions
3. Validate backward compatibility with existing INI configurations
4. Test mixed environments with both TOML and INI files
5. Verify performance impact is minimal
6. Ensure all error conditions are properly handled
7. Validate logging and warning messages are appropriate

Create end-to-end test scenarios that demonstrate the feature working as specified in the SEP. Document any remaining issues or limitations that need to be addressed.
