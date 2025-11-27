// src/components/ProtectedRoute.jsx
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children, requireAdmin = false }) {
  const { auth, loading } = useAuth();

  if (loading) return null;

  if (!auth?.token) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && auth.user?.role !== "admin") {
    return <Navigate to="/" replace />;
  }

  return children;
}