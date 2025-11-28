// backend/src/routes/auth.js
import express from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { body, validationResult } from 'express-validator';
import { query } from '../db/pool.js';
import { generateOtp, getExpiry } from '../utils/otp.js';
import { JWT_SECRET,GOOGLE_CLIENT_ID } from '../config/env.js';
import { sendOtpEmail } from '../utils/mailer.js';
const { OAuth2Client } = require("google-auth-library");

const router = express.Router();

const googleClient = GOOGLE_CLIENT_ID
  ? new OAuth2Client(GOOGLE_CLIENT_ID)
  : null;

const validate = (rules) => [
  ...rules,
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      console.error('Validation error:', errors.array());
      return res.status(400).json({ errors: errors.array() });
    }
    next();
  },
];

const normalizeEmail = (email = '') => email.trim().toLowerCase();

// REGISTER – STEP 1: request OTP
router.post('/register-request-otp', async (req, res) => {
  try {
    const rawEmail = req.body.email || '';
    const email = normalizeEmail(rawEmail);

    const code = generateOtp();
    const expiresAt = getExpiry(10);

    await query(
      `INSERT INTO otps (email, code, purpose, expires_at)
       VALUES ($1, $2, $3, $4)`,
      [email, code, 'REGISTER', expiresAt]
    );

    const mailResult = await sendOtpEmail({
      to: email,
      otp: code,
      purpose: 'REGISTER',
    });

    if (!mailResult.success) {
      console.warn(
        'OTP email not delivered. OTP logged on server only (dev mode).'
      );
    }

    return res.json({
      message:
        "OTP generated. If email doesn't arrive, use the OTP from server logs.",
      devOtp: process.env.NODE_ENV !== 'production' ? code : undefined,
    });
  } catch (err) { 
    console.error('Error in /register-request-otp:', err);
    return res.status(500).json({ err });
  }
});

// REGISTER – STEP 2: verify OTP and create user
router.post(
  '/register-verify',
  validate([
    body('name').notEmpty().withMessage('Name is required'),
    body('email').isEmail(),
    body('otp').isLength({ min: 4 }),
    body('password').isLength({ min: 6 }),
  ]),
  async (req, res) => {
    try {
      const { name, email: rawEmail, otp, password } = req.body;
      const email = normalizeEmail(rawEmail);

      const {
        rows: [otpRow],
      } = await query(
        `SELECT * FROM otps
         WHERE email = $1 AND code = $2 AND purpose = $3 AND used = FALSE
         ORDER BY created_at DESC
         LIMIT 1`,
        [email, otp, 'REGISTER']
      );

      if (!otpRow) {
        return res.status(400).json({ message: 'Invalid OTP' });
      }

      const nowIso = new Date().toISOString();
      if (otpRow.expires_at < nowIso) {
        return res.status(400).json({ message: 'OTP expired' });
      }

      const hashed = bcrypt.hashSync(password, 10);

      const {
        rows: [user],
      } = await query(
        `INSERT INTO users (name, email, password, is_verified)
         VALUES ($1, $2, $3, TRUE)
         ON CONFLICT (email) DO UPDATE SET
           name = EXCLUDED.name,
           password = EXCLUDED.password,
           is_verified = TRUE
         RETURNING id, name, email, role`,
        [name, email, hashed]
      );

      await query(`UPDATE otps SET used = TRUE WHERE id = $1`, [otpRow.id]);

      const role = user.role || 'user';

      const token = jwt.sign(
        { userId: user.id, email: user.email, name: user.name, role },
        JWT_SECRET,
        { expiresIn: '1d' }
      );

      return res.json({
        message: 'Registration successful',
        token,
        user: {
          id: user.id,
          name: user.name,
          email: user.email,
          role,
        },
      });
    } catch (err) {
      console.error('Error in /register-verify:', err);
      return res.status(500).json({ message: 'DB error / registration failed' });
    }
  }
);

// LOGIN
router.post(
  '/login',
  validate([
    body('email').isEmail().withMessage('Valid email required'),
    body('password').notEmpty().withMessage('Password is required'),
  ]),
  async (req, res) => {
    try {
      const rawEmail = req.body.email || '';
      const email = normalizeEmail(rawEmail);
      const { password } = req.body;

      const {
        rows: [user],
      } = await query('SELECT * FROM users WHERE email = $1', [email]);

      if (!user) {
        console.warn('Login failed: user not found for', email);
        return res.status(400).json({ message: 'Invalid credentials' });
      }

      const ok = bcrypt.compareSync(password, user.password);
      if (!ok) {
        console.warn('Login failed: wrong password for', email);
        return res.status(400).json({ message: 'Invalid credentials' });
      }

      const role = user.role || 'user';

      const token = jwt.sign(
        {
          userId: user.id,
          email: user.email,
          name: user.name,
          role,
        },
        JWT_SECRET,
        { expiresIn: '1d' }
      );

      console.log('Login successful for', email);
      res.json({
        message: 'Login successful',
        token,
        user: {
          id: user.id,
          name: user.name,
          email: user.email,
          role,
        },
      });
    } catch (err) {
      console.error('DB error on login:', err);
      return res.status(500).json({ message: 'DB error' });
    }
  }
);

// FORGOT PASSWORD – STEP 1: request OTP
router.post(
  '/forgot-password-request',
  validate([body('email').isEmail()]),
  async (req, res) => {
    try {
      const rawEmail = req.body.email || '';
      const email = normalizeEmail(rawEmail);

      const { rowCount } = await query(
        'SELECT id FROM users WHERE email = $1',
        [email]
      );

      if (rowCount === 0) {
        console.warn('Forgot password for non-existing email:', email);
        return res.json({
          message:
            'If the email exists, an OTP has been sent to reset the password',
        });
      }

      const code = generateOtp();
      const expiresAt = getExpiry(10);

      await query(
        `INSERT INTO otps (email, code, purpose, expires_at)
         VALUES ($1, $2, $3, $4)`,
        [email, code, 'RESET', expiresAt]
      );

      try {
        await sendOtpEmail({ to: email, otp: code, purpose: 'RESET' });
        console.log('Reset OTP for', email, '=>', code);
        return res.json({
          message:
            'If the email exists, an OTP has been sent to reset the password',
        });
      } catch (mailErr) {
        console.error('Error sending reset OTP email:', mailErr);
        return res
          .status(500)
          .json({ message: 'Failed to send OTP email. Try again.' });
      }
    } catch (err) {
      console.error('DB error on forgot-password-request:', err);
      return res.status(500).json({ message: 'DB error' });
    }
  }
);

// FORGOT PASSWORD – STEP 2: verify + change password
router.post(
  '/forgot-password-verify',
  validate([
    body('email').isEmail(),
    body('otp').isLength({ min: 4 }),
    body('newPassword').isLength({ min: 6 }),
  ]),
  async (req, res) => {
    try {
      const { email: rawEmail, otp, newPassword } = req.body;
      const email = normalizeEmail(rawEmail);

      const {
        rows: [otpRow],
      } = await query(
        `SELECT * FROM otps
         WHERE email = $1 AND code = $2 AND purpose = $3 AND used = FALSE
         ORDER BY created_at DESC
         LIMIT 1`,
        [email, otp, 'RESET']
      );

      if (!otpRow) {
        return res.status(400).json({ message: 'Invalid OTP' });
      }

      const nowIso = new Date().toISOString();
      if (otpRow.expires_at < nowIso) {
        return res.status(400).json({ message: 'OTP expired' });
      }

      const hashed = bcrypt.hashSync(newPassword, 10);

      const result = await query(
        'UPDATE users SET password = $1 WHERE email = $2',
        [hashed, email]
      );

      if (result.rowCount === 0) {
        console.warn('Password reset for non-existing email:', email);
        return res
          .status(400)
          .json({ message: 'User not found for this email' });
      }

      await query('UPDATE otps SET used = TRUE WHERE id = $1', [otpRow.id]);

      console.log('Password reset successful for', email);
      return res.json({ message: 'Password reset successful' });
    } catch (err) {
      console.error('DB error on reset verify:', err);
      return res.status(500).json({ message: 'DB error' });
    }
  }
);

router.post("/google", async (req, res) => {
  try {
    const { idToken, credential } = req.body || {};

    // Accept either "idToken" or "credential" from frontend
    const token = idToken || credential;

    if (!token) {
      return res
        .status(400)
        .json({ message: "idToken (or credential) is required" });
    }

    if (!googleClient || !GOOGLE_CLIENT_ID) {
      console.error("Google auth not configured on server.");
      return res
        .status(500)
        .json({ message: "Google login is not configured on server." });
    }

    // Verify ID token with Google
    const ticket = await googleClient.verifyIdToken({
      idToken: token,
      audience: GOOGLE_CLIENT_ID,
    });

    const payload = ticket.getPayload();

    const googleId = payload.sub;
    const rawEmail = payload.email || "";
    const email = normalizeEmail(rawEmail);
    const name = payload.name || email;
    const avatar = payload.picture || null;

    if (!email) {
      return res
        .status(400)
        .json({ message: "Google account does not have a valid email." });
    }

    // TC: O(1) average lookup by email
    db.get(
      "SELECT * FROM users WHERE email = ?",
      [email],
      (err, userRow) => {
        if (err) {
          console.error("DB error on Google login:", err);
          return res.status(500).json({ message: "DB error" });
        }

        if (userRow) {
          // Existing user: log them in
          const role = userRow.role || "user";

          const jwtPayload = {
            userId: userRow.id,
            email: userRow.email,
            name: userRow.name,
            role,
          };

          const token = jwt.sign(jwtPayload, JWT_SECRET, {
            expiresIn: "1d",
          });

          console.log("Google login successful for existing user:", email);

          return res.json({
            message: "Login successful",
            token,
            user: {
              id: userRow.id,
              name: userRow.name,
              email: userRow.email,
              role,
              avatar: userRow.avatar || avatar || null,
            },
          });
        }

        // New user: create a record
        const createdAt = new Date().toISOString();
        const role = "user";

        // Dummy password to satisfy NOT NULL constraint
        const dummyPassword = bcrypt.hashSync(googleId + JWT_SECRET, 10);

        db.run(
          "INSERT INTO users (name, email, password, role, is_verified, created_at, google_id, avatar) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
          [name, email, dummyPassword, role, 1, createdAt, googleId, avatar],
          function (err2) {
            if (err2) {
              console.error("DB error inserting Google user:", err2);
              return res.status(500).json({ message: "DB error" });
            }

            const userId = this.lastID;

            const jwtPayload = { userId, email, name, role };

            const token = jwt.sign(jwtPayload, JWT_SECRET, {
              expiresIn: "1d",
            });

            console.log("Google login created new user:", email);

            return res.json({
              message: "Login successful",
              token,
              user: {
                id: userId,
                name,
                email,
                role,
                avatar,
              },
            });
          }
        );
      }
    );
  } catch (err) {
    console.error("Error in /api/auth/google:", err);
    return res.status(401).json({ message: "Invalid Google token" });
  }
});

export default router;
