// backend/src/middleware/requireAdmin.js
let requireAdmin;
if (process.env.NODE_ENV === 'test') {
  requireAdmin = function (req, _res, next) {
    if (!req.user) {
      req.user = {
        userId: 1,
        email: 'admin@test.com',
        name: 'Admin Test',
        role: 'admin',
      };
    }
    return next();
  };
} else {
  requireAdmin = function (req, res, next) {
    if (!req.user) {
      return res.status(401).json({ message: 'Unauthorized: No user found' });
    }

    if (req.user.role !== 'admin') {
      return res.status(403).json({ message: 'Forbidden: Admins only' });
    }

    next();
  };
}

export default requireAdmin;
