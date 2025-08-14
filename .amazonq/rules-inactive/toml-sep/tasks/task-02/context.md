# Core TOML Parsing Functions - Implementation Context

## Task Overview
Implementing core TOML parsing functions in `botocore/configloader.py` to handle TOML configuration files with native data type support. This establishes the foundational parsing infrastructure for TOML configuration.

## Project Structure
- **Repository**: botocore (AWS SDK for Python core library)
- **Language**: Python
- **Target File**: `botocore/configloader.py`
- **Key Functions to Implement**:
  - `raw_toml_parse(config_filename)`
  - `load_toml_config(config_filename)`
  - `_convert_toml_types(config_dict)`

## Requirements Summary
1. Parse TOML files with native data type preservation
2. Use Python 3.11+ built-in `tomllib` module
3. Implement error handling with existing exception classes
4. Maintain compatibility with existing configuration structure
5. Follow existing code patterns in configloader.py

## Implementation Paths
- **Primary File**: `botocore/configloader.py`
- **Pattern**: Follow existing `load_config()` and `raw_config_parse()` functions
- **Error Handling**: Use `ConfigNotFound` and `ConfigParseError`

## Dependencies
- Python 3.11+ `tomllib` module
- Existing configloader.py infrastructure
- File path handling utilities
- Exception classes already defined

## Acceptance Criteria
1. TOML file parsing with native types
2. Error handling for missing files and syntax errors
3. Main entry point function compatibility
4. Data type preservation (boolean, integer, string)

## Testing Strategy
- Unit tests for TOML parsing functions
- Error condition testing
- Data type preservation validation
- Integration with existing configuration system
