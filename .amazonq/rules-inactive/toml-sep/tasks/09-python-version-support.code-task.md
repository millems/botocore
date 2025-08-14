# Task: Add Python 3.9-3.10 Conditional Import Support

## Description
Extend the TOML parsing implementation to support Python 3.9 and 3.10 by adding conditional imports for the `tomli` library. This ensures TOML functionality works across all supported Python versions while maintaining identical behavior.

## Background
Python 3.11+ includes built-in `tomllib` module, but earlier versions require the external `tomli` library. The implementation must gracefully handle both scenarios while providing clear error messages when dependencies are missing.

## Technical Requirements
1. Modify `raw_toml_parse()` to check Python version and use appropriate library
2. Use `tomllib` for Python 3.11+
3. Fall back to `tomli` for Python 3.9-3.10
4. Raise clear error messages when `tomli` is not available
5. Maintain identical functionality across all supported Python versions
6. Handle import errors gracefully with helpful messages
7. Ensure no performance impact from version checking

## Dependencies
- Core TOML parsing functions from previous tasks
- Python version detection capabilities
- Optional `tomli` library for Python < 3.11
- Error handling infrastructure

## Implementation Approach
1. Add version detection logic to TOML parsing functions
2. Implement conditional imports with try/except blocks
3. Provide clear error messages for missing dependencies
4. Test functionality across different Python versions
5. Document version requirements and optional dependencies

## Acceptance Criteria

1. **Python 3.11+ Built-in Library Usage**
   - Given Python version 3.11 or higher
   - When TOML parsing functions are called
   - Then built-in `tomllib` module is used for parsing

2. **Python 3.9-3.10 External Library Usage**
   - Given Python version 3.9 or 3.10 with `tomli` installed
   - When TOML parsing functions are called
   - Then external `tomli` library is used for parsing

3. **Missing Library Error Handling**
   - Given Python version 3.9 or 3.10 without `tomli` installed
   - When TOML parsing is attempted
   - Then `ConfigParseError` is raised with helpful message about installing `tomli`

4. **Functionality Consistency**
   - Given the same TOML file parsed on different Python versions
   - When parsing results are compared
   - Then identical output is produced regardless of which library is used

5. **Performance Impact**
   - Given repeated TOML parsing operations
   - When version checking overhead is measured
   - Then performance impact is negligible (version check cached or minimal)

6. **Error Message Quality**
   - Given missing `tomli` library on Python < 3.11
   - When error is raised
   - Then error message includes specific installation instructions and version requirements

## Metadata
- **Complexity**: Low
- **Labels**: Python Versions, Conditional Imports, Dependencies, Compatibility
- **Required Skills**: Python, Version detection, Import handling, Dependency management
