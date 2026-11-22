import dotenv from 'dotenv';
import app from './app.js';
import { checkDatabaseConnection, disconnectDatabase } from './config/prisma.js';

// Load environment variables from .env
dotenv.config();

const PORT = process.env.PORT || 5000;

const server = app.listen(PORT, async () => {
  console.log(`[Backend] Adaptive Study Planner server running on port ${PORT}`);
  console.log(`[Backend] Health check available at http://localhost:${PORT}/health`);

  // Non-blocking database connectivity check
  const dbStatus = await checkDatabaseConnection(2000);
  if (dbStatus.isConnected) {
    console.log(`[Backend] Database connection established (latency: ${dbStatus.latencyMs}ms)`);
  } else {
    console.warn(`[Backend] Database connection notice: PostgreSQL is currently unreachable (${dbStatus.error}). Application running with mock/in-memory fallback readiness.`);
  }
});

// Handle server startup errors
server.on('error', (err) => {
  console.error(`[Backend] Server error: ${err.message}`);
  process.exit(1);
});

// Graceful shutdown handling
const handleGracefulShutdown = async (signal) => {
  console.log(`[Backend] ${signal} signal received: closing HTTP server`);
  server.close(async () => {
    console.log('[Backend] HTTP server closed');
    await disconnectDatabase();
    process.exit(0);
  });
};

process.on('SIGTERM', () => handleGracefulShutdown('SIGTERM'));
process.on('SIGINT', () => handleGracefulShutdown('SIGINT'));
