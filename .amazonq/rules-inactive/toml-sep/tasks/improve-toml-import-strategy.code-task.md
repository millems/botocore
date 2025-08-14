# Task: Improve TOML Import Strategy with Module-Level Import and Graceful Fallback

## Description
Replace the current inline import strategy for TOML libraries with a cleaner module-level import approach that provides better error handling and performance. This will eliminate repeated import logic and provide clearer error messages when TOML support is unavailable.

## Background
The current implementation performs TOML library imports inline within the `raw_toml_parse()` function, checking Python version and handling ImportError each time the function is called. This creates unnecessary overhead and makes the code harder to maintain. A module-level import with graceful fallback would be cleaner and more efficient.

## Technical Requirements
1. Move TOML import logic to module level in `botocore/configloader.py`
2. Create a `TOML_AVAILABLE` flag to track library availability
3. Provide clear error messages when TOML support is unavailable
4. Maintain backward compatibility with Python 3.9-3.10 using tomli
5. Support Python 3.11+ built-in tomllib
6. Ensure error messages are helpful for users missing dependencies
7. Avoid import errors during module loading when tomli is unavailable

## Dependencies
- Python 3.11+ built-in `tomllib` module
- Optional `tomli` package for Python 3.9-3.10
- Existing `ConfigParseError` exception class
- Current TOML parsing functionality

## Implementation Approach
1. Add module-level import block with version checking and exception handling
2. Set `TOML_AVAILABLE` boolean flag based on import success
3. Update `raw_toml_parse()` to check the flag before attempting to parse
4. Provide clear error messages that guide users to install missing dependencies
5. Ensure the module can still be imported even when TOML libraries are unavailable

## Acceptance Criteria

1. **Module-Level Import Success**
   - Given Python 3.11+ environment
   - When the configloader module is imported
   - Then `tomllib` is imported and `TOML_AVAILABLE` is True

2. **Fallback Import Success**
   - Given Python 3.9-3.10 environment with tomli installed
   - When the configloader module is imported
   - Then `tomli` is imported as `tomllib` and `TOML_AVAILABLE` is True

3. **Graceful Import Failure**
   - Given Python 3.9-3.10 environment without tomli
   - When the configloader module is imported
   - Then module loads successfully with `TOML_AVAILABLE` as False

4. **Clear Error Messages**
   - Given TOML parsing is attempted when libraries are unavailable
   - When `raw_toml_parse()` is called
   - Then a clear ConfigParseError is raised with installation instructions

5. **Performance Improvement**
   - Given multiple TOML parsing operations
   - When using the new import strategy
   - Then import overhead is eliminated after the first module load

6. **Backward Compatibility**
   - Given existing TOML parsing functionality
   - When using the new import strategy
   - Then all existing behavior is preserved

## Metadata
- **Complexity**: Low
- **Labels**: Performance, Code Quality, Import Strategy, TOML
- **Required Skills**: Python imports, Module design, Error handling
- **Suggested Reviewers**: Someone familiar with Python packaging and imports
