// src/pages/LoginPage.jsx
import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../api/axiosClient";
import { FaSpinner, FaLock, FaEnvelope } from "react-icons/fa";
import { FcGoogle } from "react-icons/fc";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import deepklarityLogo from "../assets/images/deepklarity-logo.png";

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) {
      console.warn("VITE_GOOGLE_CLIENT_ID is not set. Google login will be disabled.");
      return;
    }

    const existingScript = document.querySelector(
      'script[src="https://accounts.google.com/gsi/client"]'
    );
    if (existingScript) return;

    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await api.post("/api/auth/login", { email, password });
      const { token, user } = res.data || {};

      if (!token || !user) {
        toast.error("Login succeeded but server sent no token/user");
        return;
      }

      login({ token, user });
      toast.success("Login successful!", { autoClose: 1500 });

      setTimeout(() => {
        if (user.role === "admin") navigate("/admin");
        else navigate("/");
      }, 1500);
    } catch (err) {
      const backendMsg = err?.response?.data?.message;
      toast.error(backendMsg || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    if (!GOOGLE_CLIENT_ID) {
      toast.error("Google login is not configured.");
      return;
    }

    if (!window.google || !window.google.accounts || !window.google.accounts.id) {
      toast.error("Google services not loaded yet. Please try again.");
      return;
    }

    setGoogleLoading(true);

    try {
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: async (response) => {
          const idToken = response.credential;
          if (!idToken) {
            toast.error("Google login failed: no credential received.");
            setGoogleLoading(false);
            return;
          }

          try {
            const res = await api.post("/api/auth/google", { idToken });
            const { token, user } = res.data || {};

            if (!token || !user) {
              toast.error("Google login succeeded but no token/user returned.");
              setGoogleLoading(false);
              return;
            }

            login({ token, user });
            toast.success("Logged in with Google!", { autoClose: 1500 });

            setTimeout(() => {
              if (user.role === "admin") navigate("/admin");
              else navigate("/");
            }, 1500);
          } catch (err) {
            const backendMsg = err?.response?.data?.message;
            toast.error(backendMsg || "Google login failed. Please try again.");
          } finally {
            setGoogleLoading(false);
          }
        },
      });

      window.google.accounts.id.prompt((notification) => {
        const notDisplayed = notification.isNotDisplayed?.();
        const skipped = notification.isSkippedMoment?.();
        if (notDisplayed || skipped) {
          setGoogleLoading(false);
        }
      });
    } catch (err) {
      console.error("Error during Google login:", err);
      toast.error("Google login failed. Please try again.");
      setGoogleLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <ToastContainer />

      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2.5 group">
            <img
              src={deepklarityLogo}
              alt="DeepKlarity"
              className="w-10 h-10 object-contain"
            />
            <span className="font-bold text-xl text-slate-900">
              DeepKlarity
            </span>
          </Link>
        </div>

        {/* Card */}
        <div className="card card-body">
          <div className="text-center mb-6">
            <h1 className="text-heading text-slate-900 mb-1">Welcome back</h1>
            <p className="text-body text-sm">Sign in to your account to continue</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5" autoComplete="off">
            {/* Email */}
            <div>
              <label className="label">Email address</label>
              <div className="input-wrapper">
                <FaEnvelope className="input-icon" />
                <input
                  type="email"
                  className="input"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="Enter your email"
                  autoComplete="email"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="label">Password</label>
              <div className="input-wrapper">
                <FaLock className="input-icon" />
                <input
                  type="password"
                  className="input"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="Enter your password"
                  autoComplete="current-password"
                />
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full"
            >
              {loading ? (
                <>
                  <FaSpinner className="animate-spin w-4 h-4" />
                  <span>Signing in...</span>
                </>
              ) : (
                <span>Sign In</span>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-3 my-6">
            <div className="h-px flex-1 bg-slate-200" />
            <span className="text-xs text-slate-400 uppercase">or</span>
            <div className="h-px flex-1 bg-slate-200" />
          </div>

          {/* Google Login */}
          <button
            type="button"
            onClick={handleGoogleLogin}
            disabled={googleLoading || loading}
            className="btn btn-secondary w-full"
          >
            {googleLoading ? (
              <>
                <FaSpinner className="animate-spin w-4 h-4" />
                <span>Connecting...</span>
              </>
            ) : (
              <>
                <FcGoogle className="w-5 h-5" />
                <span>Continue with Google</span>
              </>
            )}
          </button>

          {/* Footer Links */}
          <div className="flex justify-between text-sm mt-6 pt-6 border-t border-slate-100">
            <Link
              to="/register"
              className="text-indigo-600 font-medium hover:text-indigo-700 transition-colors"
            >
              Create account
            </Link>

            <Link
              to="/forgot-password"
              className="text-slate-500 hover:text-slate-700 transition-colors"
            >
              Forgot password?
            </Link>
          </div>
        </div>

        {/* Back to Home */}
        <p className="text-center mt-6 text-sm text-slate-500">
          <Link to="/" className="hover:text-indigo-600 transition-colors">
            ← Back to home
          </Link>
        </p>
      </div>
    </div>
  );
}