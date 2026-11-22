# API Specification & Contracts

This directory documents the API contracts between the client, backend, and ML service.

## Planned Endpoints Overview

### Backend API (Express.js)
- `/health` - Service health status
- `/api/auth/*` - Student authentication (future phase)
- `/api/subjects/*` - Subject catalog
- `/api/topics/*` - Topic catalog and prerequisite information
- `/api/quizzes/*` - Question delivery and attempt submission
- `/api/recommendations/*` - Personalized study schedule retrieval

### ML Service API (FastAPI)
- `/health` - ML service health check
- `/api/v1/mastery/estimate` - Estimate topic mastery probability using BKT
- `/api/v1/recommendation/next` - Generate adaptive topic recommendation based on mastery and prerequisites
