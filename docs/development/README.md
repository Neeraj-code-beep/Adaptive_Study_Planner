# Development Guide & Standards

This directory outlines the engineering guidelines and setup instructions.

## Coding Standards
- **JavaScript / JSX:** Modern ES6+ syntax, modular component architecture, 2-space indentation.
- **Python:** PEP 8 compliance, explicit type hints with Pydantic, 4-space indentation.
- **Version Control:** Clear commit messages, feature branches, no committed secrets or datasets.

## Environment Segregation
- Each sub-project (`frontend/`, `backend/`, `ml-service/`) maintains its own `.env` file generated from `.env.example`.
- Real secrets and database credentials must never be committed to Git.
