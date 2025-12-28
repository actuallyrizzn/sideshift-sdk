# API Versioning Strategy

This document outlines the API versioning strategy for the SideShift SDK.

## Overview

The SideShift SDK supports configurable API versions to allow flexibility when the SideShift.ai API introduces new versions or deprecates old ones.

## Supported Versions

Currently supported API versions:
- **v2** (default, recommended) - Current production API

## Version Configuration

### Client Constructor

You can specify the API version when creating a client:

```python
from sideshift_sdk import SideShiftClient

# Use default v2 API
client = SideShiftClient(secret="...")

# Explicitly specify v2 API
client = SideShiftClient(secret="...", api_version="v2")

# Use custom base URL (takes precedence over api_version)
client = SideShiftClient(secret="...", base_url="https://sideshift.ai/api/v2")
```

### Environment Variable

You can also set the API version via environment variable:

```bash
export SIDESHIFT_API_VERSION=v2
```

### Version Validation

The SDK validates that only supported API versions are used. If an unsupported version is specified, a `ValueError` is raised:

```python
# This will raise ValueError
client = SideShiftClient(secret="...", api_version="v1")  # v1 is not supported
```

## Version Selection Priority

The SDK uses the following priority order for determining the base URL:

1. **Explicit `base_url` parameter** (highest priority)
2. **`SIDESHIFT_BASE_URL` environment variable**
3. **`api_version` parameter** (constructs URL from version)
4. **`SIDESHIFT_API_VERSION` environment variable** (constructs URL from version)
5. **Default v2 API** (lowest priority)

## Backward Compatibility

### SDK Versioning

The SDK follows [Semantic Versioning](https://semver.org/):
- **Major version** (X.0.0): Breaking changes
- **Minor version** (0.X.0): New features, backward compatible
- **Patch version** (0.0.X): Bug fixes, backward compatible

### API Version Support

- The SDK will support multiple API versions when necessary
- When a new API version is released, the SDK will be updated to support it
- Old API versions will be deprecated with advance notice
- Deprecated versions will be removed in a future major SDK version

## Migration Strategy

### When a New API Version is Released

1. **SDK Update**: The SDK will be updated to support the new version
2. **Documentation**: Migration guides will be provided
3. **Deprecation Notice**: Old versions will be marked as deprecated
4. **Transition Period**: Both versions will be supported during the transition
5. **Removal**: Deprecated versions will be removed in a future major SDK version

### Example Migration

```python
# Before: Using v2 (default)
client = SideShiftClient(secret="...")

# After: Explicitly using v2 (recommended for clarity)
client = SideShiftClient(secret="...", api_version="v2")

# Future: When v3 is released
client = SideShiftClient(secret="...", api_version="v3")
```

## Best Practices

1. **Explicit Version**: Always specify the API version explicitly in production code
2. **Environment Variables**: Use environment variables for configuration management
3. **Version Pinning**: Pin your SDK version in requirements.txt to ensure compatibility
4. **Testing**: Test your application when upgrading SDK versions
5. **Monitoring**: Monitor for deprecation notices and migration guides

## Version History

| SDK Version | Supported API Versions | Notes |
|-------------|------------------------|-------|
| 0.1.0+      | v2                     | Initial release, v2 only |

## Future Considerations

- When v3 API is released, the SDK will support both v2 and v3
- Migration tools may be provided to help transition between versions
- Version-specific features will be clearly documented

