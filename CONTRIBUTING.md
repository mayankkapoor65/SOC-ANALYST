# Contributing to SentinelAI

Thank you for your interest in contributing to **Security Log Anomaly Detection (SentinelAI)**. This document covers setup, standards, and the pull request process.

---

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/Security-Log-Anomaly-Detection.git
cd Security-Log-Anomaly-Detection

# Backend
pip install -r requirements.txt
cp .env.example .env
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Frontend (separate terminal)
cd frontend
npm install
cp .env.example .env
npm start

# Optional: generate demo data
python3 log_generator.py
```

### Running Tests

```bash
# Backend (38 tests)
python3 -m unittest discover -s tests -v

# Frontend
cd frontend && npm test -- --watchAll=false
```

---

## Coding Standards

### Python (Backend)

- Follow PEP 8 style
- Use type hints where practical
- Parameterized SQL queries only — never interpolate user input into SQL
- Structured logging via `logging.getLogger(__name__)`
- New endpoints must include RBAC permissions when `AUTH_REQUIRED=true`
- Do not break backward compatibility on `POST /log` response fields

### JavaScript (Frontend)

- Functional React components with hooks
- Keep API calls in `AuthContext` / `useDashboardData`
- Match existing SentinelAI CSS conventions in `frontend/src/styles/sentinel.css`
- Role-based UI gating via `canAccessView()`

### Documentation

- Update `README.md` for user-facing changes
- Add phase docs under `docs/` for significant features
- Update `CHANGELOG.md` under `[Unreleased]` or new version section

---

## Pull Request Process

1. **Fork** the repository and create a feature branch from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes** with focused commits — one logical change per commit when possible

3. **Test** — ensure all unit tests pass before submitting

4. **Document** — update README, CHANGELOG, or docs as appropriate

5. **Open a Pull Request** with:
   - Clear title describing the change
   - Summary of what and why
   - Test plan (commands run, results)
   - Screenshots for UI changes

6. **Review** — address feedback; maintain backward compatibility unless explicitly discussed

---

## Scope Guidelines

| Change Type | Guidance |
|-------------|----------|
| Bug fixes | Welcome — include regression test when feasible |
| Documentation | Always welcome |
| New detection rules | Discuss in issue first; include validation report |
| API breaking changes | Require major version bump and migration notes |
| Security fixes | See [SECURITY.md](SECURITY.md) — do not open public issues for vulnerabilities |

---

## Demo Accounts

When testing auth changes, use seeded demo accounts:

| Role | Username | Password |
|------|----------|----------|
| ADMIN | admin | Admin123! |
| ANALYST | analyst1 | Analyst123! |
| VIEWER | viewer1 | Viewer123! |

---

## Questions?

Open a GitHub Issue with the `question` label or refer to [docs/architecture.md](docs/architecture.md).
