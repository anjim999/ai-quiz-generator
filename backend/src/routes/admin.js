// backend/src/routes/admin.js
import express from 'express';
import { query } from '../db/pool.js';
import auth from '../middleware/auth.js';
import requireAdmin from '../middleware/requireAdmin.js';

const router = express.Router();

router.use(auth);
router.use(requireAdmin);

router.get('/users', async (_req, res) => {
  try {
    const { rows } = await query(
      `
      SELECT
        u.id,
        u.name,
        u.email,
        u.role,
        u.created_at,
        COUNT(q.id) AS quiz_count
      FROM users u
      LEFT JOIN quizzes q
        ON q.user_id = u.id
      GROUP BY u.id
      ORDER BY u.created_at DESC
      `
    );

    res.json(rows);
  } catch (err) {
    console.error('Admin users query error:', err);
    res.status(500).json({ message: 'DB error' });
  }
});

router.get('/user/:userId/attempts', async (req, res) => {
  try {
    const { userId } = req.params;

    const { rows } = await query(
      `
      SELECT
        qa.id,
        qa.quiz_id,
        q.title,
        q.url,
        qa.score,
        q.full_quiz_data,
        qa.submitted_at,
        qa.time_taken_seconds,
        qa.total_time,
        qa.total_questions
      FROM quiz_attempts qa
      JOIN quizzes q ON qa.quiz_id = q.id
      WHERE qa.user_id = $1
      ORDER BY qa.submitted_at DESC
      `,
      [userId]
    );

    res.json(rows);
  } catch (err) {
    console.error('Failed to fetch user attempts:', err);
    res.status(500).json({ message: 'DB error' });
  }
});

export default router;
