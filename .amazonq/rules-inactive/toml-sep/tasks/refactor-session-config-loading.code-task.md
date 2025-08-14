# Task: Refactor Session Config Loading Logic to Eliminate Code Duplication

## Description
Extract the duplicated try/catch blocks in `session.py` full_config property into a clean helper method that handles TOML-to-INI fallback logic. This will improve maintainability and reduce code duplication while preserving existing functionality.

## Background
The current implementation in `botocore/session.py` has duplicated try/catch blocks for loading TOML and INI configuration files. This creates maintenance overhead and makes the logic harder to follow. The duplication exists because we need to try TOML first, then fallback to INI, then provide a default empty config.

## Technical Requirements
1. Extract config loading logic into a private helper method `_load_config_with_fallback()`
2. Implement clean fallback chain: TOML → INI → default empty config
3. Preserve all existing error handling behavior
4. Maintain the same return structure and types
5. Keep the warning logic separate and unchanged
6. Ensure credentials file merging logic remains unchanged

## Dependencies
- Existing `botocore.configloader.load_toml_config()` function
- Existing `botocore.configloader.load_config()` function
- Existing `ConfigNotFound` exception handling
- Current session instance variables and methods

## Implementation Approach
1. Create `_load_config_with_fallback()` method that encapsulates the loading logic
2. Use a clean loop structure to try each loader in sequence
3. Return early on success, continue on ConfigNotFound
4. Keep the method focused only on config loading, not warning or credentials merging
5. Update `full_config` property to use the new helper method

## Acceptance Criteria

1. **Helper Method Creation**
   - Given the session class needs config loading
   - When `_load_config_with_fallback()` is called
   - Then it returns the same config structure as the current implementation

2. **TOML Priority**
   - Given both TOML and INI files exist
   - When the helper method loads config
   - Then TOML config is loaded and INI is ignored

3. **INI Fallback**
   - Given TOML file doesn't exist but INI file exists
   - When the helper method loads config
   - Then INI config is loaded successfully

4. **Default Fallback**
   - Given neither TOML nor INI files exist
   - When the helper method loads config
   - Then it returns `{'profiles': {}}` as default

5. **Error Handling Preservation**
   - Given the same error conditions as before
   - When the helper method encounters errors
   - Then the same exceptions are raised with same behavior

6. **No Functional Changes**
   - Given any existing configuration scenario
   - When using the refactored code
   - Then the behavior is identical to the original implementation

## Metadata
- **Complexity**: Low
- **Labels**: Refactoring, Code Quality, Session, Configuration
- **Required Skills**: Python, Botocore internals
- **Suggested Reviewers**: Someone familiar with botocore session management
