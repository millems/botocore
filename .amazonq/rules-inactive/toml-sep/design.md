# TOML Configuration Support Design Document

## Executive Summary

This document outlines the implementation of TOML configuration file support for the AWS SDK for Python as specified in the SEP. The feature provides native data types (boolean, integer, array) as an alternative to the string-only INI format currently used. The implementation uses a hybrid session-level approach that combines file discovery in `session.py` with TOML parsing extensions in `configloader.py`. This approach modifies the configuration loading pipeline without breaking the existing provider chain or credential resolution mechanisms.

## Problem Statement

### Current INI Format Limitations

The existing INI-based configuration system stores all configuration values as strings, requiring runtime type conversion throughout the codebase. This creates several issues: boolean values suffer from ambiguity with variations like `"true"`, `"True"`, `"TRUE"`, `"false"`, `"False"`, `"FALSE"`, `"1"`, `"0"`, `"yes"`, `"Yes"`, `"YES"`, `"no"`, `"No"`, and `"NO"` all being valid representations; array values are stored as comma-separated strings that are prone to whitespace-related parsing errors; and there is no native validation for numeric ranges or data types at the configuration level.

### SEP Requirements

The SEP mandates support for native TOML data types including boolean (`true`/`false`), integer, and array values. TOML files must take precedence over INI files when both exist in the same location. The implementation must support the `AWS_CONFIG_FILE_TOML` environment variable for specifying custom TOML file locations. TOML files use a different section syntax with dot notation: `[profile.name]`, `[sso-session.name]`, and `[services.name]`. The parser must implement strict parsing with no fallback to INI format when TOML parsing errors occur.

### Backward Compatibility Constraints

The implementation must ensure that existing INI files continue working without any modifications. No breaking changes to public APIs are permitted. All existing environment variables must remain functional. The provider chain resolution logic must remain intact to avoid disrupting the existing configuration resolution mechanisms.

## Design Approach

### Selected Solution: Hybrid Implementation

The chosen approach implements file discovery through session-level logic in the `full_config` property, while TOML parsing is handled through ConfigLoader extensions. A conversion layer manages the translation between TOML native types and existing configuration consumers. The precedence logic implements TOML file discovery before falling back to INI format.

### Rejected Alternatives Analysis

Three alternative approaches were considered and rejected. The ConfigLoader extension-only approach was rejected because it cannot derive TOML file paths from INI file paths, and the `load_config(filename)` API contract prevents internal format switching without breaking changes to function signatures. The provider chain extension approach was rejected because the provider chain resolves variables rather than file contents, and the session bypasses the provider chain for config file loading through direct `botocore.configloader.load_config()` calls, creating an architecture mismatch where config file parsing occurs before provider chain resolution. The pure session-level implementation was rejected because it would expose TOML native types directly to all configuration consumers, requiring defensive type checking across an extensive codebase.

## Technical Design

### File Discovery and Precedence Logic

The default TOML file location is `~/.aws/config.toml`, with INI fallback to the existing `~/.aws/config` location. Platform-specific path resolution uses the existing session logic to maintain consistency. The new `AWS_CONFIG_FILE_TOML` environment variable integrates with the existing `BOTOCORE_DEFAUT_SESSION_VARIABLES` system and takes precedence over `AWS_CONFIG_FILE` when both are set.

The session integration modifies the `Session.full_config` property in `botocore.session` to check for TOML files first:

```python
@property
def full_config(self):
    if self._config is None:
        toml_file = self.get_config_variable('config_file_toml')
        if toml_file and os.path.exists(toml_file):
            self._config = botocore.configloader.load_toml_config(toml_file)
        else:
            # Existing INI logic unchanged
```

### TOML Parsing Implementation

The implementation adds three new functions to `botocore.configloader`: `load_toml_config(config_filename)` serves as the main entry point with a signature matching the existing `load_config()` function; `raw_toml_parse(config_filename)` handles TOML file parsing with native type preservation; and `build_toml_profile_map(parsed_toml_config)` processes sections using TOML-specific syntax.

TOML section syntax differs significantly from INI format. TOML uses `[profile.default]` for profile name extraction, while the current INI format uses `[profile default]` with `shlex.split()` parsing. The existing `_parse_section()` function in `botocore.configloader` is incompatible with dot notation and requires modification.

Library integration uses Python 3.11+'s built-in `tomllib` module for newer Python versions, while older versions require the external `tomli` dependency. Error handling wrappers ensure consistent exception types across both TOML and INI parsing.

### Data Type Conversion Strategy

Boolean properties including `use_dualstack_endpoint`, `use_fips_endpoint`, `aws_endpoint_discovery_enabled`, `s3_disable_express_session_auth`, `ec2_metadata_v1_disabled`, and `disable_request_compression` convert from TOML `true`/`false` values to Python `True`/`False` objects. The existing `ensure_boolean()` function in `botocore.utils` already handles both string and boolean inputs, providing compatibility between TOML native types and existing string-based INI values.

Integer properties including `duration_seconds`, `metadata_service_timeout`, and `request_min_compression_size_bytes` convert from TOML integer values like `3600` directly to Python integer objects. Existing code uses `int()` conversion where needed, maintaining compatibility with the current string-to-integer conversion patterns.

Array properties present the most significant challenge. The `sigv4a_signing_region_set` property converts from TOML arrays like `["us-east-1", "us-west-2"]` to Python lists. However, no existing conversion function exists in `botocore.configprovider` for this property, creating a technical issue that requires new conversion logic.

The conversion layer must handle array-to-list conversion for `sigv4a_signing_region_set`, boolean string-to-boolean conversion (handled by existing `ensure_boolean()`), integer string-to-integer conversion (handled by existing `int()` calls), mixed-type handling in credentials file merging operations, type normalization in `_merge_list_of_dicts()` operations in `botocore.configloader`, and defensive type checking throughout the configuration loading pipeline.

## Implementation Plan

### Core File Modifications

The `botocore/session.py` file requires modification of the `full_config` property for TOML file discovery, addition of environment variable conflict warning logic, and preservation of existing credentials file merging behavior.

The `botocore/configloader.py` file needs new TOML parsing functions with native type support, modification of `build_profile_map()` for TOML section syntax compatibility, and extension of `_parse_section()` or creation of a TOML-specific equivalent.

The `botocore/configprovider.py` file must add `config_file_toml` to the `BOTOCORE_DEFAUT_SESSION_VARIABLES` dictionary, implement array conversion functions for affected properties, and extend the type conversion infrastructure.

Supporting files include `botocore/exceptions.py` for TOML-specific error handling, `requirements.txt` or `setup.py` for the TOML library dependency, and type conversion utilities for mixed TOML/INI scenarios.

### Data Structure Compatibility

Both TOML and INI parsing produce identical output structures: `{'profiles': {...}, 'sso_sessions': {...}, 'services': {...}}`. Native types are preserved where beneficial and converted where necessary to ensure existing code paths receive expected data types.

Credentials file integration handles TOML config combined with INI credentials merging, implements type conflict resolution in profile merging, and ensures profile name matching across formats.

## Risk Assessment

### Array Data Type Incompatibility

The `sigv4a_signing_region_set` property has no conversion function in the provider configuration. TOML arrays versus INI comma-separated strings create a type mismatch that requires new conversion logic in the configprovider.

### TOML Section Syntax Incompatibility

The existing `_parse_section()` function in `botocore.configloader` uses `shlex.split("profile name")` for space-separated format parsing. TOML's `[profile.name]` dot notation requires different parsing logic, necessitating modification or replacement of the section parsing logic.

### Third-Party Plugin Compatibility

Third-party plugins may depend on specific configuration data types. Custom configuration providers may expect string inputs, and extension points may access raw configuration data in ways that could be affected by the introduction of native TOML types.

---

**Document Scope**: Technical implementation details for development team  
**Target Audience**: Senior engineers, technical leads, and architects
