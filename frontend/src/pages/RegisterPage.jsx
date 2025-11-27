
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axiosClient";
import { useAuth } from "../context/AuthContext";
import { FaUserPlus, FaSpinner, FaEnvelope, FaLock } from "react-icons/fa";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

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
        err.response?.data?.message ||
        "Error sending OTP. Please try again.";

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
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
      <ToastContainer />

      <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl p-8 space-y-6 border border-gray-200">
        <div className="text-center">
          <FaUserPlus className="w-8 h-8 mx-auto mb-2 text-indigo-600" />
          <h1 className="text-3xl font-extrabold text-gray-900">
            {step === 1 ? "Create Account" : "Verify & Set Password"}
          </h1>
          <p className="text-sm text-gray-500 mt-1">Step {step} of 2</p>
        </div>

        {step === 1 && (
          <form
            onSubmit={handleRequestOtp}
            className="space-y-6"
            autoComplete="off"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Name
              </label>
              <input
                type="text"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-shadow duration-200"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="Your full name"
                autoComplete="name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email address
              </label>
              <input
                type="email"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-shadow duration-200"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@example.com"
                autoComplete="email"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="cursor-pointer w-full bg-blue-600 text-white py-2.5 rounded-lg font-semibold shadow-md hover:bg-blue-700 active:scale-[0.98] transition duration-150 flex items-center justify-center space-x-2 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <FaSpinner className="animate-spin w-4 h-4" />
                  <span>Sending OTP...</span>
                </>
              ) : (
                <>
                  <FaEnvelope className="w-4 h-4" />
                  <span>Send OTP</span>
                </>
              )}
            </button>
          </form>
        )}

        {step === 2 && (
          <form
            onSubmit={handleVerify}
            className="space-y-6"
            autoComplete="off"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Name
              </label>
              <input
                type="text"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm bg-gray-100 text-gray-500"
                value={name}
                disabled
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm bg-gray-100 text-gray-500"
                value={email}
                disabled
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                OTP
              </label>
              <input
                type="text"
                name="otp"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-shadow duration-200"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                required
                placeholder="Enter OTP from email"
                autoComplete="one-time-code"
                inputMode="numeric"
                maxLength="6"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Create Password
              </label>
              <input
                type="password"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-shadow duration-200"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Create a password"
                autoComplete="new-password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="cursor-pointer w-full bg-green-600 text-white py-2.5 rounded-lg font-semibold shadow-md hover:bg-green-700 active:scale-[0.98] transition duration-150 flex items-center justify-center space-x-2 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <FaSpinner className="animate-spin w-4 h-4" />
                  <span>Verifying...</span>
                </>
              ) : (
                <>
                  <FaLock className="w-4 h-4" />
                  <span>Register</span>
                </>
              )}
            </button>

            <button
              type="button"
              className="cursor-pointer w-full mt-2 text-xs font-medium text-indigo-600 hover:text-indigo-800 hover:underline transition-colors duration-150"
              onClick={() => {
                setStep(1);
                setOtp("");
                setPassword("");
              }}
            >
              Change email / name
            </button>
          </form>
        )}

        <div className="text-center pt-4 border-t border-gray-100">
          <p className="text-sm text-gray-600">
            Already have an account?{" "}
            <Link
              to="/login"
              className="text-indigo-600 font-medium hover:underline cursor-pointer"
            >
              Login
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}