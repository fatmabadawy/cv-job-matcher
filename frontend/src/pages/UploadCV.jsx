import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import { addToast } from "../components/Toast";
import { UploadCloud, FileText, CheckCircle2, ArrowRight, Layers, Award, BookOpen, FileCheck, Radio } from "lucide-react";

export default function UploadCV() {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const inputRef = useRef();
  const navigate = useNavigate();

  function handleDrop(e) {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) setFile(f);
  }

  async function handleUpload() {
    if (!file) {
      addToast("Please select a CV signal file first", "error");
      return;
    }
    setLoading(true);
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await client.post("/cv/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
      addToast("CV signal uploaded and parsed successfully", "success");
    } catch (err) {
      addToast(err.response?.data?.detail || "Upload failed", "error");
    } finally {
      setLoading(false);
    }
  }

  const sd = result?.structured_data;

  return (
    <div style={{ maxWidth: 800, margin: "32px auto", padding: "0 24px" }}>
      {/* Title Header */}
      <div style={{ marginBottom: 28 }}>
        <div className="chip chip-indigo font-mono-tabular" style={{ marginBottom: 8, fontSize: "0.75rem" }}>
          GROQ LLM SIGNAL EXTRACTOR
        </div>
        <h1 style={{ fontSize: "2rem", fontWeight: 700 }}>Upload Candidate CV Signal</h1>
        <p style={{ color: "#94A3B8", fontSize: "0.9rem", marginTop: 4 }}>
          Upload your PDF, DOCX, or TXT file. Groq LLM will automatically parse structured skills and seniority for vector matching.
        </p>
      </div>

      {/* Control Panel Dropzone */}
      <div className="control-panel" style={{ padding: 32, marginBottom: 24 }}>
        <div
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          style={{
            border: `2px dashed ${dragging ? "#6366F1" : file ? "#10B981" : "rgba(255, 255, 255, 0.1)"}`,
            borderRadius: 10,
            padding: "44px 20px",
            textAlign: "center",
            cursor: "pointer",
            transition: "all 0.2s ease",
            background: dragging
              ? "rgba(99, 102, 241, 0.1)"
              : file
              ? "rgba(16, 185, 129, 0.05)"
              : "rgba(10, 12, 16, 0.6)",
          }}
        >
          <div style={{
            width: 52,
            height: 52,
            borderRadius: 12,
            background: file ? "rgba(16, 185, 129, 0.15)" : "rgba(99, 102, 241, 0.12)",
            border: `1px solid ${file ? "#10B981" : "#6366F1"}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 16px auto",
          }}>
            {file ? <FileCheck size={26} color="#10B981" /> : <UploadCloud size={26} color="#6366F1" />}
          </div>

          {file ? (
            <>
              <p style={{ fontWeight: 700, fontSize: "1rem", color: "#10B981" }}>{file.name}</p>
              <p className="font-mono-tabular" style={{ color: "#94A3B8", fontSize: "0.82rem", marginTop: 4 }}>
                {(file.size / 1024).toFixed(1)} KB — Ready to parse signal
              </p>
            </>
          ) : (
            <>
              <p style={{ fontWeight: 700, fontSize: "1rem", color: "#F1F5F9", marginBottom: 4 }}>
                Drop resume signal here or click to browse
              </p>
              <p style={{ color: "#64748B", fontSize: "0.84rem" }}>
                Supports PDF, DOCX, or TXT (Max 10MB)
              </p>
            </>
          )}

          <input ref={inputRef} type="file" accept=".pdf,.docx,.txt" style={{ display: "none" }} onChange={(e) => setFile(e.target.files[0])} />
        </div>

        <div style={{ display: "flex", gap: 12, marginTop: 24, justifyContent: "flex-end" }}>
          <button
            id="upload-cv-btn"
            className="btn-control-primary"
            onClick={handleUpload}
            disabled={!file || loading}
          >
            {loading ? (
              <>
                <span className="spin-icon">⟳</span> Uploading CV Signal...
              </>
            ) : (
              <>
                <Radio size={16} /> Upload Signal & Parse
              </>
            )}
          </button>

          {result && (
            <button className="btn-control-secondary" onClick={() => navigate("/matches")}>
              <span>Find Matches</span> <ArrowRight size={15} />
            </button>
          )}
        </div>
      </div>

      {/* Extracted Signal Breakdown */}
      {sd && (
        <div className="control-panel" style={{ padding: 28 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20, borderBottom: "1px solid var(--border-subtle)", paddingBottom: 14 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <CheckCircle2 size={20} color="#10B981" />
              <h2 style={{ fontSize: "1.2rem", fontWeight: 700 }}>Parsed Candidate Signal</h2>
            </div>
            <button className="btn-control-primary" onClick={() => navigate("/matches")} style={{ padding: "6px 12px", fontSize: "0.82rem" }}>
              Find Matches <ArrowRight size={14} />
            </button>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 20 }}>
            <ProfileItem icon={Layers} label="Summary" value={sd.summary || "No summary extracted"} span />
            <ProfileItem icon={Award} label="Seniority Level" value={sd.seniority || "Junior / Associate"} />
            <ProfileItem icon={BookOpen} label="Education" value={sd.education || "Degree / Coursework"} />
          </div>

          {sd.skills?.length > 0 && (
            <div>
              <div className="font-mono-tabular" style={{ fontSize: "0.78rem", fontWeight: 700, color: "#94A3B8", textTransform: "uppercase", letterSpacing: "0.04em", marginBottom: 8 }}>
                PARSED TECHNICAL SKILLS ({sd.skills.length})
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {sd.skills.map((skill, i) => (
                  <span key={i} className="chip chip-indigo font-mono-tabular" style={{ fontSize: "0.82rem" }}>
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ProfileItem({ icon: Icon, label, value, span }) {
  return (
    <div style={{
      gridColumn: span ? "1 / -1" : undefined,
      background: "rgba(10, 12, 16, 0.6)",
      padding: 14,
      borderRadius: 8,
      border: "1px solid var(--border-subtle)",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, color: "#64748B", fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.04em", marginBottom: 4 }}>
        <Icon size={13} color="#6366F1" /> {label}
      </div>
      <div style={{ fontSize: "0.9rem", color: "#F1F5F9", fontWeight: 500 }}>
        {value}
      </div>
    </div>
  );
}
