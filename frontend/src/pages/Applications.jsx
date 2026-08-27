import { useState, useEffect } from "react";
import client from "../api/client";
import { addToast } from "../components/Toast";
import { Kanban as KanbanIcon, MoreVertical, Trash2, ArrowRight, Building2 } from "lucide-react";

const COLUMNS = ["applied", "screening", "interview", "offer", "rejected"];
const COLUMN_LABELS = {
  applied: "APPLIED",
  screening: "SCREENING",
  interview: "INTERVIEW",
  offer: "OFFER ACCEPTED",
  rejected: "REJECTED",
};

const COLUMN_COLORS = {
  applied: "#6366F1",
  screening: "#38BDF8",
  interview: "#F59E0B",
  offer: "#10B981",
  rejected: "#F43F5E",
};

function KanbanCard({ app, onStatusChange, onDelete }) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div
      className="control-panel control-panel-interactive"
      style={{ padding: 14, position: "relative" }}
      id={`app-card-${app.id}`}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <p style={{ fontWeight: 700, fontSize: "0.9rem", color: "#F1F5F9", marginBottom: 2 }}>
            {app.job?.title || `Job #${app.job_id}`}
          </p>
          <p style={{ color: "#94A3B8", fontSize: "0.8rem", display: "flex", alignItems: "center", gap: 4 }}>
            <Building2 size={13} color="#6366F1" /> {app.job?.company || "Company"}
          </p>
          {app.notes && (
            <p style={{ fontSize: "0.75rem", color: "#64748B", marginTop: 6 }}>
              {app.notes}
            </p>
          )}
        </div>

        <div style={{ position: "relative" }}>
          <button
            className="btn-control-secondary"
            style={{ padding: "4px 6px", borderRadius: 6 }}
            onClick={() => setMenuOpen(!menuOpen)}
          >
            <MoreVertical size={14} />
          </button>

          {menuOpen && (
            <div style={{
              position: "absolute",
              right: 0,
              top: "100%",
              marginTop: 4,
              background: "#1C1F26",
              border: "1px solid var(--border-subtle)",
              borderRadius: 8,
              zIndex: 50,
              minWidth: 160,
              padding: 4,
              boxShadow: "0 8px 24px rgba(0,0,0,0.5)",
            }}>
              <div className="font-mono-tabular" style={{ fontSize: "0.7rem", fontWeight: 700, color: "#64748B", padding: "4px 8px" }}>
                STAGE TRANSITION
              </div>
              {COLUMNS.filter((c) => c !== app.status).map((s) => (
                <button
                  key={s}
                  onClick={() => { onStatusChange(app.id, s); setMenuOpen(false); }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                    width: "100%",
                    padding: "6px 8px",
                    textAlign: "left",
                    background: "transparent",
                    border: "none",
                    color: "#F1F5F9",
                    fontSize: "0.8rem",
                    cursor: "pointer",
                    borderRadius: 4,
                  }}
                >
                  <ArrowRight size={12} color={COLUMN_COLORS[s]} /> {COLUMN_LABELS[s]}
                </button>
              ))}

              <div style={{ height: 1, background: "var(--border-subtle)", margin: "4px 0" }} />

              <button
                onClick={() => { onDelete(app.id); setMenuOpen(false); }}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  width: "100%",
                  padding: "6px 8px",
                  textAlign: "left",
                  background: "transparent",
                  border: "none",
                  color: "#F43F5E",
                  fontSize: "0.8rem",
                  cursor: "pointer",
                  borderRadius: 4,
                }}
              >
                <Trash2 size={12} /> Remove Signal
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function Applications() {
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get("/applications")
      .then((res) => setApps(res.data))
      .catch(() => addToast("Failed to load applications", "error"))
      .finally(() => setLoading(false));
  }, []);

  async function handleStatusChange(appId, newStatus) {
    try {
      const res = await client.patch(`/applications/${appId}`, { status: newStatus });
      setApps((prev) => prev.map((a) => a.id === appId ? { ...a, status: res.data.status } : a));
      addToast(`Moved to ${COLUMN_LABELS[newStatus]}`, "success");
    } catch {
      addToast("Failed to update status", "error");
    }
  }

  async function handleDelete(appId) {
    try {
      await client.delete(`/applications/${appId}`);
      setApps((prev) => prev.filter((a) => a.id !== appId));
      addToast("Application removed", "info");
    } catch {
      addToast("Failed to delete", "error");
    }
  }

  return (
    <div style={{ maxWidth: 1200, margin: "32px auto", padding: "0 24px" }}>
      <div style={{ marginBottom: 28 }}>
        <div className="chip chip-indigo font-mono-tabular" style={{ marginBottom: 8, fontSize: "0.75rem" }}>
          SIGNAL APPLICATION PIPELINE
        </div>
        <h1 style={{ fontSize: "2rem", fontWeight: 700 }}>Application Pipeline</h1>
        <p style={{ color: "#94A3B8", fontSize: "0.9rem", marginTop: 4 }}>
          {apps.length} active position application{apps.length !== 1 ? "s" : ""} tracked in pipeline
        </p>
      </div>

      {loading ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 14 }}>
          {COLUMNS.map((c) => (
            <div key={c} className="control-panel skeleton-box" style={{ height: 220 }} />
          ))}
        </div>
      ) : apps.length === 0 ? (
        <div className="control-panel" style={{ textAlign: "center", padding: "64px 24px" }}>
          <div style={{
            width: 52,
            height: 52,
            borderRadius: 12,
            background: "rgba(99, 102, 241, 0.1)",
            border: "1px solid var(--border-focus)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 16px auto",
          }}>
            <KanbanIcon size={26} color="#6366F1" />
          </div>
          <h2 style={{ fontSize: "1.3rem", fontWeight: 700, marginBottom: 8 }}>No Tracked Applications Yet</h2>
          <p style={{ color: "#94A3B8", fontSize: "0.9rem", maxWidth: 420, margin: "0 auto 20px auto" }}>
            Select a job position from your matches and click "Mark as Applied" to track interview stage progress here.
          </p>
        </div>
      ) : (
        <div style={{
          display: "grid",
          gridTemplateColumns: `repeat(${COLUMNS.length}, 1fr)`,
          gap: 14,
          alignItems: "start",
          overflowX: "auto",
        }}>
          {COLUMNS.map((col) => {
            const colApps = apps.filter((a) => a.status === col);
            return (
              <div key={col}>
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: 14,
                  padding: "8px 12px",
                  borderRadius: 8,
                  background: "rgba(10, 12, 16, 0.8)",
                  border: `1px solid ${COLUMN_COLORS[col]}33`,
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <div style={{ width: 6, height: 6, borderRadius: "50%", background: COLUMN_COLORS[col] }} />
                    <span className="font-mono-tabular" style={{ fontWeight: 700, fontSize: "0.78rem", color: "#F1F5F9" }}>{COLUMN_LABELS[col]}</span>
                  </div>
                  <span className="chip chip-slate font-mono-tabular" style={{ fontSize: "0.72rem", padding: "1px 6px" }}>
                    {colApps.length}
                  </span>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {colApps.map((app) => (
                    <KanbanCard
                      key={app.id}
                      app={app}
                      onStatusChange={handleStatusChange}
                      onDelete={handleDelete}
                    />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
