# TOML Section Parsing with Dot Notation - Implementation Context

## Task Overview
Implementing `build_toml_profile_map(parsed_toml_config)` function to handle TOML's dot notation syntax for sections. This converts TOML table structures into the standard configuration structure expected by botocore.

## Project Structure
- **Repository**: botocore (AWS SDK for Python core library)
- **Language**: Python
- **Target File**: `botocore/configloader.py`
- **Key Function**: `build_toml_profile_map(parsed_toml_config)`

## Requirements Summary
1. Handle TOML dot notation: `[profile.name]` → profiles['name']
2. Handle SSO sessions: `[sso-session.name]` → sso_sessions['name']
3. Handle services: `[services.name]` → services['name']
4. Preserve other top-level sections as-is
5. Output structure must match `build_profile_map()` for INI files
6. Process nested dictionaries recursively

## Implementation Paths
- **Primary File**: `botocore/configloader.py`
- **Pattern**: Follow existing `build_profile_map()` structure
- **Key Difference**: TOML dot notation vs INI space-separated sections

## Dependencies
- Core TOML parsing functions from task-02
- Understanding of existing `build_profile_map()` output structure
- TOML table structure handling

## Acceptance Criteria
1. Profile section parsing with dot notation
2. SSO session parsing
3. Services section parsing
4. Output structure compatibility with INI format
5. Top-level section preservation

## Testing Strategy
- Unit tests for dot notation parsing
- Structure compatibility validation
- Edge case handling for nested configurations
- Integration with existing configuration system

## Key Challenge
TOML uses dot notation (`[profile.name]`) while INI uses space-separated format (`[profile name]`). The existing `_parse_section()` function uses `shlex.split()` which is incompatible with TOML syntax, requiring separate parsing logic.
