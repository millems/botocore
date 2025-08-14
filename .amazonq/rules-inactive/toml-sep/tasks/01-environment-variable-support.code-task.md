# Task: Add TOML Environment Variable Support to ConfigProvider

## Description
Add support for the `AWS_CONFIG_FILE_TOML` environment variable to the botocore configuration system. This enables users to specify custom TOML configuration file locations through environment variables, following the same pattern as existing INI configuration variables.

## Background
The botocore configuration system uses `BOTOCORE_DEFAUT_SESSION_VARIABLES` to define environment variables that can be accessed through the session. Adding TOML support requires integrating a new `config_file_toml` variable that maps to the `AWS_CONFIG_FILE_TOML` environment variable.

## Technical Requirements
1. Modify `BOTOCORE_DEFAUT_SESSION_VARIABLES` dictionary in `botocore/configprovider.py`
2. Add `config_file_toml` variable mapping to `AWS_CONFIG_FILE_TOML` environment variable
3. Follow existing pattern used for `config_file` variable
4. Ensure variable is accessible via `session.get_config_variable('config_file_toml')`
5. Maintain compatibility with existing configuration variables

## Dependencies
- Existing `botocore/configprovider.py` file
- Session configuration system
- Environment variable handling infrastructure

## Implementation Approach
1. Locate `BOTOCORE_DEFAUT_SESSION_VARIABLES` dictionary in configprovider.py
2. Add new entry following the existing tuple format: `(default_value, env_var_name, config_var_name, conversion_func)`
3. Use the same pattern as `config_file` variable for consistency

## Acceptance Criteria

1. **Environment Variable Registration**
   - Given the `AWS_CONFIG_FILE_TOML` environment variable is set
   - When a session is created
   - Then `session.get_config_variable('config_file_toml')` returns the environment variable value

2. **Default Behavior**
   - Given no `AWS_CONFIG_FILE_TOML` environment variable is set
   - When `session.get_config_variable('config_file_toml')` is called
   - Then it returns None (default value)

3. **Integration with Session System**
   - Given the new variable is added to `BOTOCORE_DEFAUT_SESSION_VARIABLES`
   - When the session configuration system initializes
   - Then the variable is available through standard session methods

## Metadata
- **Complexity**: Low
- **Labels**: Configuration, Environment Variables, Session
- **Required Skills**: Python, botocore configuration system
