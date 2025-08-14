# Task: Add TOML Section Parsing with Dot Notation Support

## Description
Implement `build_toml_profile_map(parsed_toml_config)` function to handle TOML's dot notation syntax for sections. This function converts TOML table structures into the standard configuration structure expected by botocore, handling the fundamental difference between TOML dot notation and INI space-separated sections.

## Background
TOML uses dot notation for nested sections (`[profile.name]`, `[sso-session.name]`) while INI uses space-separated format (`[profile name]`, `[sso-session name]`). The existing `_parse_section()` function uses `shlex.split()` which is incompatible with TOML syntax, requiring separate parsing logic.

## Technical Requirements
1. Implement `build_toml_profile_map(parsed_toml_config)` function in `botocore/configloader.py`
2. Handle TOML dot notation: `[profile.name]` → profiles['name']
3. Handle SSO sessions: `[sso-session.name]` → sso_sessions['name']
4. Handle services: `[services.name]` → services['name']
5. Preserve other top-level sections as-is
6. Output structure must match `build_profile_map()` for INI files
7. Process nested dictionaries recursively

## Dependencies
- Core TOML parsing functions from previous task
- Understanding of existing `build_profile_map()` output structure
- TOML table structure handling

## Implementation Approach
1. Parse TOML table keys to identify section types (profile, sso-session, services)
2. Extract section names from dot notation
3. Build structured dictionary matching INI output format
4. Handle nested configurations within each section
5. Preserve non-standard sections for extensibility

## Acceptance Criteria

1. **Profile Section Parsing**
   - Given TOML with `[profile.default]` and `[profile.dev]` sections
   - When `build_toml_profile_map()` processes the config
   - Then output contains `profiles: {'default': {...}, 'dev': {...}}`

2. **SSO Session Parsing**
   - Given TOML with `[sso-session.my-sso]` section
   - When `build_toml_profile_map()` processes the config
   - Then output contains `sso_sessions: {'my-sso': {...}}`

3. **Services Section Parsing**
   - Given TOML with `[services.s3]` section
   - When `build_toml_profile_map()` processes the config
   - Then output contains `services: {'s3': {...}}`

4. **Output Structure Compatibility**
   - Given any valid TOML configuration
   - When processed through `build_toml_profile_map()`
   - Then output structure matches the format produced by INI `build_profile_map()`

5. **Top-Level Section Preservation**
   - Given TOML with custom top-level sections
   - When `build_toml_profile_map()` processes the config
   - Then custom sections are preserved in the output

## Metadata
- **Complexity**: Medium
- **Labels**: TOML, Section Parsing, Dot Notation, Configuration Structure
- **Required Skills**: Python, TOML format, Dictionary manipulation, Pattern matching
