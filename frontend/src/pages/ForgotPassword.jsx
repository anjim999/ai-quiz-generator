// src/pages/ForgotPassword.jsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axiosClient";
import { FaSpinner, FaEnvelope, FaKey, FaLock, FaArrowLeft } from "react-icons/fa";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import deepklarityLogo from "../assets/images/deepklarity-logo.png";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [step, setStep] = useState(1);
  const [otp, setOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const normalizeEmail = (value) => value.trim().toLowerCase();

  const handleRequestOtp = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const normalizedEmail = normalizeEmail(email);
      setEmail(normalizedEmail);

      await api.post("/api/auth/forgot-password-request", {
        email: normalizedEmail,
      });

      toast.success(
        "If the email exists, an OTP has been sent. Please check your inbox.",
        { autoClose: 2000 }
      );

      setStep(2);
    } catch (err) {
      console.error(err);
      const backendMsg =
        err.response?.data?.message || "Error sending OTP. Please try again.";
      toast.error(backendMsg, { autoClose: 2000 });
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const normalizedEmail = normalizeEmail(email);

      await api.post("/api/auth/forgot-password-verify", {
        email: normalizedEmail,
        otp: otp.trim(),
        newPassword,
      });

      toast.success("Password reset successful. Redirecting to login...", {
        autoClose: 1500,
      });

      setTimeout(() => {
        navigate("/login");
      }, 1500);
    } catch (err) {
      console.error(err);
      const backendMsg =
        err.response?.data?.message ||
        "Error resetting password. Check OTP and try again.";
      toast.error(backendMsg, { autoClose: 2000 });
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
            <h1 className="text-heading text-slate-900 mb-1">Reset Password</h1>
            <p className="text-body text-sm">
              {step === 1
                ? "Enter your email to receive a reset code"
                : "Enter the code sent to your email"}
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
                    <span>Sending Code...</span>
                  </>
                ) : (
                  <>
                    <FaEnvelope className="w-4 h-4" />
                    <span>Send Reset Code</span>
                  </>
                )}
              </button>
            </form>
          )}

          {step === 2 && (
            <form onSubmit={handleVerify} className="space-y-5" autoComplete="off">
              {/* Email Display */}
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                <p className="text-sm text-slate-600">Reset code sent to:</p>
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

              {/* New Password */}
              <div>
                <label className="label">New Password</label>
                <div className="input-wrapper">
                  <FaLock className="input-icon" />
                  <input
                    type="password"
                    className="input"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    placeholder="Enter new password"
                    autoComplete="new-password"
                    minLength="6"
                  />
                </div>
              </div>

              <button type="submit" disabled={loading} className="btn btn-success w-full">
                {loading ? (
                  <>
                    <FaSpinner className="animate-spin w-4 h-4" />
                    <span>Resetting...</span>
                  </>
                ) : (
                  <span>Reset Password</span>
                )}
              </button>

              <button
                type="button"
                className="btn btn-ghost w-full"
                onClick={() => {
                  setStep(1);
                  setOtp("");
                  setNewPassword("");
                }}
              >
                <FaArrowLeft className="w-3 h-3" />
                <span>Change email</span>
              </button>
            </form>
          )}

          {/* Footer */}
          <div className="text-center text-sm mt-6 pt-6 border-t border-slate-100">
            <Link
              to="/login"
              className="text-indigo-600 font-medium hover:text-indigo-700 transition-colors"
            >
              ← Back to Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}