import { Link, useLocation, useNavigate } from "react-router-dom";
import { Activity, UploadCloud, Kanban, Settings, LogOut, Radio } from "lucide-react";

const NAV_ITEMS = [
  { path: "/matches", label: "Ranked Matches", icon: Activity },
  { path: "/upload", label: "Upload Signal", icon: UploadCloud },
  { path: "/applications", label: "Pipeline", icon: Kanban },
  { path: "/settings", label: "System Config", icon: Settings },
];

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  if (!token && location.pathname !== "/login") {
    return null;
  }

  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user_id");
    navigate("/login");
  }

  return (
    <header style={{
      background: "rgba(20, 22, 26, 0.95)",
      backdropFilter: "blur(12px)",
      borderBottom: "1px solid var(--border-subtle)",
      position: "sticky",
      top: 0,
      zIndex: 100,
      padding: "0 24px",
    }}>
      <div style={{
        maxWidth: 1240,
        margin: "0 auto",
        height: 64,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: 16,
      }}>
        {/* Brand Logo & Signal Status */}
        <Link to="/matches" style={{
          textDecoration: "none",
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}>
          <div style={{
            width: 36,
            height: 36,
            borderRadius: 8,
            background: "rgba(99, 102, 241, 0.15)",
            border: "1px solid rgba(99, 102, 241, 0.3)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}>
            <Radio size={20} color="#6366F1" />
          </div>
          <div>
            <div style={{
              fontFamily: "var(--font-display)",
              fontWeight: 700,
              fontSize: "1.15rem",
              lineHeight: 1.1,
              color: "#F1F5F9",
              display: "flex",
              alignItems: "center",
              gap: 6,
            }}>
              JOB<span style={{ color: "#6366F1" }}>SIGNAL</span>
            </div>
            <div className="font-mono-tabular" style={{ fontSize: "0.68rem", color: "#64748B", letterSpacing: "0.04em" }}>
              MATCH ENGINE v2.4
            </div>
          </div>
        </Link>

        {/* Control Room Navigation Tabs */}
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: 4,
          background: "rgba(10, 12, 16, 0.6)",
          padding: "4px",
          borderRadius: 8,
          border: "1px solid var(--border-subtle)",
        }}>
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  padding: "7px 14px",
                  borderRadius: 6,
                  textDecoration: "none",
                  fontSize: "0.85rem",
                  fontWeight: active ? 600 : 500,
                  color: active ? "#F1F5F9" : "#94A3B8",
                  background: active ? "var(--panel-surface)" : "transparent",
                  border: active ? "1px solid var(--border-focus)" : "1px solid transparent",
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  transition: "all 0.15s ease",
                }}
              >
                <Icon size={15} color={active ? "#6366F1" : "#64748B"} />
                {item.label}
              </Link>
            );
          })}
        </div>

        {/* Signal Active Status & Sign Out */}
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div className="chip chip-emerald font-mono-tabular" style={{ padding: "5px 10px", fontSize: "0.75rem" }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#10B981", display: "inline-block" }} />
            222 JOBS EMBEDDED
          </div>

          <button className="btn-control-secondary" onClick={logout} style={{ padding: "7px 12px", fontSize: "0.82rem" }}>
            <LogOut size={14} />
            Sign Out
          </button>
        </div>
      </div>
    </header>
  );
}
