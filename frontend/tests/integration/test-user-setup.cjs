/**
 * Test User Setup Script
 *
 * Creates verified test users directly in MongoDB for integration tests.
 * Run this before running Playwright tests.
 *
 * Usage:
 *   node tests/integration/test-user-setup.js
 */

const { MongoClient } = require('mongodb');
const bcrypt = require('bcrypt');

const DB_URL = process.env.DB_URL || 'mongodb://localhost:27017';
const DB_NAME = process.env.DB_NAME || 'nyrkiodb';

const TEST_USERS = [
  {
    email: 'test@example.com',
    password: 'testpassword123',
    username: 'testuser',
    is_verified: true,
    is_active: true,
    is_superuser: false,
  },
  {
    email: 'john@foo.com',
    password: 'foo',
    username: 'john',
    is_verified: true,
    is_active: true,
    is_superuser: false,
  },
  {
    email: 'admin@foo.com',
    password: 'admin',
    username: 'admin',
    is_verified: true,
    is_active: true,
    is_superuser: true,
  }
];

async function hashPassword(password) {
  const saltRounds = 10;
  return await bcrypt.hash(password, saltRounds);
}

async function createTestUsers() {
  const client = new MongoClient(DB_URL);

  try {
    await client.connect();
    console.log('Connected to MongoDB');

    const db = client.db(DB_NAME);
    const usersCollection = db.collection('User');

    for (const userData of TEST_USERS) {
      // Check if user already exists
      const existing = await usersCollection.findOne({ email: userData.email });

      if (existing) {
        console.log(`User ${userData.email} already exists, updating...`);
        // Update to ensure verified and correct password
        await usersCollection.updateOne(
          { email: userData.email },
          {
            $set: {
              hashed_password: await hashPassword(userData.password),
              is_verified: true,
              is_active: true,
              is_superuser: userData.is_superuser
            }
          }
        );
        console.log(`✓ Updated ${userData.email}`);
      } else {
        // Create new user
        const user = {
          email: userData.email,
          hashed_password: await hashPassword(userData.password),
          is_active: userData.is_active,
          is_superuser: userData.is_superuser,
          is_verified: userData.is_verified,
          oauth_accounts: [],
          slack: {},
          billing: null,
          github_username: null,
          is_cph_user: null,
          is_repo_owner: false
        };

        await usersCollection.insertOne(user);
        console.log(`✓ Created ${userData.email}`);
      }
    }

    console.log('\n✅ All test users created/updated successfully!');
    console.log('\nTest users:');
    TEST_USERS.forEach(u => console.log(`  - ${u.email} / ${u.password}`));

  } catch (error) {
    console.error('Error creating test users:', error);
    process.exit(1);
  } finally {
    await client.close();
  }
}

async function cleanupTestUsers() {
  const client = new MongoClient(DB_URL);

  try {
    await client.connect();
    const db = client.db(DB_NAME);
    const usersCollection = db.collection('User');

    const emails = TEST_USERS.map(u => u.email);
    const result = await usersCollection.deleteMany({ email: { $in: emails } });

    console.log(`✓ Deleted ${result.deletedCount} test users`);
  } catch (error) {
    console.error('Error cleaning up test users:', error);
  } finally {
    await client.close();
  }
}

// Check if running as main script
if (require.main === module) {
  const command = process.argv[2];

  if (command === 'cleanup') {
    cleanupTestUsers();
  } else {
    createTestUsers();
  }
}

module.exports = { createTestUsers, cleanupTestUsers };
