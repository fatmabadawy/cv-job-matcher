import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import { addToast } from "../components/Toast";
import { Radio, Mail, Lock, ArrowRight, CheckCircle2 } from "lucide-react";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignup, setIsSignup] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const endpoint = isSignup ? "/auth/signup" : "/auth/login";
      const res = await client.post(endpoint, { email, password });
      localStorage.setItem("token", res.data.token);
      localStorage.setItem("user_id", String(res.data.user_id));
      addToast(isSignup ? "Account created successfully" : "Authenticated successfully", "success");
      navigate("/matches");
    } catch (err) {
      addToast(err.response?.data?.detail || "Authentication failed", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: 24,
      background: "#14161A",
    }}>
      <div style={{
        width: "100%",
        maxWidth: 900,
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: 36,
        alignItems: "center",
      }}>
        {/* Left Side: Precision Control Room Intro */}
        <div style={{ paddingRight: 12 }}>
          <div className="chip chip-indigo font-mono-tabular" style={{ marginBottom: 16, fontSize: "0.75rem" }}>
            PRECISION SIGNAL MATCHING TOOL
          </div>

          <h1 style={{ fontSize: "2.2rem", fontWeight: 700, lineHeight: 1.15, marginBottom: 14 }}>
            Candidate Signal <br />
            <span style={{ color: "#6366F1" }}>Matching Control Room</span>
          </h1>

          <p style={{ color: "#94A3B8", fontSize: "0.92rem", lineHeight: 1.6, marginBottom: 24 }}>
            Upload your resume signal and let our FAISS vector engine and Groq LLM compute ranked, scored position matches across 220+ live embedded job listings.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {[
              { title: "220+ Live Job Positions", desc: "Real jobs scraped across LinkedIn, Arbeitnow, Remotive & WWR" },
              { title: "FAISS Cosine Similarity", desc: "Normalized 384-dimensional vector space retrieval" },
              { title: "Groq LLM Reranker", desc: "0.7s batched JSON scoring and role-specific match reasons" },
            ].map((item, idx) => (
              <div key={idx} style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
                <CheckCircle2 size={16} color="#10B981" style={{ marginTop: 2, flexShrink: 0 }} />
                <div>
                  <div style={{ fontSize: "0.88rem", fontWeight: 700, color: "#F1F5F9" }}>{item.title}</div>
                  <div style={{ fontSize: "0.8rem", color: "#64748B" }}>{item.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Side: Control Panel Login Form */}
        <div className="control-panel" style={{ padding: 32 }}>
          <div style={{ textAlign: "center", marginBottom: 24 }}>
            <div style={{
              width: 44,
              height: 44,
              borderRadius: 10,
              background: "rgba(99, 102, 241, 0.15)",
              border: "1px solid var(--border-focus)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 14px auto",
            }}>
              <Radio size={22} color="#6366F1" />
            </div>
            <h2 style={{ fontSize: "1.3rem", fontWeight: 700 }}>
              {isSignup ? "Create System Account" : "Control Room Authentication"}
            </h2>
            <p style={{ color: "#94A3B8", fontSize: "0.84rem", marginTop: 2 }}>
              {isSignup ? "Enter credentials to initialize profile" : "Sign in to access signal matches dashboard"}
            </p>
          </div>

          {/* Toggle Tabs */}
          <div style={{
            display: "flex",
            gap: 4,
            marginBottom: 20,
            background: "rgba(10, 12, 16, 0.6)",
            padding: 4,
            borderRadius: 8,
            border: "1px solid var(--border-subtle)",
          }}>
            {["Sign In", "Sign Up"].map((label, i) => (
              <button
                key={label}
                onClick={() => setIsSignup(i === 1)}
                style={{
                  flex: 1,
                  padding: "8px",
                  borderRadius: 6,
                  border: "none",
                  cursor: "pointer",
                  fontWeight: 600,
                  fontSize: "0.85rem",
                  transition: "all 0.15s ease",
                  background: isSignup === (i === 1) ? "#6366F1" : "transparent",
                  color: isSignup === (i === 1) ? "#ffffff" : "#94A3B8",
                }}
              >
                {label}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div>
              <label htmlFor="email" style={{ fontSize: "0.82rem", fontWeight: 600, color: "#94A3B8", marginBottom: 4, display: "block" }}>
                Email Address
              </label>
              <div style={{ position: "relative" }}>
                <Mail size={15} color="#64748B" style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)" }} />
                <input
                  id="email"
                  className="control-input"
                  type="email"
                  placeholder="operator@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  style={{ paddingLeft: 38 }}
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" style={{ fontSize: "0.82rem", fontWeight: 600, color: "#94A3B8", marginBottom: 4, display: "block" }}>
                Password
              </label>
              <div style={{ position: "relative" }}>
                <Lock size={15} color="#64748B" style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)" }} />
                <input
                  id="password"
                  className="control-input"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                  style={{ paddingLeft: 38 }}
                />
              </div>
            </div>

            <button
              id="auth-submit-btn"
              type="submit"
              className="btn-control-primary"
              disabled={loading}
              style={{ marginTop: 4, width: "100%", padding: "11px", fontSize: "0.9rem" }}
            >
              {loading ? (
                <>
                  <span className="spin-icon">⟳</span> {isSignup ? "Creating Account..." : "Signing In..."}
                </>
              ) : (
                <>
                  {isSignup ? "Create Account & Start" : "Authenticate & Access Control Room"}
                  <ArrowRight size={15} />
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
