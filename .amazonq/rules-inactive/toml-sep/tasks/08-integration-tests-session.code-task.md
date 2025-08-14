# Task: Create Integration Tests for Session TOML Support

## Description
Create integration tests to verify end-to-end TOML configuration loading through the Session class. These tests validate the complete workflow from file discovery through configuration loading and usage in client creation.

## Background
Integration tests ensure that all TOML components work together correctly in realistic scenarios. They test the complete configuration loading pipeline including file discovery, precedence logic, credentials merging, and actual usage by AWS clients.

## Technical Requirements
1. Create integration tests in `tests/integration/` directory
2. Test TOML file discovery with and without environment variables
3. Test precedence logic (TOML over INI when both exist)
4. Test credentials file merging with TOML configuration
5. Test Session behavior with various TOML configuration scenarios
6. Test client creation using TOML-loaded configuration
7. Test warning logging when both environment variables are set
8. Use temporary files and controlled environments for test isolation

## Dependencies
- Complete TOML implementation from previous tasks
- Session class with TOML integration
- Integration test infrastructure
- Temporary file and directory utilities
- Environment variable mocking capabilities

## Implementation Approach
1. Create new integration test file for TOML functionality
2. Use temporary directories and files for test isolation
3. Mock environment variables as needed
4. Test realistic configuration scenarios
5. Verify end-to-end functionality including client creation

## Acceptance Criteria

1. **TOML File Discovery Integration**
   - Given a temporary TOML configuration file
   - When Session is created with appropriate environment variables
   - Then TOML configuration is loaded and accessible via `full_config`

2. **Precedence Logic Integration**
   - Given both TOML and INI files exist in the same environment
   - When Session loads configuration
   - Then TOML file takes precedence and INI file is ignored

3. **Credentials File Merging Integration**
   - Given a TOML configuration file and a separate credentials file
   - When Session loads configuration
   - Then credentials are properly merged into the configuration profiles

4. **Client Creation Integration**
   - Given a TOML configuration with service-specific settings
   - When an AWS client is created using the Session
   - Then client uses configuration values from the TOML file

5. **Environment Variable Warning Integration**
   - Given both `AWS_CONFIG_FILE_TOML` and `AWS_CONFIG_FILE` are set
   - When Session loads configuration
   - Then warning is logged and TOML file is used

6. **Default File Location Integration**
   - Given a TOML file exists at `~/.aws/config.toml`
   - When Session is created without explicit environment variables
   - Then default TOML file is automatically discovered and loaded

## Metadata
- **Complexity**: High
- **Labels**: Integration Testing, End-to-End Testing, Session, File Discovery, Client Creation
- **Required Skills**: Python, Integration testing, File system operations, Environment management
