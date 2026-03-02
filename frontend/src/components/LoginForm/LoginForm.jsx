import { useState } from "react";
import "./LoginForm.css";

const API_BASE = "http://localhost:8000";

// ── LoginForm ─────────────────────────────────────────────────────────────
// Full-screen login / sign-up page.
// Props:
//   onLogin — callback(email) called with the user's email on success
export function LoginForm({ onLogin }) {
  const [mode,     setMode]     = useState("login");   // "login" | "signup"
  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [error,    setError]    = useState("");
  const [loading,  setLoading]  = useState(false);

  const handleSubmit = async () => {
    setError("");
    if (!email.trim() || !password) {
      setError("Email and password are required.");
      return;
    }

    setLoading(true);
    try {
      const endpoint = mode === "login" ? "/login" : "/signup";
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        // FastAPI raises HTTPException with a `detail` field
        setError(data.detail || "Something went wrong.");
        return;
      }

      // data.email comes back from both /signup and /login responses
      onLogin(data.email);
    } catch (err) {
      setError("Could not reach the server. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  // Allow submitting with Enter key
  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSubmit();
  };

  return (
    <div className="login-shell">
      <div className="login-panel">

        {/* Brand */}
        <div className="login-panel__brand">
          <p className="login-panel__brand-name">ResaleIQ</p>
          <p className="login-panel__brand-sub">Multi-Platform Dashboard</p>
        </div>

        {/* Login / Sign Up tabs */}
        <div className="login-tabs">
          <button
            className={`login-tab ${mode === "login"  ? "login-tab--active" : ""}`}
            onClick={() => { setMode("login");  setError(""); }}
          >
            Log In
          </button>
          <button
            className={`login-tab ${mode === "signup" ? "login-tab--active" : ""}`}
            onClick={() => { setMode("signup"); setError(""); }}
          >
            Sign Up
          </button>
        </div>

        {/* Fields */}
        <div className="login-fields">
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
