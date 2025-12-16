// backend/src/db/init.js
import { queryWithRetry } from "./pool.js";

export async function initDb() {
  const schema = `
  CREATE TABLE IF NOT EXISTS quizzes (
    id SERIAL PRIMARY KEY,
    url VARCHAR(2048) NOT NULL,
    title VARCHAR(512) NOT NULL,
    user_id INT,
    date_generated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    scraped_html TEXT,
    scraped_text TEXT,
    full_quiz_data TEXT NOT NULL
  );

  DO $$
  BEGIN
    IF NOT EXISTS (
      SELECT 1 FROM pg_indexes WHERE indexname = 'uq_quizzes_url'
    ) THEN
      CREATE UNIQUE INDEX uq_quizzes_url ON quizzes (url);
    END IF;
  END $$;

  CREATE TABLE IF NOT EXISTS quiz_attempts (
    id SERIAL PRIMARY KEY,
    quiz_id INT NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    user_id INT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    submitted_at TIMESTAMPTZ,
    total_time INT,
    total_questions INT,
    time_taken_seconds INT,
    score INT,
    answers_json TEXT
  );

  CREATE INDEX IF NOT EXISTS idx_quiz_attempts_quiz_id ON quiz_attempts (quiz_id);
  `;

  try {
    console.log("Applying DB schema...");
    await queryWithRetry(schema, [], 3, 200);
    console.log("Database ready");
  } catch (err) {
    console.error("DB init error:", err && err.stack ? err.stack : err);
    throw err;
  }
  // 1. Users table
  await queryWithRetry(
    `
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      email VARCHAR(255) NOT NULL UNIQUE,
      password VARCHAR(255) NOT NULL,
      role VARCHAR(50) NOT NULL DEFAULT 'user',     -- 'user' | 'admin'
      is_verified BOOLEAN NOT NULL DEFAULT TRUE,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    `
  );

  // Ensure existing DBs get `user_id` on quiz_attempts (safe no-op if present)
  await queryWithRetry(
    `
    ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS user_id INT;
    `
  );

  // Ensure existing DBs get `user_id` on quizzes (safe no-op if present)
  await queryWithRetry(
    `
    ALTER TABLE quizzes ADD COLUMN IF NOT EXISTS user_id INT;
    `
  );

  // 2. OTPs table
  await queryWithRetry(
    `
    CREATE TABLE IF NOT EXISTS otps (
      id SERIAL PRIMARY KEY,
      email VARCHAR(255) NOT NULL,
      code VARCHAR(10) NOT NULL,
      purpose VARCHAR(20) NOT NULL,                -- 'REGISTER' | 'RESET'
      expires_at TIMESTAMPTZ NOT NULL,
      used BOOLEAN NOT NULL DEFAULT FALSE,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    `
  );

  console.log('DB schema ready');
}

  

