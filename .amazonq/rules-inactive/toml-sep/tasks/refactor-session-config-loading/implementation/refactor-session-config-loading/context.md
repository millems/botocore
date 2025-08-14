# Refactor Session Config Loading - Implementation Context

## Task Overview
Extract duplicated try/catch blocks in `botocore/session.py` full_config property into a clean helper method that handles TOML-to-INI fallback logic. This refactoring will improve maintainability and reduce code duplication while preserving all existing functionality.

## Project Structure
- **Repository**: botocore (AWS SDK for Python core library)
- **Language**: Python
- **Target File**: `botocore/session.py`
- **Testing Framework**: pytest (detected from existing test structure)

## Requirements Summary
Based on the code task description:

### Technical Requirements
1. Extract config loading logic into private helper method `_load_config_with_fallback()`
2. Implement clean fallback chain: TOML → INI → default empty config
3. Preserve all existing error handling behavior
4. Maintain same return structure and types
5. Keep warning logic separate and unchanged
6. Ensure credentials file merging logic remains unchanged

### Acceptance Criteria
- Helper method returns same config structure as current implementation
- TOML priority maintained (TOML over INI when both exist)
- INI fallback works when TOML doesn't exist
- Default fallback returns `{'profiles': {}}` when neither exists
- Error handling preservation with same exceptions
- No functional changes to existing behavior

## Implementation Paths
- **Primary File**: `botocore/session.py` - Session class full_config property
- **Helper Method**: `_load_config_with_fallback()` - New private method
- **Dependencies**: Existing configloader functions and ConfigNotFound exception

## Dependencies
- `botocore.configloader.load_toml_config()` function
- `botocore.configloader.load_config()` function  
- `ConfigNotFound` exception handling
- Current session instance variables and methods

## Existing Documentation
- **Project Structure**: Python project with pytest testing framework
- **Test Organization**: tests/unit/ and tests/integration/ directories
- **No DEVELOPMENT.md found**: Using generic Python best practices

## Current Implementation Analysis
The current `full_config` property in `botocore/session.py` has duplicated try/catch blocks:

**Current Structure (lines 455-485):**
```python
try:
    toml_config_file = self.get_config_variable('config_file_toml')
    self._config = botocore.configloader.load_toml_config(toml_config_file)
except ConfigNotFound:
    # Fallback to existing INI logic
    try:
        config_file = self.get_config_variable('config_file')
        self._config = botocore.configloader.load_config(config_file)
    except ConfigNotFound:
        self._config = {'profiles': {}}
```

**Issues Identified:**
1. Nested try/catch blocks create complexity
2. Duplication of config loading pattern
3. Mixed concerns (loading + credentials merging)
4. Hard to follow fallback logic

## Refactoring Strategy
- Extract the config loading logic into a focused helper method
- Use clean iteration over loaders to eliminate duplication
- Preserve all existing behavior and error handling
- Keep warning logic and credentials merging separate
- Maintain same return types and structures

**Proposed Helper Method Structure:**
```python
def _load_config_with_fallback(self):
    """Load configuration with TOML->INI->default fallback."""
    loaders = [
        (self.get_config_variable('config_file_toml'), botocore.configloader.load_toml_config),
        (self.get_config_variable('config_file'), botocore.configloader.load_config)
    ]
    
    for config_file, loader_func in loaders:
        try:
            return loader_func(config_file)
        except ConfigNotFound:
            continue
    
    return {'profiles': {}}
```

## Key Challenge
Ensure the refactoring maintains exact behavioral compatibility while improving code structure and maintainability.
