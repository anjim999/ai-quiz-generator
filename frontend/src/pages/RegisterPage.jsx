// src/pages/RegisterPage.jsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axiosClient";
import { useAuth } from "../context/AuthContext";
import { FaSpinner, FaEnvelope, FaLock, FaUser, FaKey, FaArrowLeft } from "react-icons/fa";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import deepklarityLogo from "../assets/images/deepklarity-logo.png";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [step, setStep] = useState(1);
  const [otp, setOtp] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const { login } = useAuth();

  const handleRequestOtp = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post("/api/auth/register-request-otp", { email });
      toast.success("OTP sent to your email. Please check your inbox.", {
        autoClose: 2000,
      });
      setStep(2);
    } catch (err) {
      console.error(err);
      const backendMsg =
        err.response?.data?.message || "Error sending OTP. Please try again.";
      toast.error(backendMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post("/api/auth/register-verify", {
        name,
        email,
        otp,
        password,
      });

      login(res.data);
      toast.success("Registration successful!", { autoClose: 1500 });

      setTimeout(() => {
        navigate("/");
      }, 1500);
    } catch (err) {
      console.error(err);
      const backendMsg =
        err.response?.data?.message ||
        "Error verifying OTP. Please check your OTP and try again.";
      toast.error(backendMsg);
    } finally {
      setLoading(false);
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
          {/* Header */}
          <div className="text-center mb-6">
            <h1 className="text-heading text-slate-900 mb-1">
              {step === 1 ? "Create Account" : "Verify Email"}
            </h1>
            <p className="text-body text-sm">
              {step === 1
                ? "Get started with your free account"
                : "Enter the OTP sent to your email"
              }
            </p>
          </div>

          {/* Step Indicator */}
          <div className="flex items-center justify-center gap-2 mb-6">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
              ${step >= 1 ? 'bg-indigo-600 text-white' : 'bg-slate-200 text-slate-500'}`}>
              1
            </div>
            <div className={`w-8 h-1 rounded ${step >= 2 ? 'bg-indigo-600' : 'bg-slate-200'}`} />
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
              ${step >= 2 ? 'bg-indigo-600 text-white' : 'bg-slate-200 text-slate-500'}`}>
              2
            </div>
          </div>

          {step === 1 && (
            <form onSubmit={handleRequestOtp} className="space-y-5" autoComplete="off">
              {/* Name */}
              <div>
                <label className="label">Full Name</label>
                <div className="input-wrapper">
                  <FaUser className="input-icon" />
                  <input
                    type="text"
                    className="input"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    placeholder="Enter your full name"
                    autoComplete="name"
                  />
                </div>
              </div>

              {/* Email */}
              <div>
                <label className="label">Email Address</label>
                <div className="input-wrapper">
                  <FaEnvelope className="input-icon" />
                  <input
                    type="email"
                    className="input"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="you@example.com"
                    autoComplete="email"
                  />
                </div>
              </div>

              <button type="submit" disabled={loading} className="btn btn-primary w-full">
                {loading ? (
                  <>
                    <FaSpinner className="animate-spin w-4 h-4" />
                    <span>Sending OTP...</span>
                  </>
                ) : (
                  <>
                    <FaEnvelope className="w-4 h-4" />
                    <span>Send Verification Code</span>
                  </>
                )}
              </button>
            </form>
          )}

          {step === 2 && (
            <form onSubmit={handleVerify} className="space-y-5" autoComplete="off">
              {/* Email Display */}
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                <p className="text-sm text-slate-600">
                  Verification code sent to:
                </p>
                <p className="font-medium text-slate-900">{email}</p>
              </div>

              {/* OTP */}
              <div>
                <label className="label">Verification Code</label>
                <div className="input-wrapper">
                  <FaKey className="input-icon" />
                  <input
                    type="text"
                    className="input text-center tracking-widest font-mono text-lg"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    required
                    placeholder="000000"
                    autoComplete="one-time-code"
                    inputMode="numeric"
                    maxLength="6"
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <label className="label">Create Password</label>
                <div className="input-wrapper">
                  <FaLock className="input-icon" />
                  <input
                    type="password"
                    className="input"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    placeholder="Create a strong password"
                    autoComplete="new-password"
                    minLength="6"
                  />
                </div>
              </div>

              <button type="submit" disabled={loading} className="btn btn-success w-full">
                {loading ? (
                  <>
                    <FaSpinner className="animate-spin w-4 h-4" />
                    <span>Creating account...</span>
                  </>
                ) : (
                  <span>Create Account</span>
                )}
              </button>

              <button
                type="button"
                className="btn btn-ghost w-full"
                onClick={() => {
                  setStep(1);
                  setOtp("");
                  setPassword("");
                }}
              >
                <FaArrowLeft className="w-3 h-3" />
                <span>Change email</span>
              </button>
            </form>
          )}

          {/* Footer */}
          <div className="text-center text-sm mt-6 pt-6 border-t border-slate-100">
            <span className="text-slate-500">Already have an account? </span>
            <Link
              to="/login"
              className="text-indigo-600 font-medium hover:text-indigo-700 transition-colors"
            >
              Sign in
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