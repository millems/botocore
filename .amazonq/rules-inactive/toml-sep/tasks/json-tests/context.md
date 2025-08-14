# JSON Test Runners - Implementation Context

## Task Overview
Create test runners for the test cases described in the SEP for TOML configuration support in botocore. The SEP specifies comprehensive testing strategy including unit tests, integration tests, and compatibility tests.

## Project Structure
- **Repository**: botocore (AWS SDK for Python core library)
- **Language**: Python
- **Testing Framework**: pytest (detected from existing test structure)
- **Target Directory**: Repository root for test implementations

## Requirements Summary
Based on the detailed design document, the testing strategy includes:

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

## Implementation Paths
- **Primary Files**: Test runner scripts in repository root
- **Pattern**: Follow existing pytest patterns in tests/ directory
- **Test Data**: JSON test case definitions for systematic testing

## Dependencies
- Complete TOML implementation (already implemented)
- pytest testing framework
- JSON test case definitions
- Existing test infrastructure in tests/ directory

## Existing Documentation
- **Detailed Design**: `./.amazonq/rules/toml-sep/detailed-design.md` - Comprehensive technical design with testing strategy
- **Project Structure**: Python project with pytest testing framework
- **Test Organization**: tests/unit/ and tests/integration/ directories

## Current TOML Test Coverage
- **Total Tests**: 37 comprehensive TOML tests already implemented
- **Unit Tests**: 22 tests in test_configloader.py covering all parsing functions
- **Session Tests**: 7 tests in test_session.py covering session integration
- **Integration Tests**: 8 tests in test_toml_session.py covering end-to-end scenarios

## Existing JSON Test Patterns
- **Pattern Found**: tests/unit/cbor/ uses JSON-driven test cases
- **Structure**: JSON files with test case arrays containing description, input, expect
- **Usage**: Test runners load JSON files and parametrize tests using pytest
- **Example**: decode-success-tests.json with structured test case definitions

## Key Features to Test
1. **TOML Parsing Functions**: raw_toml_parse, load_toml_config, build_toml_profile_map
2. **Data Type Conversion**: _convert_toml_types with backward compatibility
3. **Session Integration**: full_config property with TOML support
4. **Error Handling**: ConfigParseError and ConfigNotFound scenarios
5. **File Discovery**: Environment variables and default locations
6. **Precedence Logic**: TOML over INI with warnings

## Testing Approach
- JSON-driven test cases for systematic coverage
- Test runners that execute predefined test scenarios
- Validation of both positive and negative test cases
- Integration with existing pytest infrastructure
- Follow existing JSON test patterns from cbor tests

## Key Challenge
Create comprehensive test runners that systematically validate all TOML functionality using JSON test case definitions while integrating with existing test infrastructure and following established patterns.
