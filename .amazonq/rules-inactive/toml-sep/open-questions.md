# TOML SEP Open Questions

## Questions for SEP Author

### 1. Unknown Top-Level Sections Handling

**Question**: How should the TOML parser handle unknown top-level sections that are not `profile`, `sso-session`, or `services`?

**Context**: During implementation of `build_toml_profile_map()`, we encountered the case where TOML files may contain top-level sections that don't match the known patterns (profile.*, sso-session.*, services.*).

**Current Implementation**: Following the existing INI parser behavior, unknown sections are preserved in the final configuration dictionary.

**Alternative Approach**: Skip unknown sections and optionally log that they were ignored.

**Impact**: 
- Preserving unknown sections maintains compatibility with existing INI behavior
- Skipping unknown sections could prevent configuration pollution but might break legitimate use cases

**Recommendation Needed**: Should the TOML parser:
1. Preserve unknown sections (current implementation - matches INI behavior)
2. Skip unknown sections silently
3. Skip unknown sections with logging/warning
4. Raise an error for unknown sections

**Related Code**: `botocore/configloader.py` in `build_toml_profile_map()` function, lines handling the `else` case for unknown top-level keys.
