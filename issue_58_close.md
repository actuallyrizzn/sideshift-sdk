## ✅ Issue #58 Resolved

This issue has been successfully implemented and tested.

### Solution Summary

Implemented a comprehensive API versioning strategy for the SDK:

1. **API Version Configuration**
   - Added `api_version` parameter to both `SideShiftClient` and `AsyncSideShiftClient` constructors
   - Created `SDKConfig.get_api_version()` method with validation for supported versions
   - Added support for `SIDESHIFT_API_VERSION` environment variable

2. **Base URL Construction**
   - Implemented dynamic base URL construction from API version (e.g., "v2" → "https://sideshift.ai/api/v2")
   - Clear priority order: explicit `base_url` > `SIDESHIFT_BASE_URL` env var > `api_version` parameter > `SIDESHIFT_API_VERSION` env var > default v2

3. **Version Validation**
   - Added validation that raises clear `ValueError` for unsupported versions
   - Currently supports: v2 (default)

4. **Documentation**
   - Created comprehensive API versioning guide in `docs/API_VERSIONING.md`
   - Includes usage examples, migration strategy, and best practices

5. **Testing**
   - Added 13 new tests covering all versioning scenarios
   - All 203 tests pass ✅

### Ada's Review

> Acknowledged. Issue #58 is resolved:
> 
> - API versioning is now explicit and flexible via the api_version parameter, environment variable, and SDKConfig logic.
> - Base URL is constructed dynamically per version, with validation and clear error reporting for unsupported versions.
> - The explicit priority order for base URL and version selection is documented and enforced.
> - Backward compatibility is maintained (default remains v2 if unspecified).
> - Comprehensive documentation (docs/API_VERSIONING.md) and 13 new tests verify all versioning scenarios.
> - All 203 tests pass.
> 
> Standing directives:
> - Maintain strict validation for supported API versions; update documentation and validation logic as SideShift API versions change.
> - Ensure versioning changes are reflected in user documentation and changelogs.
> - Monitor for user or integration partner feedback regarding version migration or deprecation.
> 
> No further action required unless SideShift API releases a new version or versioning requirements change. Report if compatibility or migration issues arise.

### Commit

Commit: `d82d7bee2d1976c9921b46393d91972fab594e64`

