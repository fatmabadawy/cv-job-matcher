import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import client from "../api/client";
import { addToast } from "../components/Toast";
import ScoreGauge from "../components/ScoreGauge";
import { ArrowLeft, ExternalLink, Building2, MapPin, Copy, Download, X, Target, CheckSquare, Sparkles } from "lucide-react";

function FeatureModal({ title, content, onClose }) {
  return (
    <div style={{
      position: "fixed",
      inset: 0,
      background: "rgba(10, 12, 16, 0.85)",
      backdropFilter: "blur(8px)",
      zIndex: 1000,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: 24,
    }} onClick={onClose}>
      <div className="control-panel" onClick={(e) => e.stopPropagation()} style={{
        maxWidth: 720,
        width: "100%",
        maxHeight: "85vh",
        overflowY: "auto",
        padding: 28,
        borderColor: "var(--border-focus)",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20, borderBottom: "1px solid var(--border-subtle)", paddingBottom: 14 }}>
          <h2 style={{ fontSize: "1.3rem", fontWeight: 700, display: "flex", alignItems: "center", gap: 10 }}>
            <Sparkles size={18} color="#6366F1" /> {title}
          </h2>
          <button className="btn-control-secondary" onClick={onClose} style={{ padding: "5px 10px", borderRadius: 6 }}>
            <X size={16} />
          </button>
        </div>
        {content}
      </div>
    </div>
  );
}

function TailorCVContent({ data }) {
  const [copied, setCopied] = useState(false);

  const fullText = [
    `TAILORED PROFESSIONAL SUMMARY:`,
    data.tailored_summary,
    `\nPRIORITIZED TECH SKILLS:`,
    data.tailored_skills?.join(", "),
    `\nOPTIMIZED EXPERIENCE BULLETS:`,
    ...(data.tailored_experience_bullets?.map((b) => `• ${b}`) || []),
  ].join("\n");

  function copyToClipboard() {
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function downloadCV() {
    const element = document.createElement("a");
    const file = new Blob([fullText], { type: "text/plain" });
    element.href = URL.createObjectURL(file);
    element.download = "Tailored_Resume_Content.txt";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
      {data.key_adjustments_made?.length > 0 && (
        <div style={{ background: "rgba(99, 102, 241, 0.1)", border: "1px solid rgba(99, 102, 241, 0.25)", padding: 16, borderRadius: 8 }}>
          <p style={{ fontWeight: 700, fontSize: "0.88rem", color: "#a5b4fc", marginBottom: 6, display: "flex", alignItems: "center", gap: 6 }}>
            <Target size={15} color="#6366F1" /> Strategic Enhancements Made
          </p>
          <ul style={{ paddingLeft: 16, fontSize: "0.86rem", color: "#94A3B8", display: "flex", flexDirection: "column", gap: 4 }}>
            {data.key_adjustments_made.map((adj, i) => (
              <li key={i}>{adj}</li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <p style={{ fontWeight: 700, fontSize: "0.88rem", color: "#94A3B8", marginBottom: 6 }}>Tailored Professional Summary</p>
        <div style={{ background: "rgba(10, 12, 16, 0.8)", padding: 14, borderRadius: 8, border: "1px solid var(--border-subtle)", fontSize: "0.9rem", lineHeight: 1.6, color: "#F1F5F9" }}>
          {data.tailored_summary}
        </div>
      </div>

      {data.tailored_skills?.length > 0 && (
        <div>
          <p style={{ fontWeight: 700, fontSize: "0.88rem", color: "#94A3B8", marginBottom: 6 }}>Prioritized Skills for this Position</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {data.tailored_skills.map((s) => (
              <span key={s} className="chip chip-indigo">{s}</span>
            ))}
          </div>
        </div>
      )}

      {data.tailored_experience_bullets?.length > 0 && (
        <div>
          <p style={{ fontWeight: 700, fontSize: "0.88rem", color: "#94A3B8", marginBottom: 6 }}>Optimized Experience Bullet Points</p>
          <ul style={{ paddingLeft: 16, display: "flex", flexDirection: "column", gap: 6 }}>
            {data.tailored_experience_bullets.map((bullet, i) => (
              <li key={i} style={{ fontSize: "0.88rem", lineHeight: 1.6, color: "#F1F5F9" }}>{bullet}</li>
            ))}
          </ul>
        </div>
      )}

      <div style={{ display: "flex", gap: 10, marginTop: 8 }}>
        <button className="btn-control-secondary" onClick={copyToClipboard}>
          <Copy size={15} /> {copied ? "Copied!" : "Copy Tailored Content"}
        </button>
        <button className="btn-control-primary" onClick={downloadCV}>
          <Download size={15} /> Download (.txt)
        </button>
      </div>
    </div>
  );
}

function CoverLetterContent({ data }) {
  const [copied, setCopied] = useState(false);
  return (
    <div>
      <div style={{
        background: "rgba(10, 12, 16, 0.8)",
        borderRadius: 8,
        border: "1px solid var(--border-subtle)",
        padding: 18,
        whiteSpace: "pre-wrap",
        fontSize: "0.9rem",
        lineHeight: 1.75,
        color: "#F1F5F9",
        marginBottom: 16,
        maxHeight: 360,
        overflowY: "auto",
      }}>{data.cover_letter}</div>

      <button className="btn-control-primary" onClick={() => { navigator.clipboard.writeText(data.cover_letter); setCopied(true); setTimeout(() => setCopied(false), 2000); }}>
        <Copy size={15} /> {copied ? "Copied!" : "Copy Cover Letter"}
      </button>
    </div>
  );
}

function GapContent({ data }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {data.missing_skills?.length > 0 && (
        <div>
          <p style={{ fontWeight: 700, fontSize: "0.88rem", color: "#F43F5E", marginBottom: 6 }}>Missing Skill Requirements</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {data.missing_skills.map((s) => <span key={s} className="chip chip-slate font-mono-tabular" style={{ color: "#F43F5E" }}>{s}</span>)}
          </div>
        </div>
      )}
      {data.recommendations?.length > 0 && (
        <div>
          <p style={{ fontWeight: 700, fontSize: "0.88rem", color: "#10B981", marginBottom: 6 }}>Gap Mitigation Advice</p>
          <ul style={{ paddingLeft: 16, display: "flex", flexDirection: "column", gap: 4 }}>
            {data.recommendations.map((r, i) => <li key={i} style={{ fontSize: "0.86rem", color: "#94A3B8" }}>{r}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}

function ATSContent({ data }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
      <div style={{ textAlign: "center", padding: 12 }}>
        <div className="font-mono-tabular" style={{
          fontSize: "3rem",
          fontWeight: 700,
          color: data.ats_score >= 75 ? "#10B981" : data.ats_score >= 45 ? "#6366F1" : "#64748B",
          lineHeight: 1,
        }}>{data.ats_score}%</div>
        <p style={{ color: "#94A3B8", fontSize: "0.85rem", marginTop: 4 }}>ATS Keyword Compatibility Score</p>
      </div>

      {data.matched_keywords?.length > 0 && (
        <div>
          <p style={{ fontWeight: 700, fontSize: "0.88rem", color: "#10B981", marginBottom: 6 }}>Matched Keywords</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {data.matched_keywords.slice(0, 15).map((k) => <span key={k} className="chip chip-emerald">{k}</span>)}
          </div>
        </div>
      )}
    </div>
  );
}

function InterviewContent({ data }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {data.likely_questions?.length > 0 && (
        <div>
          <p style={{ fontWeight: 700, fontSize: "1rem", marginBottom: 12 }}>Expected Technical Interview Questions</p>
          {data.likely_questions.map((q, i) => (
            <div key={i} style={{ marginBottom: 10, padding: 14, background: "rgba(10, 12, 16, 0.8)", borderRadius: 8, border: "1px solid var(--border-subtle)" }}>
              <p style={{ fontWeight: 700, fontSize: "0.9rem", color: "#F1F5F9", marginBottom: 4 }}>Q{i + 1}: {q.question}</p>
              <p style={{ fontSize: "0.84rem", color: "#94A3B8" }}>💡 {q.tips}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function JobDetail() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [modal, setModal] = useState(null);
  const [featureLoading, setFeatureLoading] = useState(null);
  const [applying, setApplying] = useState(false);

  useEffect(() => {
    client.get("/match/results").then((res) => {
      const m = res.data.find((m) => m.job_id === Number(jobId));
      if (m) setJob(m);
    });
  }, [jobId]);

  async function runFeature(name, endpoint, loadingLabel, renderFn) {
    setFeatureLoading(name);
    try {
      const res = await client.post(`/features/${endpoint}`, { job_id: Number(jobId) });
      setModal({ title: name, content: renderFn(res.data) });
    } catch (err) {
      addToast(err.response?.data?.detail || `${name} calculation failed`, "error");
    } finally {
      setFeatureLoading(null);
    }
  }

  async function applyNow() {
    setApplying(true);
    try {
      await client.post("/applications", { job_id: Number(jobId) });
      addToast("Tracked in Pipeline! 📋", "success");
    } catch (err) {
      addToast(err.response?.data?.detail || "Could not track application", "error");
    } finally {
      setApplying(false);
    }
  }

  if (!job) return (
    <div style={{ textAlign: "center", paddingTop: 80, color: "#94A3B8" }}>
      <span className="spin-icon" style={{ fontSize: "1.5rem" }}>⟳</span> Loading position details...
    </div>
  );

  const features = [
    { name: "Tailor My CV", id: "tailor-cv", endpoint: "tailor-cv", loadingLabel: "Tailoring CV Signal...", render: (d) => <TailorCVContent data={d} /> },
    { name: "Cover Letter", id: "cover-letter", endpoint: "cover-letter", loadingLabel: "Generating Cover Letter...", render: (d) => <CoverLetterContent data={d} /> },
    { name: "Gap Analysis", id: "gap-analysis", endpoint: "gap-analysis", loadingLabel: "Analyzing Skill Gaps...", render: (d) => <GapContent data={d} /> },
    { name: "ATS Check", id: "ats-check", endpoint: "ats-check", loadingLabel: "Running ATS Check...", render: (d) => <ATSContent data={d} /> },
    { name: "Interview Prep", id: "interview-prep", endpoint: "interview-prep", loadingLabel: "Preparing Interview Q&A...", render: (d) => <InterviewContent data={d} /> },
  ];

  return (
    <div style={{ maxWidth: 1040, margin: "32px auto", padding: "0 24px" }}>
      {/* Navigation Breadcrumb */}
      <button className="btn-control-secondary" onClick={() => navigate("/matches")} style={{ marginBottom: 24, gap: 6, padding: "6px 12px", fontSize: "0.84rem" }}>
        <ArrowLeft size={14} /> Return to Ranked Matches
      </button>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 320px", gap: 24, alignItems: "start" }} className="responsive-grid-detail">
        {/* Left Column: Job Overview & Full Description */}
        <div>
          {/* Header Control Panel */}
          <div className="control-panel" style={{ padding: 28, marginBottom: 20 }}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: 20, flexWrap: "wrap" }}>
              {/* Signature Score Gauge */}
              <ScoreGauge score={job.score} size={76} strokeWidth={6} />

              <div style={{ flex: 1, minWidth: 240 }}>
                <h1 style={{ fontSize: "1.6rem", fontWeight: 700, color: "#F1F5F9", marginBottom: 6 }}>{job.title}</h1>
                <div style={{ display: "flex", alignItems: "center", gap: 16, color: "#94A3B8", fontSize: "0.88rem", marginBottom: 16 }}>
                  <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <Building2 size={15} color="#6366F1" /> {job.company}
                  </span>
                  <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <MapPin size={15} color="#64748B" /> {job.location || "Remote"}
                  </span>
                </div>

                {job.link && (
                  <a
                    id="original-posting-link"
                    href={job.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-control-secondary"
                    style={{ padding: "8px 14px", fontSize: "0.85rem", display: "inline-flex" }}
                  >
                    <span>View Original Web Posting</span> <ExternalLink size={14} />
                  </a>
                )}
              </div>
            </div>
          </div>

          {/* Full Job Description */}
          <div className="control-panel" style={{ padding: 28, marginBottom: 20 }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: 14, color: "#F1F5F9" }}>
              Full Job Description
            </h3>
            {job.description ? (
              <div
                style={{
                  fontSize: "0.92rem",
                  lineHeight: 1.75,
                  color: "#F1F5F9",
                  whiteSpace: "pre-line",
                }}
              >
                {job.description}
              </div>
            ) : (
              <p style={{ color: "#94A3B8", fontSize: "0.88rem" }}>No full description text provided for this listing.</p>
            )}
          </div>

          {/* Requirements & Tags */}
          {job.requirements && (
            <div className="control-panel" style={{ padding: 24 }}>
              <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: 12, color: "#F1F5F9" }}>
                Key Technical Tags
              </h3>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {job.requirements.split(",").map((r) => r.trim()).filter(Boolean).map((r, i) => (
                  <span key={i} className="chip chip-indigo font-mono-tabular" style={{ fontSize: "0.78rem" }}>
                    {r}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: AI Suite Controls & Application Tracker */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="control-panel" style={{ padding: 22 }}>
            <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: 14, display: "flex", alignItems: "center", gap: 8 }}>
              <Sparkles size={16} color="#6366F1" /> AI Signal Acceleration Tools
            </h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {features.map((f) => {
                const isLoading = featureLoading === f.name;
                return (
                  <button
                    key={f.id}
                    id={`feature-${f.id}`}
                    className={f.id === "tailor-cv" ? "btn-control-primary" : "btn-control-secondary"}
                    style={{ width: "100%", justifyContent: "flex-start", padding: "10px 14px" }}
                    onClick={() => runFeature(f.name, f.endpoint, f.loadingLabel, f.render)}
                    disabled={featureLoading !== null}
                  >
                    {isLoading ? (
                      <>
                        <span className="spin-icon">⟳</span> {f.loadingLabel}
                      </>
                    ) : (
                      <span>{f.name}</span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="control-panel" style={{ padding: 22 }}>
            <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: 12 }}>Pipeline Status</h3>
            <button
              id="apply-btn"
              className="btn-control-primary"
              style={{ width: "100%", justifyContent: "center" }}
              onClick={applyNow}
              disabled={applying}
            >
              {applying ? (
                <>
                  <span className="spin-icon">⟳</span> Marking Applied...
                </>
              ) : (
                <>
                  <CheckSquare size={15} /> Mark as Applied
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {modal && (
        <FeatureModal
          title={modal.title}
          content={modal.content}
          onClose={() => setModal(null)}
        />
      )}
    </div>
  );
}
