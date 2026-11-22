/**
 * Unit Tests for Prisma Client Configuration
 * File: backend/tests/unit/prisma.test.js
 */

import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { prisma, checkDatabaseConnection, disconnectDatabase } from '../../src/config/prisma.js';

describe('Prisma Database Configuration & Client Tests', () => {
  test('PrismaClient singleton is instantiated and defined', () => {
    assert.ok(prisma, 'Prisma client singleton must be defined');
    assert.strictEqual(typeof prisma.$connect, 'function', 'Prisma client must have $connect method');
    assert.strictEqual(typeof prisma.$disconnect, 'function', 'Prisma client must have $disconnect method');
  });

  test('Prisma schema models are registered on client instance', () => {
    // Verify our defined models are accessible on the client
    assert.ok(prisma.user, 'User model delegate must exist on prisma client');
    assert.ok(prisma.studentProfile, 'StudentProfile model delegate must exist on prisma client');
    assert.ok(prisma.subject, 'Subject model delegate must exist on prisma client');
    assert.ok(prisma.topic, 'Topic model delegate must exist on prisma client');
    assert.ok(prisma.topicPrerequisite, 'TopicPrerequisite model delegate must exist on prisma client');
    assert.ok(prisma.question, 'Question model delegate must exist on prisma client');
    assert.ok(prisma.questionOption, 'QuestionOption model delegate must exist on prisma client');
    assert.ok(prisma.studentInteraction, 'StudentInteraction model delegate must exist on prisma client');
    assert.ok(prisma.studentTopicMastery, 'StudentTopicMastery model delegate must exist on prisma client');
    assert.ok(prisma.masteryHistory, 'MasteryHistory model delegate must exist on prisma client');
    assert.ok(prisma.studyRecommendation, 'StudyRecommendation model delegate must exist on prisma client');
  });

  test('checkDatabaseConnection handles connection check without unhandled exceptions', async () => {
    const result = await checkDatabaseConnection(1000);
    assert.ok(typeof result.isConnected === 'boolean', 'isConnected must be a boolean');
    if (!result.isConnected) {
      assert.ok(typeof result.error === 'string', 'error must be reported when not connected');
    } else {
      assert.ok(typeof result.latencyMs === 'number', 'latencyMs must be reported when connected');
    }
  });

  test('disconnectDatabase executes cleanly', async () => {
    await assert.doesNotReject(
      async () => await disconnectDatabase(),
      'disconnectDatabase must not throw an unhandled error'
    );
  });
});
