/**
 * Integration Test for Express Application Server
 * File: backend/tests/integration/server.test.js
 */

import { test, describe, before, after } from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import app from '../../src/app.js';
import { disconnectDatabase } from '../../src/config/prisma.js';

describe('Express Server Integration & Health Endpoints', () => {
  let server;
  let testPort;

  before((_, done) => {
    // Bind to an ephemeral port for testing
    server = app.listen(0, () => {
      testPort = server.address().port;
      done();
    });
  });

  after((_, done) => {
    server.close(async () => {
      await disconnectDatabase();
      done();
    });
  });

  test('GET /health returns 200 with service and database diagnostic metadata', async () => {
    const response = await fetch(`http://localhost:${testPort}/health`);
    assert.strictEqual(response.status, 200);
    const body = await response.json();
    assert.strictEqual(body.status, 'healthy');
    assert.strictEqual(body.service, 'backend');
    assert.ok('database' in body, 'Health check should contain database status object');
    assert.strictEqual(typeof body.database.connected, 'boolean');
  });

  test('GET /api returns 200 with Phase 6 welcome message', async () => {
    const response = await fetch(`http://localhost:${testPort}/api`);
    assert.strictEqual(response.status, 200);
    const body = await response.json();
    assert.ok(body.message.includes('Adaptive Study Planner API'));
    assert.strictEqual(body.version, '0.1.0');
  });

  test('GET /unknown-route returns 404 error envelope', async () => {
    const response = await fetch(`http://localhost:${testPort}/nonexistent-route-xyz`);
    assert.strictEqual(response.status, 404);
    const body = await response.json();
    assert.strictEqual(body.error.status, 404);
  });
});
