import { useState, useEffect } from "react";
import client from "../api/client";
import { addToast } from "../components/Toast";
import { User, Globe, Database, Cpu, Shield, RefreshCw, Zap, Server } from "lucide-react";

export default function Settings() {
  const [profile, setProfile] = useState(null);
  const [scraping, setScraping] = useState(false);
  const [indexing, setIndexing] = useState(false);

  useEffect(() => {
    client.get("/auth/me").then((res) => setProfile(res.data)).catch(() => {});
  }, []);

  async function triggerScrape() {
    setScraping(true);
    try {
      const res = await client.post("/admin/scrape");
      const c = res.data.scraped;
      addToast(
        `Scraped ${c.total} new jobs (RemoteOK: ${c.remoteok}, WWR: ${c.weworkremotely}, Remotive: ${c.remotive || 0})`,
        "success"
      );
    } catch (err) {
      addToast(err.response?.data?.detail || "Scraping failed", "error");
    } finally {
      setScraping(false);
    }
  }

  async function triggerIndex() {
    setIndexing(true);
    try {
      const res = await client.post("/admin/build-index");
      addToast(`Indexed ${res.data.indexed} new jobs`, "success");
    } catch (err) {
      addToast(err.response?.data?.detail || "Indexing failed", "error");
    } finally {
      setIndexing(false);
    }
  }

  return (
    <div style={{ maxWidth: 760, margin: "32px auto", padding: "0 24px" }} className="animate-fade-in">
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: "2.2rem", fontWeight: 800 }}>System Settings</h1>
        <p style={{ color: "#94a3b8", fontSize: "0.92rem", marginTop: 4 }}>
          Manage your account profile, trigger web scrapers, and inspect AI engine status
        </p>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
        {/* Account Profile Card */}
        <div className="glass-panel" style={{ padding: 28 }}>
          <h2 style={{ fontSize: "1.2rem", fontWeight: 800, marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
            <User size={18} color="#6366f1" /> Account Information
          </h2>
          {profile ? (
            <div>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 16px", background: "rgba(15, 23, 42, 0.6)", borderRadius: 10, border: "1px solid var(--border-glass)" }}>
                <div>
                  <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#64748b", textTransform: "uppercase" }}>Email Address</div>
                  <div style={{ fontSize: "1rem", fontWeight: 600, color: "#f8fafc", marginTop: 2 }}>{profile.email}</div>
                </div>
                <span className="badge badge-emerald">Active Account</span>
              </div>
            </div>
          ) : (
            <div style={{ color: "#94a3b8" }}>Loading account profile...</div>
          )}
        </div>

        {/* Data Sources Controls */}
        <div className="glass-panel" style={{ padding: 28 }}>
          <h2 style={{ fontSize: "1.2rem", fontWeight: 800, marginBottom: 8, display: "flex", alignItems: "center", gap: 8 }}>
            <Globe size={18} color="#06b6d4" /> Live Web Scraping & Indexing
          </h2>
          <p style={{ color: "#94a3b8", fontSize: "0.9rem", marginBottom: 20 }}>
            Trigger real-time HTTP web scrapers across RemoteOK, WeWorkRemotely RSS, and Remotive API to index new remote tech positions.
          </p>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <button
              id="scrape-btn"
              className="btn-cyan"
              onClick={triggerScrape}
              disabled={scraping}
            >
              <RefreshCw size={16} /> {scraping ? "Scraping Live Web..." : "Scrape Web Jobs Now"}
            </button>

            <button
              id="index-btn"
              className="btn-secondary"
              onClick={triggerIndex}
              disabled={indexing}
            >
              <Database size={16} /> {indexing ? "Building Vectors..." : "Build FAISS Vector Index"}
            </button>
          </div>
        </div>

        {/* System Architecture Details */}
        <div className="glass-panel" style={{ padding: 28 }}>
          <h2 style={{ fontSize: "1.2rem", fontWeight: 800, marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
            <Cpu size={18} color="#a855f7" /> AI Architecture & Stack
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {[
              ["Vector Embeddings Engine", "SentenceTransformers (all-MiniLM-L6-v2, 384-dim)"],
              ["Vector Search Index", "FAISS IndexFlatIP (L2 Normalized Cosine Similarity)"],
              ["Primary Reranking LLM", "Groq API (openai/gpt-oss-20b, 0.7s latency)"],
              ["Web Scraping Pipeline", "RemoteOK API + WeWorkRemotely RSS + Remotive API"],
              ["Background Scheduler", "APScheduler (Weekly Job Digest Task)"],
              ["Authentication", "JWT (HMAC-SHA256, Passlib Bcrypt)"],
            ].map(([k, v], idx) => (
              <div key={idx} style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                fontSize: "0.88rem",
                padding: "10px 14px",
                background: "rgba(15, 23, 42, 0.5)",
                borderRadius: 8,
                border: "1px solid var(--border-glass)",
              }}>
                <span style={{ color: "#94a3b8", fontWeight: 600 }}>{k}</span>
                <span style={{ color: "#f8fafc", fontWeight: 600 }}>{v}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
