# Existing Botocore Configuration Architecture Research

## Overview

Research into the current botocore configuration system to understand how configuration files are loaded, parsed, and used throughout the SDK. This research informs the TOML configuration implementation design.

## Key Configuration Components Identified

From the codebase overview, the following key configuration-related components were found:

### Core Configuration Classes
- `ConfigValueStore` - Manages configuration values
- `Config` - Main configuration class
- `ConfigProvider` - Base provider for configuration values
- `DefaultConfigResolver` - Resolves default configuration values
- `ConfigChainFactory` - Creates configuration provider chains

### Configuration Providers
- `ChainProvider` - Chains multiple providers
- `InstanceVarProvider` - Instance variable provider
- `ScopedConfigProvider` - Scoped configuration provider
- `EnvironmentProvider` - Environment variable provider
- `SectionConfigProvider` - Section-based configuration provider
- `ConstantProvider` - Constant value provider

### Session and Client Integration
- `Session` - Main session class that manages configuration
- `ClientArgsCreator` - Creates client arguments from configuration
- `BaseClient` - Base client that uses configuration

## Current Session.full_config Implementation

The current `full_config` property in `Session` class works as follows:

```python
@property
def full_config(self):
    """Return the parsed config file.

    The ``get_config`` method returns the config associated with the
    specified profile.  This property returns the contents of the
    **entire** config file.

    :rtype: dict
    """
    if self._config is None:
        try:
            config_file = self.get_config_variable('config_file')
            self._config = botocore.configloader.load_config(config_file)
        except ConfigNotFound:
            self._config = {'profiles': {}}
        try:
            # Now we need to inject the profiles from the
            # credentials file.  We don't actually need the values
            # in the creds file, only the profile names so that we
            # can validate the user is not referring to a nonexistent
            # profile.
            cred_file = self.get_config_variable('credentials_file')
            cred_profiles = botocore.configloader.raw_config_parse(
                cred_file
            )
            for profile in cred_profiles:
                cred_vars = cred_profiles[profile]
                if profile not in self._config['profiles']:
                    self._config['profiles'][profile] = cred_vars
                else:
                    self._config['profiles'][profile].update(cred_vars)
        except ConfigNotFound:
            pass
    return self._config
```

### Key Insights for TOML Implementation

1. **File Discovery**: Uses `self.get_config_variable('config_file')` to get the config file path
2. **Loading**: Calls `botocore.configloader.load_config(config_file)` to parse the file
3. **Caching**: Results are cached in `self._config`
4. **Credentials Merging**: Merges credentials file profiles into the config
5. **Error Handling**: Gracefully handles `ConfigNotFound` exceptions
6. **Structure**: Returns a dict with `{'profiles': {}}` structure

### TOML Integration Points

Based on the requirements clarification, the TOML implementation should:

1. **Integrate directly into `full_config` property** - Modify this property to check for TOML files first
2. **Use same path resolver** - Leverage existing `get_config_variable()` mechanism
3. **Use same caching behavior** - Maintain the `self._config` caching pattern
4. **Log warnings** - Add warning when both TOML and INI environment variables are set
5. **Fail fast** - Implement strict error handling as specified

## Next Steps

1. Examine `botocore.configloader.load_config()` implementation
2. Investigate the `get_config_variable()` mechanism for adding `config_file_toml`
3. Understand the provider chain architecture
4. Analyze data type handling in current configuration system
