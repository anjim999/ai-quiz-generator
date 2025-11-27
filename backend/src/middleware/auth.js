// backend/src/middleware/auth.js
import jwt from 'jsonwebtoken';
import { JWT_SECRET } from '../config/env.js';

let authMiddleware;

if (process.env.NODE_ENV === 'test') {
  authMiddleware = function (req, _res, next) {
    req.user = {
      userId: 1,
      email: 'test@example.com',
      name: 'Test User',
      role: 'admin',
    };
    return next();
  };
} else {
  authMiddleware = function (req, res, next) {
    const authHeader = req.headers.authorization || '';
    const token = authHeader.startsWith('Bearer ')
      ? authHeader.slice(7)
      : null;

    if (!token) {
      return res.status(401).json({ message: 'No token provided' });
    }

    try {
      const decoded = jwt.verify(token, JWT_SECRET);
      req.user = {
        userId: decoded.userId,
        email: decoded.email,
        name: decoded.name,
        role: decoded.role || 'user',
      };
      next();
    } catch (err) {
      console.error('JWT error:', err);
      return res.status(401).json({ message: 'Invalid or expired token' });
    }
  };
}

export default authMiddleware;
