# Idea Honing - TOML Configuration Support

This document captures the requirements clarification process for implementing TOML configuration support in botocore.

## Question 1: Implementation Scope and Priority

Based on the design document, there are three main technical challenges identified:

1. **Array Data Type Incompatibility**: `sigv4a_signing_region_set` property has no conversion function
2. **TOML Section Syntax Incompatibility**: Existing `_parse_section()` uses `shlex.split()` for space-separated format
3. **Third-Party Plugin Compatibility**: Plugins may depend on specific configuration data types

Which of these challenges should be prioritized first in the implementation, and are there any that could be deferred to a later phase? Should we implement a minimal viable version that handles basic TOML parsing first, or tackle all challenges comprehensively from the start?

**Answer**: For challenge #2 (TOML Section Syntax), we should have separate parsing for TOML and not try to reuse the INI parsing pieces. For challenges #1 (Array Data Type) and #3 (Plugin Compatibility), we should ensure that users of session.py do not break by matching the existing data types when returning from those methods. These challenges are small enough to include in earlier phases rather than deferring them.

## Question 2: TOML Library Selection and Dependency Management

The design document mentions using Python 3.11+'s built-in `tomllib` module for newer versions and the external `tomli` dependency for older versions. 

How should we handle the dependency management strategy? Should we:
- Make `tomli` an optional dependency that's only required when TOML files are actually used?
- Add `tomli` as a required dependency for all Python versions for consistency?
- Use conditional imports with graceful degradation if TOML libraries aren't available?

Also, what's the minimum Python version that botocore currently supports, and does this affect our TOML library choice?

**Answer**: Boto supports Python 3.9+. Let's focus on 3.11+ for earlier milestones, and add support for 3.9 and 3.10 later. We'll use conditional imports in those versions.

## Question 3: Error Handling and Fallback Strategy

The SEP specifies strict parsing with no fallback to INI when TOML parsing fails. However, there are different scenarios to consider:

1. **TOML file exists but has syntax errors** - Should fail with clear error message
2. **AWS_CONFIG_FILE_TOML is set but file doesn't exist** - Should this fail or fall back to INI discovery?
3. **TOML library not available on older Python versions** - Should this gracefully degrade to INI-only mode or fail?
4. **Mixed environment where some users have TOML files and others don't** - How should we handle deployment scenarios?

What's the preferred error handling approach for each of these scenarios, especially considering the phased rollout (3.11+ first, then 3.9-3.10)?

**Answer**: In cases 1-3, we should fail. Case 4 is not a concern.

## Question 4: Data Type Conversion Implementation

The design document identifies that `sigv4a_signing_region_set` has no existing conversion function in the configprovider, but we need to ensure session.py users don't break by matching existing data types.

For the array conversion specifically:
- Should we create a new conversion function in `botocore.configprovider` for array properties?
- Should the conversion happen at the configloader level before data reaches the provider chain?
- How should we handle the conversion from TOML native arrays `["us-east-1", "us-west-2"]` to the expected format that existing code expects?

Also, are there any other properties beyond `sigv4a_signing_region_set` that might need special array handling?

**Answer**: Let's have the config provider for TOML arrays do the conversion to match the format of INI, for backwards-compatibility. This is the only array we need to consider.

## Question 5: File Discovery Integration

The design document proposes modifying the `Session.full_config` property to check for TOML files first. However, there are some integration details to clarify:

- Should the TOML file discovery logic be integrated directly into the existing `full_config` property, or should we create a separate method that `full_config` calls?
- How should we handle the warning logic when both `AWS_CONFIG_FILE_TOML` and INI environment variables are set?
- Should the TOML file path resolution use the same platform-specific logic as the existing INI file discovery?

Also, should we maintain the same caching behavior for TOML config as exists for INI config (where `self._config` is cached)?

**Answer**: Integrate it directly into the full_config property. We should write the warning to the logger. Use the same path resolver for TOML as was used for INI. Use the same caching behavior as well.
