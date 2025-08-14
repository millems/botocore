# Task: Integrate TOML Support into Session.full_config Property

## Description
Modify the `full_config` property in `botocore/session.py` to check for TOML configuration files before falling back to INI files. This integration provides seamless TOML support while maintaining full backward compatibility with existing INI configurations.

## Background
The `Session.full_config` property is the primary entry point for configuration loading in botocore. It currently loads INI files through `botocore.configloader.load_config()`. TOML support requires checking for TOML files first while preserving all existing behavior including caching and credentials file merging.

## Technical Requirements
1. Check for `AWS_CONFIG_FILE_TOML` environment variable first
2. If not set, check for default `~/.aws/config.toml` file
3. Fall back to existing INI logic if no TOML file found
4. Log warnings when both TOML and INI environment variables are set
5. Maintain same caching behavior using `self._config`
6. Preserve existing credentials file merging logic
7. Handle `ConfigNotFound` exceptions appropriately

## Dependencies
- TOML parsing functions from previous tasks
- Existing `Session.full_config` property implementation
- `get_config_variable()` method for environment variable access
- Logging infrastructure for warnings

## Implementation Approach
1. Modify the `full_config` property in Session class
2. Add TOML file discovery logic before INI fallback
3. Integrate warning logging for environment variable conflicts
4. Preserve existing error handling and caching patterns
5. Maintain credentials file merging behavior

## Acceptance Criteria

1. **TOML Environment Variable Priority**
   - Given `AWS_CONFIG_FILE_TOML` environment variable is set to a valid TOML file
   - When `session.full_config` is accessed
   - Then the TOML file is loaded instead of any INI file

2. **Default TOML File Discovery**
   - Given no `AWS_CONFIG_FILE_TOML` environment variable is set
   - When `~/.aws/config.toml` exists and `session.full_config` is accessed
   - Then the default TOML file is loaded

3. **INI Fallback Behavior**
   - Given no TOML files are found (environment variable or default location)
   - When `session.full_config` is accessed
   - Then existing INI loading logic is used unchanged

4. **Environment Variable Conflict Warning**
   - Given both `AWS_CONFIG_FILE_TOML` and `AWS_CONFIG_FILE` are set
   - When `session.full_config` is accessed
   - Then a warning is logged and TOML file takes precedence

5. **Caching Behavior Preservation**
   - Given a configuration file has been loaded once
   - When `session.full_config` is accessed again
   - Then the cached configuration is returned without re-parsing

6. **Credentials File Merging**
   - Given a TOML configuration file and a credentials file exist
   - When `session.full_config` is accessed
   - Then credentials are merged into profiles following existing logic

## Metadata
- **Complexity**: Medium
- **Labels**: Session, Integration, File Discovery, Caching, Backward Compatibility
- **Required Skills**: Python, Session management, File I/O, Logging
