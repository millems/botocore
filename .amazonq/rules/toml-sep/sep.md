# TOML Configuration File Support

## Abstract

This SEP proposes adding TOML (Tom's Obvious, Minimal Language) format support to AWS SDK configuration files as an alternative to the existing INI format. The TOML format will be supported through a single `config.toml` file that combines both configuration and credentials, located at `~/.aws/config.toml` by default.

TOML support addresses key limitations of the current INI format by providing native data types (boolean, integer, array), improved structural clarity, and better validation capabilities. Properties currently represented as strings in INI files will be converted to their appropriate native types in TOML: boolean properties like `use_dualstack_endpoint` will use native `true`/`false` values, numeric properties like `duration_seconds` will use integer types, and comma-separated values like `sigv4a_signing_region_set` will become proper arrays.

The implementation maintains full backward compatibility with existing INI files. When both TOML and INI files are present, TOML takes precedence. A new environment variable `AWS_CONFIG_FILE_TOML` allows users to specify custom TOML file locations, with strict parsing that does not fall back to INI files when TOML is explicitly specified.

This enhancement improves the developer experience by reducing configuration errors through type safety, enabling better IDE support and validation tooling, and providing a more structured and readable configuration format. The feature will be implemented consistently across all AWS SDKs using core TOML v1.0.0 specification features only, ensuring cross-platform compatibility and consistent behavior.

## Motivation

The current INI-based configuration format for AWS SDKs, while functional, presents several limitations that impact developer experience and configuration reliability. All configuration properties are stored as strings, requiring runtime parsing and type conversion that can lead to configuration errors. Boolean values like `use_dualstack_endpoint = true` are stored as string literals, making it unclear whether the value should be `"true"`, `"True"`, `"1"`, or other variations. Numeric values like `duration_seconds = 3600` require string-to-integer conversion with potential for parsing errors. List values like `sigv4a_signing_region_set = us-east-1,us-west-2` use comma-separated strings that are difficult to validate and prone to whitespace-related issues.

TOML format support addresses these customer pain points by providing native data types that eliminate ambiguity and reduce configuration errors. Developers benefit from:

1. **Type Safety**: Boolean properties use native `true`/`false` values, eliminating string parsing ambiguity
2. **Enhanced Readability**: TOML's structured format with native arrays and clear section hierarchy improves configuration comprehension
3. **Better Tooling Support**: TOML has superior IDE support with syntax highlighting, validation, and auto-completion compared to INI files
4. **Reduced Configuration Errors**: Native data types prevent common mistakes like incorrect boolean values or malformed arrays
5. **Future Extensibility**: TOML's rich type system supports more complex configuration needs as AWS services evolve

The business justification for cross-SDK implementation includes improved customer satisfaction through reduced configuration-related support requests, enhanced developer productivity through better tooling integration, and alignment with modern configuration management practices used by other cloud providers and development tools.

This enhancement maintains complete backward compatibility with existing INI files while providing a clear migration path for users who want to adopt the improved TOML format.

## Specification

### File Discovery and Precedence

SDKs MUST implement the following file discovery order when no environment variables are set:

1. Check for `~/.aws/config.toml` (platform-specific path resolution)
2. If TOML file exists and is valid, use it exclusively
3. If TOML file exists but contains invalid TOML syntax, fail with parse error
4. If TOML file does not exist, fall back to existing INI file discovery

SDKs MUST support the `AWS_CONFIG_FILE_TOML` environment variable to specify custom TOML file locations. When this environment variable is set:

- SDKs MUST use only the specified TOML file
- SDKs MUST NOT fall back to INI files if the TOML file is invalid or inaccessible
- SDKs MUST fail with a clear error message if the specified TOML file cannot be parsed

When both `AWS_CONFIG_FILE_TOML` and INI environment variables (`AWS_CONFIG_FILE`, `AWS_SHARED_CREDENTIALS_FILE`) are set:

- SDKs MUST log a warning message indicating both environment variable types are set
- SDKs MUST use the TOML file exclusively
- SDKs MUST ignore the INI environment variables

### TOML File Structure

The TOML configuration file MUST use the following top-level section structure:

- `[profile.*]` sections for profile configurations
- `[sso-session.*]` sections for SSO session configurations  
- `[services.*]` sections for service-specific configurations

The default profile MUST be represented as `[profile.default]` and MUST NOT receive special handling different from other profiles.

Example structure:
```toml
[profile.default]
region = "us-east-1"
use_dualstack_endpoint = true

[profile.dev]
region = "us-west-2"
aws_access_key_id = "AKIAIOSFODNN7EXAMPLE"
aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

[profile.assume-role-example]
role_arn = "arn:aws:iam::123456789012:role/ExampleRole"
source_profile = "dev"
duration_seconds = 3600

[sso-session.my-sso]
sso_start_url = "https://my-sso-portal.awsapps.com/start"
sso_region = "us-east-1"

[services.s3]
endpoint_url = "https://s3.us-west-2.amazonaws.com"
```

### Data Type Requirements

TOML files MUST use native data types for the following properties:

**Boolean Properties** (native boolean `true`/`false`):
- `use_dualstack_endpoint`
- `use_fips_endpoint`
- `aws_endpoint_discovery_enabled`
- `s3_disable_express_session_auth`
- `ec2_metadata_v1_disabled`
- `disable_request_compression`

**Numeric Properties** (native integer):
- `duration_seconds`
- `metadata_service_timeout`
- `request_min_compression_size_bytes`

**Array Properties** (native TOML array):
- `sigv4a_signing_region_set`

All other properties MUST use string values to maintain compatibility with existing configuration processing.

### TOML Configuration Examples

The following examples demonstrate TOML configuration syntax for common AWS SDK configuration scenarios.

#### Basic Profile Configuration
```toml
[profile.default]
region = "us-east-1"
output = "json"
use_dualstack_endpoint = true  # Native boolean
use_fips_endpoint = false
```

#### Profile with Credentials and Role Assumption
```toml
[profile.dev]
region = "us-west-2"
aws_access_key_id = "AKIAIOSFODNN7EXAMPLE"
aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

[profile.assume-role-example]
role_arn = "arn:aws:iam::123456789012:role/ExampleRole"
source_profile = "dev"
duration_seconds = 3600  # Native integer
```

#### Multi-Region Configuration with Native Array
```toml
[profile.multi-region]
sigv4a_signing_region_set = ["us-east-1", "us-west-2", "eu-west-1"]  # Native array
```

#### SSO Configuration
```toml
[profile.sso-user]
region = "us-east-1"
sso_session = "my-company-sso"
sso_account_id = "123456789012"
sso_role_name = "DeveloperRole"

[sso-session.my-company-sso]
sso_start_url = "https://my-company.awsapps.com/start"
sso_region = "us-east-1"
sso_registration_scopes = ["sso:account:access"]
```

#### Service-Specific Configuration
```toml
[services.s3]
endpoint_url = "https://s3.us-west-2.amazonaws.com"

[services.dynamodb]
endpoint_url = "https://dynamodb.us-east-1.amazonaws.com"
```

### Service Configuration

The legacy `s3` sub-property syntax used in INI profile sections is NOT supported in TOML format. Users MUST use the `[services.s3]` section for S3-specific configuration:

```toml
# INI format (not supported in TOML)
[profile example]
s3 =
  endpoint_url = https://s3.us-west-2.amazonaws.com

# TOML format (required)
[services.s3]
endpoint_url = "https://s3.us-west-2.amazonaws.com"
```

### Error Handling Requirements

SDKs MUST implement strict TOML parsing with the following error handling behavior:

- Invalid TOML syntax MUST result in immediate parse failure with no recovery attempts
- SDKs MUST NOT fall back to INI file parsing when TOML parsing fails
- Parse errors MUST include file path, line number (when available), and specific error details
- Unknown configuration properties MUST be ignored silently
- Invalid data type values MUST cause parsing to fail with clear error messages indicating expected types

### Edge Case Handling

SDKs MUST handle the following edge cases:

- **Empty TOML files**: MUST be treated as valid with no configuration properties
- **Missing files**: When `AWS_CONFIG_FILE_TOML` is not set and `~/.aws/config.toml` does not exist, MUST fall back to INI discovery
- **Empty string values**: Properties with empty string values (`property = ""`) MUST be treated as valid empty strings
- **Missing property values**: Properties without values (e.g., `property =`) MUST cause TOML parsing to fail
- **Case sensitivity**: TOML property names are case-sensitive and MUST be matched exactly as specified
- **File permissions**: If TOML file exists but is not readable, MUST fail with permission error rather than falling back to INI

### Cross-SDK Consistency Requirements

SDKs MUST use only core TOML v1.0.0 specification features. SDKs MUST NOT use:
- TOML extensions or non-standard features
- Language-specific TOML library extensions
- Custom parsing behavior beyond the TOML specification

### Platform-Specific Requirements

SDKs MUST resolve the default TOML file location using platform-specific paths:

- **Linux/macOS**: `~/.aws/config.toml`
- **Windows**: `%USERPROFILE%\.aws\config.toml`

Home directory resolution MUST follow the same precedence as existing INI files:
1. `HOME` environment variable (all platforms)
2. `USERPROFILE` environment variable (Windows)
3. `HOMEDRIVE` + `HOMEPATH` concatenation (Windows)
4. SDK-specific home directory resolution (optional)

### Backward Compatibility Requirements

SDKs MUST maintain complete backward compatibility with existing INI file functionality:

- Existing INI files MUST continue to work without modification
- Existing environment variables MUST continue to function as before
- Existing configuration APIs MUST remain unchanged
- SDK behavior MUST be identical when using INI files versus equivalent TOML files

TOML support MUST be implemented as a purely additive feature with no breaking changes to existing functionality.

## Feature ID

This feature will NOT be tracked for business metrics. The rationale for not tracking TOML configuration support is as follows:

1. **Configuration Format vs. Runtime Behavior**: TOML support is a configuration file format enhancement that affects how configuration is loaded at SDK initialization time, not how individual service operations are executed. Business metrics are designed to track runtime operation characteristics rather than configuration loading mechanisms.

2. **No Wire Protocol Impact**: Unlike features such as retry modes, request compression, or signing algorithms that affect the actual HTTP requests sent to AWS services, TOML configuration parsing occurs entirely within the SDK before any service calls are made. The resulting configuration values are identical whether loaded from INI or TOML format.

3. **Implementation Detail**: The choice between INI and TOML configuration formats is an implementation detail of how users provide configuration to SDKs, similar to how environment variables or programmatic configuration are not tracked. The business value is in the configuration values themselves, not the format used to specify them.

4. **Measurement Complexity**: Tracking TOML usage would require adding metrics collection to configuration loading code paths that currently have no business metrics instrumentation. This would add complexity without providing actionable business insights, as the format choice doesn't correlate with service usage patterns or customer success metrics.

5. **Privacy Considerations**: Configuration file format choice is a local development environment decision that doesn't need to be reported to AWS services for business intelligence purposes.

The focus of business metrics should remain on features that directly impact service interactions, performance characteristics, and customer experience with AWS APIs rather than local configuration management preferences.

## Test Cases

Two complementary test suites are provided in JSON format to ensure consistent TOML configuration implementation across all SDK languages.

### Primary Test Suite: [toml-configuration-test-cases.json](toml-configuration-test-cases.json)

This suite verifies TOML-specific functionality. Each test case follows this structure:

```json
{
  "name": "Descriptive test name",
  "input": {
    "tomlFile": "TOML file content",
    "environmentVariables": { "AWS_CONFIG_FILE_TOML": "/path" },
    "configFile": "Optional INI config for precedence tests",
    "credentialsFile": "Optional INI credentials for precedence tests"
  },
  "output": {
    "profiles": { "expected": "parsed structure" },
    "ssoSessions": { "expected": "parsed structure" },
    "services": { "expected": "parsed structure" },
    "warnings": ["Expected warning messages"],
    "errorContaining": "Expected error message substring"
  }
}
```

### Equivalence Test Suite: [toml-ini-equivalence-tests.json](toml-ini-equivalence-tests.json)

This suite verifies INI and TOML configurations produce identical parsed results. Each test case follows this structure:

```json
{
  "name": "Equivalence test description",
  "iniInput": {
    "configFile": "INI config file content",
    "credentialsFile": "INI credentials file content"
  },
  "tomlInput": {
    "tomlFile": "Equivalent TOML file content"
  },
  "expectedOutput": {
    "profiles": { "identical": "parsed structure" },
    "ssoSessions": { "identical": "parsed structure" },
    "services": { "identical": "parsed structure" }
  }
}
```

### Test Runner Implementation Requirements

SDKs MUST implement test runners that:

1. **Parse Test Input**: Load TOML files, set environment variables, and optionally load INI files as specified in each test case
2. **Execute Configuration Loading**: Use the SDK's standard configuration loading mechanism with the test inputs
3. **Validate Output Structure**: Compare the parsed configuration against the expected output structure
4. **Verify Error Conditions**: For tests with `errorContaining`, ensure the expected error occurs and contains the specified message substring
5. **Check Warnings**: For tests with `warnings`, verify the expected warning messages are logged
6. **Assert Equivalence**: For equivalence tests, verify that both INI and TOML inputs produce identical parsed configuration structures

### Cross-SDK Consistency Requirements

Test implementations MUST:
- Use the SDK's production configuration loading code paths (not test-specific parsers)
- Handle environment variable simulation consistently across platforms
- Normalize file path separators for cross-platform compatibility
- Validate that error messages contain the required substrings (exact message format may vary by language)
- Ensure warning message detection works with the SDK's logging framework

The test suites are designed to be language-agnostic. SDK teams should implement test runners in their preferred testing framework while maintaining the input/output contracts specified in the JSON files.

## Alternatives

The following alternatives were considered during the design process but were not chosen for the reasons outlined below.

### Alternative 1: Separate TOML Files for Config and Credentials

**Approach**: Use separate `config.toml` and `credentials.toml` files, mirroring the current INI file structure.

**Rationale for Rejection**: This approach would require users to manage two separate TOML files and would not take full advantage of TOML's structural capabilities. The single file approach leverages TOML's native section organization to provide a cleaner, more unified configuration experience. Additionally, maintaining separate files would complicate the file discovery logic and environment variable handling without providing meaningful benefits.

### Alternative 2: Different File Naming Convention

**Approach**: Use alternative naming schemes such as `aws-config.toml`, `aws.toml`, or `config.aws.toml`.

**Rationale for Rejection**: The `config.toml` naming convention was chosen for consistency with the existing `config` file pattern and to clearly indicate the relationship between INI and TOML formats. Alternative naming schemes would be less intuitive for users familiar with the current configuration system and could create confusion about which file takes precedence.

### Alternative 3: Different Environment Variable Naming

**Approach**: Use environment variables like `AWS_TOML_CONFIG_FILE`, `AWS_CONFIG_TOML`, or `AWS_TOML_FILE`.

**Rationale for Rejection**: The `AWS_CONFIG_FILE_TOML` naming convention was chosen to clearly parallel the existing `AWS_CONFIG_FILE` variable while making the TOML format explicit. This naming pattern is more descriptive and follows the established AWS environment variable naming conventions.

### Alternative 4: INI Takes Precedence Over TOML

**Approach**: When both INI and TOML files exist, prioritize INI files to maintain backward compatibility.

**Rationale for Rejection**: This approach would discourage adoption of the improved TOML format and would not provide users with a clear migration path. Having TOML take precedence encourages users to adopt the better format while still maintaining full backward compatibility for users who haven't migrated yet.

### Alternative 5: TOML Extensions and Custom Features

**Approach**: Use TOML extensions or custom parsing features to provide additional functionality beyond the core TOML v1.0.0 specification.

**Rationale for Rejection**: Using only core TOML specification features ensures maximum compatibility across different TOML parser libraries and programming languages. Custom extensions would create implementation complexity, reduce portability, and potentially cause inconsistencies between SDK languages. The core TOML specification provides all necessary features for AWS configuration needs.

### Alternative 6: Gradual Data Type Migration

**Approach**: Initially support only string values in TOML format, then gradually introduce native data types in future versions.

**Rationale for Rejection**: This approach would not provide the immediate benefits of native data types that motivate TOML adoption. Users would not see clear advantages over INI format, reducing adoption incentives. Implementing native data types from the beginning provides immediate value and avoids the complexity of managing multiple TOML format versions.

### Alternative 7: Automatic INI-to-TOML Conversion

**Approach**: Provide built-in SDK functionality to automatically convert existing INI files to TOML format.

**Rationale for Rejection**: Automatic conversion functionality was deemed out of scope for this SEP as it represents tooling rather than core SDK functionality. Users can adopt TOML format at their own pace without requiring conversion utilities. Third-party tools or separate utilities can provide conversion functionality if needed.

## Frequently Asked Questions (FAQ)

### Why was TOML chosen over other configuration formats like YAML or JSON?

TOML was selected because it provides the best balance of human readability, native data type support, and parsing simplicity for configuration files. Unlike YAML, TOML has unambiguous syntax that reduces configuration errors. Unlike JSON, TOML supports comments and is more readable for configuration purposes. TOML's design philosophy aligns well with AWS configuration needs: obvious, minimal, and easy to parse.

### How does the transition from INI to TOML work for existing users?

The transition is entirely optional and gradual. Existing INI files continue to work without any changes. Users can create a `config.toml` file alongside their existing INI files, and the TOML file will take precedence. This allows users to migrate at their own pace and test TOML configuration without risk of breaking existing setups.

### Are there any platform-specific differences in TOML file handling?

TOML file discovery follows the same platform-specific patterns as existing INI files. The default location is `~/.aws/config.toml` on Linux/macOS and `%USERPROFILE%\.aws\config.toml` on Windows. Home directory resolution uses the same environment variable precedence as INI files. TOML parsing itself is platform-agnostic and follows the TOML v1.0.0 specification consistently across all platforms.

### What happens if I have both TOML and INI environment variables set?

When both `AWS_CONFIG_FILE_TOML` and INI environment variables (`AWS_CONFIG_FILE`, `AWS_SHARED_CREDENTIALS_FILE`) are set, the SDK will log a warning message and use the TOML file exclusively. The INI environment variables will be ignored. This ensures predictable behavior while alerting users to the potential configuration conflict.

### Why does TOML parsing fail strictly without falling back to INI?

Strict parsing ensures that TOML configuration errors are caught immediately rather than silently falling back to potentially outdated INI configuration. This prevents subtle configuration issues where users expect TOML settings to be active but INI settings are actually being used due to TOML parsing failures. Clear error messages help users fix TOML syntax issues quickly.

### How are unknown configuration properties handled in TOML files?

Unknown properties in TOML files are ignored silently, following the same pattern as INI files. This allows for forward compatibility when new configuration properties are added and prevents configuration loading from failing due to properties that might be valid in newer SDK versions.

### Will INI format support be deprecated or removed in the future?

There are no current plans to deprecate or remove INI format support. TOML support is designed as an additive enhancement that provides benefits for users who want them while maintaining full backward compatibility for users who prefer to continue using INI format.

### Can I mix INI and TOML files in the same configuration setup?

When no environment variables are set, SDKs will use TOML files if present, otherwise fall back to INI files. You cannot mix formats within a single configuration loading operation - either TOML takes precedence entirely, or INI files are used entirely. This ensures consistent behavior and prevents configuration conflicts between formats.

### How do I migrate complex INI configurations with sub-properties to TOML?

The legacy `s3` sub-property syntax used in INI files is not supported in TOML format. Instead, use the `[services.s3]` section for S3-specific configuration. This provides cleaner organization and takes advantage of TOML's native section structure. The equivalence test suite provides examples of how various INI configurations map to TOML format.

### Are there performance implications of using TOML vs INI format?

TOML parsing may have slightly different performance characteristics than INI parsing, but the impact is minimal since configuration loading occurs infrequently (typically only at SDK initialization). The benefits of native data types and improved structure generally outweigh any minor performance differences. Configuration loading performance is not a significant factor in overall application performance.

## Revisions

| Revision # | Date       | Change                      | Author                                     |
| ---------- | ---------- | --------------------------- | ------------------------------------------ |
| 1          | 2025-08-08 | Initial revision of this SEP. | millem@ |
