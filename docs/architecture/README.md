# System Architecture Documentation

This directory details the architectural decisions and system interactions of the Adaptive Study Planner.

## High-Level Topology

```text
[ React + Vite Client (Port 3000) ]
               │
               │ HTTP / JSON
               ▼
   [ Express.js API Gateway (Port 5000) ]
         │                     │
         │ Database Queries    │ HTTP Service-to-Service
         ▼                     ▼
[ PostgreSQL + Prisma ]  [ FastAPI ML Service (Port 8000) ]
                               │
                               ▼
                       [ BKT / Rec Engine ]
```

## Architectural Layers
- **Frontend:** Modular UI separated into reusable primitives, domain components, and routing pages.
- **Backend:** Layered architecture (Routes -> Controllers -> Services -> Repositories -> Prisma).
- **ML Service:** Independent microservice isolated from web application business logic.
