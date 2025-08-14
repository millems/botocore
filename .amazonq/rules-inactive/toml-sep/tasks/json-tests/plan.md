# JSON Test Runners - Implementation Plan

## Test Strategy

### Current State Analysis
- **37 comprehensive TOML tests** already implemented across unit, session, and integration test files
- **Existing JSON test pattern** found in tests/unit/cbor/ with structured test case definitions
- **pytest framework** with parametrized test execution using JSON data files

### JSON Test Runner Design

#### 1. Test Case JSON Schema
Following the existing cbor pattern, create JSON files with test case arrays:
```json
[
  {
    "description": "Test case description",
    "category": "unit|integration|compatibility", 
    "input": {
      "toml_content": "TOML configuration string",
      "environment": {"AWS_CONFIG_FILE_TOML": "/path/to/file"},
      "files": {"config.toml": "content"}
    },
    "expect": {
      "result": "expected output",
      "exception": "expected exception type",
      "warnings": ["expected warning messages"]
    }
  }
]
```

#### 2. Test Runner Structure
- **Unit Test Runner**: `tests/unit/toml/test_toml_json_runner.py`
- **Integration Test Runner**: `tests/integration/test_toml_json_runner.py`
- **JSON Test Data**: `tests/unit/toml/toml-test-cases.json`

#### 3. Test Categories

**Unit Tests (22 existing tests to convert)**:
- TOML parsing with various data types
- Section syntax handling (dot notation)
- Data type conversion accuracy
- Error conditions (syntax errors, missing files, missing library)
- File path expansion and validation
- Edge cases (empty files, special characters, complex nesting)

**Session Tests (7 existing tests to convert)**:
- Environment variable handling
- Configuration caching behavior
- Default file discovery
- TOML environment variable priority
- Credentials not merged with TOML

**Integration Tests (8 existing tests to convert)**:
- End-to-end configuration loading
- Precedence logic (TOML over INI)
- Client creation with TOML configuration
- Environment variable warning logging
- Complex configuration scenarios

## Implementation Plan

### Phase 1: JSON Test Case Definitions
1. **Create JSON schema** for test case structure
2. **Extract test scenarios** from existing 37 TOML tests
3. **Convert test cases** to JSON format with input/output pairs
4. **Organize by category** (unit, session, integration)

### Phase 2: Test Runner Implementation
1. **Create unit test runner** following cbor pattern
2. **Create integration test runner** for end-to-end scenarios
3. **Implement test data loading** and parametrization
4. **Add proper test isolation** with temporary files and environment mocking

### Phase 3: Test Execution and Validation
1. **Run JSON-driven tests** and compare with existing test results
2. **Validate test coverage** matches existing 37 tests
3. **Ensure test isolation** and proper cleanup
4. **Verify pytest integration** and reporting

### Phase 4: Documentation and Usage
1. **Document test runner usage** and JSON schema
2. **Create examples** of adding new test cases
3. **Integrate with existing test suite** execution

## Test Case Extraction Strategy

### From Unit Tests (test_configloader.py)
- Extract 22 TOML test scenarios with input TOML content and expected parsed results
- Include error test cases with expected exceptions
- Cover all data type conversion scenarios

### From Session Tests (test_session.py)  
- Extract 7 session integration scenarios with environment variable setups
- Include configuration caching and discovery test cases
- Cover TOML precedence and warning scenarios

### From Integration Tests (test_toml_session.py)
- Extract 8 end-to-end scenarios with complete file system setups
- Include client creation and complex configuration scenarios
- Cover precedence logic and fallback mechanisms

## Success Criteria

1. **Complete Coverage**: JSON test runners execute all 37 existing TOML test scenarios
2. **Systematic Testing**: JSON-driven approach allows easy addition of new test cases
3. **Pattern Consistency**: Follows existing cbor JSON test pattern
4. **Test Isolation**: Proper temporary file and environment variable handling
5. **Integration**: Seamless integration with existing pytest test suite
6. **Documentation**: Clear usage instructions and examples

## Risk Mitigation

### Test Data Complexity
- **Risk**: TOML test cases involve complex file system operations and environment variables
- **Mitigation**: Use structured JSON schema with file content and environment specifications

### Test Isolation
- **Risk**: Tests may interfere with each other through shared file system or environment state
- **Mitigation**: Follow existing patterns for temporary files and environment variable mocking

### Maintenance Overhead
- **Risk**: Maintaining both existing tests and JSON test cases
- **Mitigation**: JSON test runners complement existing tests, don't replace them initially
