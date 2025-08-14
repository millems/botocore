# TOML Environment Variable Support - Implementation Context

## Task Overview
Implementing support for the `AWS_CONFIG_FILE_TOML` environment variable in botocore's configuration system. This is the first task in the TOML SEP implementation.

## Project Structure
- **Repository**: botocore (AWS SDK for Python core library)
- **Language**: Python
- **Size**: Large codebase (4,904 files, 8,235 symbols)
- **Key Directories**:
  - `botocore/` - Main source code
  - `tests/` - Test suite
  - `botocore/data/` - AWS service definitions

## Requirements Summary
1. Add `config_file_toml` variable to `BOTOCORE_DEFAUT_SESSION_VARIABLES` in `botocore/configprovider.py`
2. Map to `AWS_CONFIG_FILE_TOML` environment variable
3. Follow existing pattern used for `config_file` variable
4. Ensure accessibility via `session.get_config_variable('config_file_toml')`
5. Maintain backward compatibility

## Implementation Paths
- **Primary File**: `botocore/configprovider.py`
- **Target Dictionary**: `BOTOCORE_DEFAUT_SESSION_VARIABLES`
- **Pattern**: Follow existing `config_file` variable format

## Dependencies
- Existing session configuration system
- Environment variable handling infrastructure
- No external dependencies required

## Acceptance Criteria
1. Environment variable registration works correctly
2. Default behavior returns None when not set
3. Integration with session system functions properly

## Existing Documentation
- CONTRIBUTING.rst: Standard contribution guidelines, requires unit tests
- Project uses ruff for code style enforcement
- Pre-commit hooks available for validation

## Testing Strategy
- Unit tests required (per CONTRIBUTING.rst)
- Test environment variable behavior
- Test session integration
- Test default value handling
