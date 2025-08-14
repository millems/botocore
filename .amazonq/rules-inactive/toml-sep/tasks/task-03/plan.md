# TOML Section Parsing with Dot Notation - Implementation Plan

## Current Status Analysis

The `build_toml_profile_map()` function was already implemented in task-02 and includes:
- Basic dot notation parsing for `[profile.name]`, `[sso-session.name]`, `[services.name]`
- Proper structure mapping to match INI format
- Top-level section preservation

However, the current tests may not fully cover all acceptance criteria from this task.

## Test Strategy

### Test Scenarios to Add/Verify
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

### Test Implementation
- Add specific test cases to `tests/unit/test_configloader.py`
- Test direct calls to `build_toml_profile_map()` function
- Verify edge cases and complex configurations
- Compare output structure with INI equivalent

## Implementation Approach

### 1. Assessment of Current Implementation
- Review existing `build_toml_profile_map()` function
- Verify it handles all required dot notation patterns
- Check if any improvements are needed

### 2. Test Enhancement
- Add comprehensive test cases for all acceptance criteria
- Test edge cases and complex nested configurations
- Verify compatibility with INI output structure

### 3. Implementation Refinement (if needed)
- Make any necessary improvements to the function
- Ensure robust handling of all TOML section types
- Optimize for performance and maintainability

## Acceptance Criteria Mapping

1. **Profile Section Parsing** → Test with multiple profile sections
2. **SSO Session Parsing** → Test with sso-session sections
3. **Services Section Parsing** → Test with services sections
4. **Output Structure Compatibility** → Compare with INI build_profile_map output
5. **Top-Level Section Preservation** → Test with custom sections

## Risk Assessment
- **Low Risk**: Function already exists and basic functionality works
- **Focus Area**: Comprehensive testing to ensure all edge cases are covered
- **Compatibility**: Verify exact match with INI configuration structure
