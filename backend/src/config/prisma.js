/**
 * Centralized Prisma Client Configuration
 * File: backend/src/config/prisma.js
 * 
 * Provides a singleton PrismaClient instance across the application lifecycle.
 * Prevents multiple active client pools during development/restarts and exposes
 * diagnostic health-check and graceful disconnection routines.
 */

import { PrismaClient } from '@prisma/client';
import dotenv from 'dotenv';

dotenv.config();

const isDevelopment = process.env.NODE_ENV !== 'production';

// Configure development logging levels
const prismaClientOptions = {
  log: isDevelopment
    ? [
        { emit: 'stdout', level: 'warn' },
        { emit: 'stdout', level: 'error' },
      ]
    : [{ emit: 'stdout', level: 'error' }],
};

// Global singleton pattern to prevent connection pool exhaustion in development
const globalForPrisma = globalThis;

export const prisma = globalForPrisma.prisma ?? new PrismaClient(prismaClientOptions);

if (isDevelopment) {
  globalForPrisma.prisma = prisma;
}

/**
 * Validates active connectivity to the PostgreSQL database.
 * Returns an object with connection status, latency, or diagnostic error.
 * 
 * @param {number} timeoutMs - Max wait time before timing out (default 3000ms)
 * @returns {Promise<{ isConnected: boolean, latencyMs?: number, error?: string }>}
 */
export async function checkDatabaseConnection(timeoutMs = 3000) {
  const startTime = Date.now();
  try {
    // Probe database using a simple SELECT 1 query
    const probePromise = prisma.$queryRaw`SELECT 1 as connected;`;
    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error(`Connection probe timed out after ${timeoutMs}ms`)), timeoutMs)
    );

    await Promise.race([probePromise, timeoutPromise]);
    const latencyMs = Date.now() - startTime;
    return {
      isConnected: true,
      latencyMs,
    };
  } catch (err) {
    return {
      isConnected: false,
      error: err.message,
    };
  }
}

/**
 * Disconnects the Prisma client cleanly during application shutdown.
 */
export async function disconnectDatabase() {
  try {
    await prisma.$disconnect();
    console.log('[Database] Prisma client successfully disconnected.');
  } catch (err) {
    console.error(`[Database] Error disconnecting Prisma client: ${err.message}`);
  }
}

export default prisma;
