## Problem Description

The SDK currently has no API versioning strategy:
- API version is hardcoded in the base URL (`/api/v2`)
- No way to configure or change API version
- No strategy for handling future API version changes
- No documentation on versioning approach
- No backward compatibility considerations documented

## Proposed Solution

1. Make API version configurable via:
   - Client constructor parameter `api_version` (default: "v2")
   - Environment variable `SIDESHIFT_API_VERSION`
   - SDKConfig helper method
2. Add API versioning documentation explaining:
   - Current supported versions
   - Version selection strategy
   - Backward compatibility policy
   - Migration path for version changes
3. Add version validation to ensure only supported versions are used
4. Update base URL construction to use configurable version

