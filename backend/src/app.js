import express from 'express';
import cors from 'cors';
import { checkDatabaseConnection } from './config/prisma.js';

/**
 * Express Application Configuration
 * Configures global middlewares, health checks, and centralized error handling.
 * Specific domain routes will be registered in future implementation phases.
 */
const app = express();

// Environment-based CORS Configuration
const allowedOrigin = process.env.FRONTEND_URL || 'http://localhost:5173';
app.use(cors({
  origin: allowedOrigin,
  credentials: true,
}));

// Body Parsing Middlewares
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health Check Endpoint
app.get('/health', async (req, res) => {
  const dbCheck = await checkDatabaseConnection(1000);
  res.status(200).json({
    status: 'healthy',
    service: 'backend',
    database: {
      connected: dbCheck.isConnected,
      latencyMs: dbCheck.latencyMs ?? null,
      message: dbCheck.isConnected ? 'PostgreSQL operational' : 'PostgreSQL currently unreachable',
    },
    timestamp: new Date().toISOString(),
  });
});

// Root API Welcome Endpoint
app.get('/api', (req, res) => {
  res.status(200).json({
    message: 'Welcome to Adaptive Study Planner API',
    version: '0.1.0',
    phase: 'Phase 6 - Database Architecture & Persistence',
  });
});

// 404 Handler for Unmatched Routes
app.use((req, res, next) => {
  res.status(404).json({
    error: {
      message: `Endpoint ${req.method} ${req.originalUrl} not found.`,
      status: 404,
    },
  });
});

// Centralized Error Handling Middleware
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  res.status(statusCode).json({
    error: {
      message: err.message || 'Internal Server Error',
      status: statusCode,
      timestamp: new Date().toISOString(),
    },
  });
});

export default app;
