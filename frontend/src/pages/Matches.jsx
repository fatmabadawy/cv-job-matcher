import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import { addToast } from "../components/Toast";
import ScoreGauge from "../components/ScoreGauge";
import { Search, MapPin, Building2, ChevronRight, RefreshCw, Upload, CheckCircle2, SlidersHorizontal, Globe, Filter } from "lucide-react";

function getJobSource(link) {
  if (!link) return "Web Listing";
  if (link.includes("linkedin.com")) return "LinkedIn";
  if (link.includes("arbeitnow.com")) return "Arbeitnow";
  if (link.includes("weworkremotely.com")) return "WeWorkRemotely";
  if (link.includes("remotive.com")) return "Remotive";
  if (link.includes("remoteok.com")) return "RemoteOK";
  return "Web Listing";
}

function getWorkMode(job) {
  const text = `${job.location || ''} ${job.title || ''} ${job.description || ''}`.toLowerCase();
  if (text.includes("hybrid")) return "Hybrid";
  if (text.includes("remote") || text.includes("worldwide") || text.includes("anywhere")) return "Remote";
  return "Onsite";
}

function JobCard({ match, onSelect }) {
  const source = getJobSource(match.link);
  const workMode = getWorkMode(match);

  return (
    <div
      className="control-panel control-panel-interactive"
      style={{
        padding: "20px 24px",
        cursor: "pointer",
        display: "flex",
        gap: 20,
        alignItems: "center",
      }}
      onClick={() => onSelect(match)}
      id={`job-card-${match.job_id}`}
    >
      {/* 1. Signature Score Gauge */}
      <ScoreGauge score={match.score} size={64} strokeWidth={5} />

      {/* 2. Structured Data Hierarchy: Title > Company/Location/Source > Reasons */}
      <div style={{ flex: 1, minWidth: 0 }}>
        {/* Title & Source Pill */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", marginBottom: 4 }}>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#F1F5F9" }}>{match.title}</h3>
          
          {/* Source Tag */}
          <span className="chip chip-indigo font-mono-tabular" style={{ fontSize: "0.72rem" }}>
            <Globe size={11} color="#6366F1" /> {source}
          </span>

          {/* Work Mode Tag */}
          <span className="chip chip-slate font-mono-tabular" style={{ fontSize: "0.72rem" }}>
            {workMode}
          </span>

          {match.score >= 75 && (
            <span className="chip chip-emerald font-mono-tabular" style={{ fontSize: "0.72rem" }}>
              HIGH SIGNAL
            </span>
          )}
        </div>

        {/* Company & Location */}
        <div style={{ display: "flex", alignItems: "center", gap: 16, color: "#94A3B8", fontSize: "0.86rem", marginBottom: 10 }}>
          <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <Building2 size={14} color="#6366F1" /> {match.company}
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <MapPin size={14} color="#64748B" /> {match.location || "Remote"}
          </span>
        </div>

        {/* Match Reasons */}
        {match.reasons?.length > 0 && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {match.reasons.map((r, i) => (
              <span key={i} className="chip chip-slate font-mono-tabular" style={{ fontSize: "0.75rem" }}>
                <CheckCircle2 size={12} color={match.score >= 75 ? "#10B981" : "#6366F1"} /> {r}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Chevron Action Indicator */}
      <div style={{
        width: 34,
        height: 34,
        borderRadius: 8,
        background: "rgba(255, 255, 255, 0.04)",
        border: "1px solid var(--border-subtle)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "#94A3B8",
        flexShrink: 0,
      }}>
        <ChevronRight size={18} />
      </div>
    </div>
  );
}

export default function Matches() {
  const [matches, setMatches] = useState([]);
  const [query, setQuery] = useState("");
  const [locationQuery, setLocationQuery] = useState("");
  const [selectedSource, setSelectedSource] = useState("All");
  const [selectedWorkMode, setSelectedWorkMode] = useState("All");
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    client.get("/match/results")
      .then((res) => setMatches(res.data))
      .catch(() => {})
      .finally(() => setFetching(false));
  }, []);

  async function runMatch() {
    setLoading(true);
    try {
      const res = await client.post("/match/run");
      setMatches(res.data);
      addToast(`Evaluated ${res.data.length} candidate jobs against CV signal`, "success");
    } catch (err) {
      const msg = err.response?.data?.detail || "Match calculation failed";
      addToast(msg, "error");
    } finally {
      setLoading(false);
    }
  }

  const filteredMatches = matches.filter((m) => {
    // Text search query
    if (query.trim()) {
      const q = query.toLowerCase();
      const matchText = (m.title + " " + m.company + " " + (m.reasons || []).join(" ")).toLowerCase();
      if (!matchText.includes(q)) return false;
    }

    // Location query
    if (locationQuery.trim()) {
      const lq = locationQuery.toLowerCase();
      const locText = (m.location || "").toLowerCase();
      if (!locText.includes(lq)) return false;
    }

    // Source filter
    if (selectedSource !== "All") {
      const source = getJobSource(m.link);
      if (source !== selectedSource) return false;
    }

    // Work Mode filter
    if (selectedWorkMode !== "All") {
      const mode = getWorkMode(m);
      if (mode !== selectedWorkMode) return false;
    }

    return true;
  });

  return (
    <div style={{ maxWidth: 1040, margin: "32px auto", padding: "0 24px" }}>
      {/* Control Room Header */}
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: 28,
        flexWrap: "wrap",
        gap: 16,
      }}>
        <div>
          <div className="chip chip-indigo font-mono-tabular" style={{ marginBottom: 8, fontSize: "0.75rem" }}>
            MULTI-SITE AGGREGATOR + FAISS VECTOR SEARCH
          </div>
          <h1 style={{ fontSize: "2rem", fontWeight: 700 }}>Ranked Job Matches</h1>
          <p style={{ color: "#94A3B8", fontSize: "0.9rem", marginTop: 4 }}>
            {matches.length > 0
              ? `${matches.length} positions evaluated from LinkedIn, Arbeitnow, WeWorkRemotely, Remotive & RemoteOK`
              : "Upload your CV signal to compute instant ranked position scores"}
          </p>
        </div>

        <div style={{ display: "flex", gap: 10 }}>
          <button className="btn-control-secondary" onClick={() => navigate("/upload")}>
            <Upload size={15} /> Upload Signal CV
          </button>
          <button
            id="run-match-btn"
            className="btn-control-primary"
            onClick={runMatch}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spin-icon">⟳</span> Finding Matches...
              </>
            ) : (
              <>
                <RefreshCw size={15} /> Find Matches
              </>
            )}
          </button>
        </div>
      </div>

      {/* Advanced Filter Control Bar */}
      {matches.length > 0 && (
        <div className="control-panel" style={{ padding: 18, marginBottom: 24, display: "flex", flexDirection: "column", gap: 14 }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            {/* Title / Keyword Search Input */}
            <div style={{ position: "relative" }}>
              <Search size={15} color="#64748B" style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)" }} />
              <input
                className="control-input"
                type="text"
                placeholder="Search job title, company, or tech skill..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                style={{ paddingLeft: 36, fontSize: "0.85rem" }}
              />
            </div>

            {/* Location Search Input */}
            <div style={{ position: "relative" }}>
              <MapPin size={15} color="#64748B" style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)" }} />
              <input
                className="control-input"
                type="text"
                placeholder="Filter location (e.g. Remote, Germany, US, Berlin)..."
                value={locationQuery}
                onChange={(e) => setLocationQuery(e.target.value)}
                style={{ paddingLeft: 36, fontSize: "0.85rem" }}
              />
            </div>
          </div>

          {/* Filter Chips: Work Mode & Job Website Source */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12, borderTop: "1px solid var(--border-subtle)", paddingTop: 12 }}>
            {/* Work Mode Selector */}
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span className="font-mono-tabular" style={{ fontSize: "0.75rem", fontWeight: 700, color: "#64748B", textTransform: "uppercase" }}>
                Work Mode:
              </span>
              {["All", "Remote", "Onsite", "Hybrid"].map((mode) => (
                <button
                  key={mode}
                  onClick={() => setSelectedWorkMode(mode)}
                  style={{
                    padding: "4px 10px",
                    borderRadius: 6,
                    fontSize: "0.78rem",
                    fontWeight: selectedWorkMode === mode ? 700 : 500,
                    color: selectedWorkMode === mode ? "#ffffff" : "#94A3B8",
                    background: selectedWorkMode === mode ? "var(--accent-indigo)" : "rgba(255, 255, 255, 0.04)",
                    border: selectedWorkMode === mode ? "1px solid var(--border-focus)" : "1px solid var(--border-subtle)",
                    cursor: "pointer",
                    transition: "all 0.15s ease",
                  }}
                >
                  {mode}
                </button>
              ))}
            </div>

            {/* Website Source Selector */}
            <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
              <span className="font-mono-tabular" style={{ fontSize: "0.75rem", fontWeight: 700, color: "#64748B", textTransform: "uppercase" }}>
                Source:
              </span>
              {["All", "LinkedIn", "Arbeitnow", "WeWorkRemotely", "Remotive", "RemoteOK"].map((src) => (
                <button
                  key={src}
                  onClick={() => setSelectedSource(src)}
                  style={{
                    padding: "4px 10px",
                    borderRadius: 6,
                    fontSize: "0.78rem",
                    fontWeight: selectedSource === src ? 700 : 500,
                    color: selectedSource === src ? "#ffffff" : "#94A3B8",
                    background: selectedSource === src ? "var(--accent-indigo)" : "rgba(255, 255, 255, 0.04)",
                    border: selectedSource === src ? "1px solid var(--border-focus)" : "1px solid var(--border-subtle)",
                    cursor: "pointer",
                    transition: "all 0.15s ease",
                  }}
                >
                  {src}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Async Loading Skeleton */}
      {fetching ? (
        <div style={{ display: "grid", gap: 14 }}>
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="control-panel skeleton-box" style={{ height: 96 }} />
          ))}
        </div>
      ) : matches.length === 0 ? (
        <div className="control-panel" style={{ textAlign: "center", padding: "64px 24px" }}>
          <div style={{
            width: 56,
            height: 56,
            borderRadius: 12,
            background: "rgba(99, 102, 241, 0.1)",
            border: "1px solid var(--border-focus)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 20px auto",
          }}>
            <SlidersHorizontal size={26} color="#6366F1" />
          </div>
          <h2 style={{ fontSize: "1.3rem", fontWeight: 700, marginBottom: 8 }}>No Signal Matches Processed</h2>
          <p style={{ color: "#94A3B8", fontSize: "0.9rem", maxWidth: 440, margin: "0 auto 24px auto" }}>
            Upload your resume signal first, then click "Find Matches" to execute FAISS vector search across 220+ embedded positions.
          </p>
          <button className="btn-control-primary" onClick={runMatch} disabled={loading}>
            {loading ? (
              <>
                <span className="spin-icon">⟳</span> Finding Matches...
              </>
            ) : (
              <>Find Matches Now</>
            )}
          </button>
        </div>
      ) : filteredMatches.length === 0 ? (
        <div className="control-panel" style={{ textAlign: "center", padding: "48px 24px" }}>
          <p style={{ color: "#94A3B8", fontSize: "0.95rem" }}>
            No jobs match your current location, work mode, or source filter criteria.
          </p>
          <button
            className="btn-control-secondary"
            onClick={() => { setSelectedSource("All"); setSelectedWorkMode("All"); setQuery(""); setLocationQuery(""); }}
            style={{ marginTop: 16 }}
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div style={{ display: "grid", gap: 14 }}>
          {filteredMatches.map((m) => (
            <JobCard key={m.job_id} match={m} onSelect={(m) => navigate(`/jobs/${m.job_id}`)} />
          ))}
        </div>
      )}
    </div>
  );
}
