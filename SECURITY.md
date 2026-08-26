# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x | Yes |
| < 1.0 | No |

---

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly by contacting:

**Contact:** [pragnaramesh10@gmail.com](mailto:pragnaramesh10@gmail.com)

Please do not report security vulnerabilities through public GitHub issues.

Please include:

- Description of the issue
- Steps to reproduce
- Potential impact
- Suggested remediation (if known)

Acknowledgement will be provided as soon as possible.

---

## Responsible Disclosure

We ask that you:

- Give us reasonable time to investigate and remediate before public disclosure
- Avoid accessing, modifying, or deleting data belonging to others
- Do not perform denial-of-service attacks or automated scanning against production systems without permission

We will credit researchers who report valid issues (with permission) in release notes.

---

## Known Security Considerations

This project is designed for **portfolio, educational, and demonstration use**. The following are documented known risks:

| Area | Risk | Mitigation |
|------|------|------------|
| ML models | Pickle deserialization (`joblib.load`) | Path allowlisting; migrate to ONNX/skops planned |
| Authentication | `AUTH_REQUIRED=false` by default in local dev | Set `AUTH_REQUIRED=true` for any public deployment |
| Secrets | Default JWT secret and admin password | Rotate via `.env` before production |
| Ingestion | `POST /log` is intentionally public | Add reverse-proxy rate limiting in production |
| CORS | Defaults to permissive in dev | Restrict `CORS_ORIGINS` in production |

See [docs/final_release_audit.md](docs/final_release_audit.md) for the full security audit.

---

## Security Best Practices for Deployers

1. Set `AUTH_REQUIRED=true`
2. Generate a strong JWT secret: `openssl rand -hex 32`
3. Change default admin and demo passwords
4. Terminate TLS at a reverse proxy (nginx, Caddy)
5. Do not commit `.env` files or `*.db` databases
6. Restrict network access to the ingestion endpoint if possible

---

## Security Updates

Security-related fixes are documented in [CHANGELOG.md](CHANGELOG.md) with clear version tags.
