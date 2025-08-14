# Task: Implement Core TOML Parsing Functions in ConfigLoader

## Description
Create the foundational TOML parsing functions in `botocore/configloader.py` to handle TOML configuration files with native data type support. This establishes the core parsing infrastructure needed for TOML configuration support.

## Background
The existing configuration system uses INI files parsed through `configparser`. TOML support requires separate parsing functions that preserve native data types (boolean, integer, array) while maintaining compatibility with the existing configuration structure.

## Technical Requirements
1. Implement `raw_toml_parse(config_filename)` function to parse TOML files with native types
2. Implement `load_toml_config(config_filename)` as main entry point matching `load_config()` signature
3. Implement `_convert_toml_types(config_dict)` for backward compatibility conversion
4. Use Python 3.11+ built-in `tomllib` module
5. Handle file path expansion and validation consistent with existing INI parsing
6. Implement proper error handling with `ConfigNotFound` and `ConfigParseError`

## Dependencies
- Python 3.11+ with built-in `tomllib` module
- Existing `botocore/configloader.py` file
- `ConfigNotFound` and `ConfigParseError` exception classes
- File path handling utilities

## Implementation Approach
1. Add TOML parsing functions to configloader.py
2. Use tomllib for TOML file parsing
3. Implement error handling consistent with existing INI parsing
4. Create basic type conversion function for compatibility
5. Follow existing code patterns and naming conventions

## Acceptance Criteria

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

## Metadata
- **Complexity**: Medium
- **Labels**: TOML, Parsing, Configuration, Data Types
- **Required Skills**: Python, TOML format, File I/O, Error handling
