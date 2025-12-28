# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

Please report (suspected) security vulnerabilities to **[security@sideshift.ai](mailto:security@sideshift.ai)**. You will receive a response within 48 hours. If the issue is confirmed, we will release a patch as soon as possible depending on complexity but historically within a few days.

## Security Best Practices

When using the SideShift SDK:

1. **Never commit secrets**: Do not commit API keys, secrets, or credentials to version control
2. **Use environment variables**: Store sensitive information in environment variables
3. **Validate inputs**: Always validate user inputs before making API calls
4. **Handle errors securely**: Don't expose sensitive information in error messages
5. **Keep dependencies updated**: Regularly update the SDK and dependencies to receive security patches
6. **Use HTTPS**: Always use HTTPS when making API requests (enforced by the SDK)

## Known Security Considerations

- The SDK requires your SideShift secret key for authenticated requests. This key grants full access to your account.
- Never share your secret key or commit it to version control.
- Use environment variables or secure secret management systems to store credentials.
- The SDK automatically uses HTTPS for all API requests.

## Disclosure Policy

When security researchers follow the guidelines below when reporting security vulnerabilities, we commit to:

- Responding in a timely manner (within 48 hours)
- Keeping the researcher updated throughout the process
- Recognizing the researcher's contribution (if desired) after the vulnerability is resolved

## Guidelines for Security Researchers

- Provide detailed information about the vulnerability
- Include steps to reproduce the issue
- Do not access or modify user data without permission
- Do not perform any actions that could harm users or the service
- Do not disclose the vulnerability publicly until it has been resolved

