# Task: Reorganize TOML Test Structure into Focused, Modular Test Classes

## Description
Refactor the existing TOML test classes to be more modular and focused by breaking down large test classes into smaller, specialized classes that each test a specific aspect of TOML functionality. This will improve test maintainability, readability, and make it easier to run specific test categories.

## Background
The current TOML test implementation has large test classes with many methods covering different aspects of TOML functionality. This makes it harder to understand what each test class is responsible for and makes it difficult to run specific categories of tests. Breaking these into focused classes will improve organization and maintainability.

## Technical Requirements
1. Analyze existing TOML test classes in `test_configloader.py`, `test_session.py`, and `test_toml_session.py`
2. Create focused test classes for different TOML functionality areas
3. Ensure all existing test coverage is preserved
4. Maintain existing test naming conventions and patterns
5. Keep test isolation and setup/teardown patterns consistent
6. Ensure tests can still be run individually and as groups
7. Update any test discovery or CI configuration if needed

## Dependencies
- Existing TOML test methods in multiple test files
- Current test infrastructure and patterns
- pytest test discovery mechanisms
- Existing test utilities and fixtures

## Implementation Approach
1. Identify logical groupings of existing TOML test methods
2. Create new focused test classes with descriptive names
3. Move related test methods to appropriate classes
4. Ensure proper test class inheritance and setup
5. Verify all tests still pass after reorganization
6. Update any documentation or comments as needed

## Acceptance Criteria

1. **Parsing Test Class**
   - Given TOML parsing functionality needs testing
   - When `TestTOMLParsing` class is created
   - Then it contains all pure TOML parsing tests (raw_toml_parse, syntax errors, file handling)

2. **Integration Test Class**
   - Given TOML session integration needs testing
   - When `TestTOMLSessionIntegration` class is created
   - Then it contains all session-level integration tests (full_config, environment variables, precedence)

3. **Compatibility Test Class**
   - Given TOML-INI compatibility needs testing
   - When `TestTOMLCompatibility` class is created
   - Then it contains all backward compatibility and equivalence tests

4. **Data Type Test Class**
   - Given TOML data type handling needs testing
   - When `TestTOMLDataTypes` class is created
   - Then it contains all type conversion and normalization tests

5. **Test Coverage Preservation**
   - Given the existing test suite has X% coverage
   - When tests are reorganized into focused classes
   - Then the same coverage percentage is maintained

6. **Test Execution**
   - Given the reorganized test structure
   - When running pytest with class-specific filters
   - Then specific test categories can be run independently

7. **Class Size Reduction**
   - Given the current large test classes
   - When reorganized into focused classes
   - Then no single test class has more than 15 test methods

## Metadata
- **Complexity**: Medium
- **Labels**: Testing, Code Organization, Test Structure, TOML
- **Required Skills**: Python testing, pytest, Test organization
- **Suggested Reviewers**: Someone familiar with testing best practices and botocore test patterns
