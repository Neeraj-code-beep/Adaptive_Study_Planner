# Local Development Setup Guide (Windows)

This document provides the exact Windows PowerShell / Command Prompt instructions to initialize, run, and verify all three services of the **Adaptive Study Planner** monorepo.

---

## 1. Prerequisites

Ensure the following tools are installed and available in your `PATH`:
- **Node.js** (v18.0.0+ / v22.x recommended) - verify with `node --version`
- **npm** (v9.0.0+) - verify with `npm --version`
- **Python** (v3.10+ / v3.13 tested) - verify with `python --version`

*Note: PostgreSQL is our target database system for upcoming phases. A live database connection is not required to run the Phase 2 foundation services.*

---

## 2. Navigate to Project Root

Open a terminal (PowerShell or Command Prompt) and navigate to the project directory:

```powershell
Set-Location "N:\adaptive-study-planner"
```
*(Or your specific repository clone directory).*

---

## 3. Install Frontend Dependencies

```powershell
Set-Location "N:\adaptive-study-planner\frontend"
Copy-Item ".env.example" ".env"
npm install
```

To verify the production build:
```powershell
npm run build
```

---

## 4. Install Backend Dependencies

```powershell
Set-Location "N:\adaptive-study-planner\backend"
Copy-Item ".env.example" ".env"
npm install
```

---

## 5. Set Up Python Virtual Environment & Install ML Service Dependencies

```powershell
Set-Location "N:\adaptive-study-planner\ml-service"
Copy-Item ".env.example" ".env"

# Create isolated Python virtual environment
python -m venv .venv

# Activate the virtual environment in PowerShell
.\.venv\Scripts\Activate.ps1

# (Optional: If PowerShell script execution is restricted, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)

# Upgrade pip and install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 6. Running All Three Services (Separate Terminals)

To run the complete system locally, open three separate terminal windows:

### Terminal 1: Machine Learning Service (FastAPI)
```powershell
Set-Location "N:\adaptive-study-planner\ml-service"
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- **Service URL:** http://127.0.0.1:8000
- **Interactive API Documentation (Swagger UI):** http://127.0.0.1:8000/docs
- **Health Check Endpoint:** http://127.0.0.1:8000/health

### Terminal 2: Backend API (Express.js)
```powershell
Set-Location "N:\adaptive-study-planner\backend"
npm run dev
```
- **Service URL:** http://localhost:5000
- **Health Check Endpoint:** http://localhost:5000/health
- **Base API Endpoint:** http://localhost:5000/api

### Terminal 3: Frontend Client (React + Vite)
```powershell
Set-Location "N:\adaptive-study-planner\frontend"
npm run dev
```
- **Application URL:** http://localhost:5173

---

## 7. Verifying Endpoints with HTTP Requests

Open a fourth terminal to test the running services using PowerShell:

### Test Frontend:
```powershell
Invoke-WebRequest -Uri "http://localhost:5173" -Method Get
```
*Expected:* Status code `200 OK`, HTML containing `<title>Adaptive Study Planner</title>`.

### Test Backend Health:
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get
```
*Expected Output:*
```json
{
  "status": "healthy",
  "service": "backend",
  "timestamp": "2026-11-21T17:36:30.571Z"
}
```

### Test ML Service Health:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
```
*Expected Output:*
```json
{
  "status": "healthy",
  "service": "ml-service",
  "timestamp": "2026-11-21T17:20:14.880610+00:00"
}
```

### Test ML Service Swagger Docs:
```powershell
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/docs" -Method Get).StatusCode
```
*Expected Output:* `200`
