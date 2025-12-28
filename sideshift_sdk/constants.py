"""Constants for SideShift SDK."""

# API Configuration
API_BASE_DOMAIN = "https://sideshift.ai"
DEFAULT_API_VERSION = "v2"
BASE_URL = f"{API_BASE_DOMAIN}/api/{DEFAULT_API_VERSION}"

# Supported API versions
SUPPORTED_API_VERSIONS = ["v2"]

# HTTP Headers
HEADER_CONTENT_TYPE = "Content-Type"
HEADER_ACCEPT = "Accept"
HEADER_USER_AGENT = "User-Agent"
HEADER_SIDESHIFT_SECRET = "x-sideshift-secret"
HEADER_USER_IP = "x-user-ip"
HEADER_REQUEST_ID = "X-Request-ID"

# Content Types
CONTENT_TYPE_JSON = "application/json"

# Image Formats
IMAGE_FORMAT_SVG = "svg"
IMAGE_FORMAT_PNG = "png"
