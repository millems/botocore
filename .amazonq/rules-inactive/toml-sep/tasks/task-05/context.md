# Session Integration for TOML Support - Implementation Context

## Task Overview
Integrating TOML configuration support into the `Session.full_config` property to provide seamless TOML support while maintaining full backward compatibility with existing INI configurations.

## Project Structure
- **Repository**: botocore (AWS SDK for Python core library)
- **Language**: Python
- **Target File**: `botocore/session.py`
- **Key Property**: `Session.full_config`

## Requirements Summary
1. Check for `AWS_CONFIG_FILE_TOML` environment variable first
2. Check for default `~/.aws/config.toml` file if env var not set
3. Fall back to existing INI logic if no TOML file found
4. Log warnings when both TOML and INI environment variables are set
5. Maintain same caching behavior and credentials file merging

## Implementation Paths
- **Primary File**: `botocore/session.py`
- **Target Property**: `full_config` property in Session class
- **Integration Point**: Before existing INI loading logic

## Dependencies
- TOML parsing functions from previous tasks (`load_toml_config`)
- Existing session infrastructure
- Environment variable access via `get_config_variable()`
- Logging infrastructure

## Acceptance Criteria
1. TOML environment variable priority
2. Default TOML file discovery
3. INI fallback behavior preservation
4. Environment variable conflict warnings
5. Caching behavior preservation
6. Credentials file merging preservation

## Testing Strategy
- Unit tests for TOML file discovery logic
- Environment variable precedence testing
- Caching behavior validation
- Credentials merging verification
- Backward compatibility testing

## Key Challenge
Must integrate TOML support without breaking any existing behavior, including caching, error handling, and credentials file merging.
