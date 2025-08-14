# Rough Idea: TOML Configuration Support Implementation

## Source
- Design Document: `/Users/millem/source/genai-workshop-1/.amazonq/rules/toml-sep/design.md`
- SEP Reference: https://code.amazon.com/packages/AwsDrSeps/commits/93b12ef10c116a65e5c472aa66e22cb25d4e8567

## Initial Concept

Implement TOML configuration file support for the AWS SDK for Python (botocore) as specified in the SEP. The feature provides native data types (boolean, integer, array) as an alternative to the string-only INI format currently used.

## Key Requirements from SEP

- Support native TOML data types: boolean (`true`/`false`), integer, and array values
- TOML files take precedence over INI files when both exist
- Support `AWS_CONFIG_FILE_TOML` environment variable
- Use dot notation syntax: `[profile.name]`, `[sso-session.name]`, `[services.name]`
- Strict parsing with no fallback to INI when TOML parsing fails
- Maintain full backward compatibility with existing INI files

## Design Approach from Document

Hybrid implementation that combines:
- File discovery through session-level logic in `session.py`
- TOML parsing extensions in `configloader.py`
- Conversion layer for translating TOML native types to existing configuration consumers
- Precedence logic implementing TOML file discovery before INI fallback

## Key Technical Challenges

1. **Array Data Type Incompatibility**: `sigv4a_signing_region_set` property has no conversion function in provider configuration
2. **TOML Section Syntax Incompatibility**: Existing `_parse_section()` uses `shlex.split()` for space-separated format, TOML uses dot notation
3. **Third-Party Plugin Compatibility**: Plugins may depend on specific configuration data types

## Implementation Files to Modify

- `botocore/session.py`: Modify `full_config` property for TOML file discovery
- `botocore/configloader.py`: Add TOML parsing functions with native type support
- `botocore/configprovider.py`: Add `config_file_toml` variable and array conversion functions
- Supporting files for error handling and dependencies
