// src/context/AuthContext.jsx
import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("auth");

    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (parsed?.token) {
          setAuth(parsed);
        } else {
          localStorage.removeItem("auth");
        }
      } catch (err) {
        console.error("Invalid auth data", err);
        localStorage.removeItem("auth");
      }
    }
    setLoading(false);
  }, []);

  const login = ({ token, user }) => {
    const payload = { token, user };
    setAuth(payload);
    localStorage.setItem("auth", JSON.stringify(payload));
  };

  const logout = () => {
    setAuth(null);
    localStorage.removeItem("auth");
  };

  return (
    <AuthContext.Provider value={{ auth, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
