import { useState } from "react";
import "./LoginForm.css";

const API_BASE = "http://localhost:8000";

// ── Dummy credentials ─────────────────────────────────────────────────────
const DUMMY_EMAIL    = "dummy@email.com";
const DUMMY_PASSWORD = "password";

// ── LoginForm ─────────────────────────────────────────────────────────────
// Full-screen login / sign-up page.
// Props:
//   onLogin — callback(email) called with the user's email on success
export function LoginForm({ onLogin }) {
  const [mode,     setMode]     = useState("login");   // "login" | "signup"
  const [firstName,       setFirstName]       = useState("");
  const [lastName,        setLastName]        = useState("");
  const [email,           setEmail]           = useState("");
  const [password,        setPassword]        = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error,           setError]           = useState("");
  const [loading,         setLoading]         = useState(false);

  const handleSubmit = async () => {
    setError("");

    if (mode === "signup") {
      if (!firstName.trim() || !lastName.trim()) {
        setError("First and last name are required.");
        return;
      }
      if (!email.trim() || !password) {
        setError("Email and password are required.");
        return;
      }
      if (password !== confirmPassword) {
        setError("Passwords do not match.");
        return;
      }
    } else {
      if (!email.trim() || !password) {
        setError("Email and password are required.");
        return;
      }
    }

    // ── Dummy bypass (remove before shipping) ──────────────────────────
    if (email === DUMMY_EMAIL && password === DUMMY_PASSWORD) {
      onLogin(DUMMY_EMAIL);
      return;
    }

    setLoading(true);
    try {
      const endpoint = mode === "login" ? "/login" : "/signup";
      const body = mode === "login"
        ? { email, password }
        : { first_name: firstName, last_name: lastName, email, password };

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(body),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Something went wrong.");
        return;
      }

      onLogin(data.email);
    } catch (err) {
      setError("Could not reach the server. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSubmit();
  };

  // Clear all fields when switching tabs
  const switchMode = (newMode) => {
    setMode(newMode);
    setError("");
    setFirstName("");
    setLastName("");
    setEmail("");
    setPassword("");
    setConfirmPassword("");
  };

  return (
    <div className="login-shell">
      <div className="login-panel">

        {/* Brand */}
        <div className="login-panel__brand">
          <p className="login-panel__brand-name">Cross-Platform Resale Intelligence</p>
          <p className="login-panel__brand-sub">Multi-Platform Dashboard</p>
        </div>

        {/* Login / Sign Up tabs */}
        <div className="login-tabs">
          <button
            className={`login-tab ${mode === "login"  ? "login-tab--active" : ""}`}
            onClick={() => switchMode("login")}
          >
            Log In
          </button>
          <button
            className={`login-tab ${mode === "signup" ? "login-tab--active" : ""}`}
            onClick={() => switchMode("signup")}
          >
            Sign Up
          </button>
        </div>

        {/* Fields */}
        <div className="login-fields">

          {/* Signup-only: first + last name side by side */}
          {mode === "signup" && (
            <div style={{ display: "flex", gap: "10px" }}>
              <div className="login-field" style={{ flex: 1 }}>
                <label>First Name</label>
                <input
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="John"
                />
              </div>
              <div className="login-field" style={{ flex: 1 }}>
                <label>Last Name</label>
                <input
                  type="text"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Doe"
                />
              </div>
            </div>
          )}

          <div className="login-field">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="you@example.com"
            />
          </div>

          <div className="login-field">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="••••••••"
            />
          </div>

          {/* Signup-only: confirm password */}
          {mode === "signup" && (
            <div className="login-field">
              <label>Confirm Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="••••••••"
              />
            </div>
          )}

          {error && <p className="login-error">{error}</p>}

          <button
            className="login-submit"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading
              ? "Please wait…"
              : mode === "login" ? "Log In" : "Create Account"}
          </button>
        </div>

      </div>
    </div>
  );
}