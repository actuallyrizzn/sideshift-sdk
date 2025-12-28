# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive examples for all SDK endpoints
- Docstring examples for key API functions
- Type aliases for commonly used types (JsonDict, HeadersDict, ResponseData)
- Constants module to replace magic strings
- Python version check in `__init__.py`
- Request/response hooks example
- `__all__` exports in endpoints module

### Changed
- Code style standardized with black formatter
- Removed unused imports (BaseModel, Any)

### Fixed
- Unused exception variables in exception handlers
- Code style inconsistencies across codebase

## [0.1.0] - 2024-01-01

### Added
- Initial release
- SideShiftClient for synchronous API calls
- AsyncSideShiftClient for asynchronous API calls
- Full coverage of SideShift.ai REST API V2 endpoints
- Pydantic models for all request/response types
- Automatic rate limit handling with exponential backoff
- Type hints throughout codebase
- Comprehensive error handling with custom exceptions

[Unreleased]: https://github.com/actuallyrizzn/sideshift-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/actuallyrizzn/sideshift-sdk/releases/tag/v0.1.0

