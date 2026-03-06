import { useState } from "react";
import { STATUS_CONFIG, PRIORITY_CONFIG } from "../constants/config";

export default function JobCard({ job, onDelete, onStatusChange, onEdit }) {
  const [expanded, setExpanded] = useState(false);
  const status = STATUS_CONFIG[job.status];
  const priority = PRIORITY_CONFIG[job.priority];

  return (
    <div
      style={{
        background: "rgba(255,255,255,0.03)",
        border: "1px solid rgba(255,255,255,0.07)",
        borderRadius: "18px",
        overflow: "hidden",
        backdropFilter: "blur(20px)",
        transition: "all 0.3s ease",
        animation: "fadeSlideUp 0.5s ease both",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = "rgba(255,255,255,0.06)";
        e.currentTarget.style.borderColor = "rgba(255,255,255,0.13)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = "rgba(255,255,255,0.03)";
        e.currentTarget.style.borderColor = "rgba(255,255,255,0.07)";
      }}
    >
      <div
        style={{
          height: "2px",
          background: `linear-gradient(90deg, ${status.color}, transparent)`,
        }}
      />
      <div style={{ padding: "22px 24px" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            gap: "16px",
          }}
        >
          <div style={{ flex: 1, minWidth: 0 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "10px",
                marginBottom: "6px",
                flexWrap: "wrap",
              }}
            >
              <span
                style={{
                  fontSize: "17px",
                  fontWeight: "700",
                  color: "#f1f5f9",
                  fontFamily: "'Playfair Display', serif",
                }}
              >
                {job.title}
              </span>
              <span
                style={{
                  fontSize: "10px",
                  fontWeight: "600",
                  color: priority.color,
                  border: `1px solid ${priority.color}44`,
                  borderRadius: "6px",
                  padding: "2px 8px",
                  letterSpacing: "0.06em",
                  textTransform: "uppercase",
                }}
              >
                {priority.label}
              </span>
            </div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "16px",
                flexWrap: "wrap",
              }}
            >
              <span
                style={{
                  fontSize: "14px",
                  color: "rgba(255,255,255,0.55)",
                  fontWeight: "500",
                }}
              >
                🏢 {job.company}
              </span>
              <span style={{ fontSize: "13px", color: "rgba(255,255,255,0.35)" }}>
                📍 {job.location}
              </span>
              {job.salary_min && (
                <span style={{ fontSize: "13px", color: "rgba(255,255,255,0.35)" }}>
                  💰 {job.salary_min}–{job.salary_max} LPA
                </span>
              )}
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", flexShrink: 0 }}>
            <span
              style={{
                fontSize: "12px",
                fontWeight: "600",
                color: status.color,
                background: status.bg,
                border: `1px solid ${status.color}33`,
                borderRadius: "20px",
                padding: "5px 14px",
                letterSpacing: "0.04em",
              }}
            >
              <span
                style={{
                  display: "inline-block",
                  width: "6px",
                  height: "6px",
                  borderRadius: "50%",
                  background: status.dot,
                  marginRight: "6px",
                  verticalAlign: "middle",
                }}
              />
              {status.label}
            </span>
            <button
              onClick={() => setExpanded(!expanded)}
              style={{
                background: "rgba(255,255,255,0.06)",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "10px",
                padding: "6px 10px",
                cursor: "pointer",
                color: "rgba(255,255,255,0.6)",
                fontSize: "12px",
                transition: "all 0.2s",
              }}
            >
              {expanded ? "▲" : "▼"}
            </button>
          </div>
        </div>

        {expanded && (
          <div
            style={{
              marginTop: "18px",
              paddingTop: "18px",
              borderTop: "1px solid rgba(255,255,255,0.06)",
              animation: "fadeSlideUp 0.3s ease",
            }}
          >
            {job.notes && (
              <p
                style={{
                  fontSize: "13px",
                  color: "rgba(255,255,255,0.45)",
                  marginBottom: "16px",
                  fontStyle: "italic",
                }}
              >
                📝 {job.notes}
              </p>
            )}
            <div
              style={{
                display: "flex",
                gap: "10px",
                flexWrap: "wrap",
                alignItems: "center",
              }}
            >
              <span style={{ fontSize: "12px", color: "rgba(255,255,255,0.3)" }}>
                Update status:
              </span>
              {Object.entries(STATUS_CONFIG).map(([key, cfg]) => (
                <button
                  key={key}
                  onClick={() => onStatusChange(job.id, key)}
                  style={{
                    fontSize: "11px",
                    fontWeight: "600",
                    color: job.status === key ? cfg.color : "rgba(255,255,255,0.4)",
                    background: job.status === key ? cfg.bg : "transparent",
                    border: `1px solid ${
                      job.status === key ? cfg.color + "44" : "rgba(255,255,255,0.1)"
                    }`,
                    borderRadius: "8px",
                    padding: "4px 12px",
                    cursor: "pointer",
                    transition: "all 0.2s",
                  }}
                >
                  {cfg.label}
                </button>
              ))}
              <button
                onClick={() => onEdit(job)}
                style={{
                  fontSize: "11px",
                  color: "#60a5fa",
                  background: "rgba(96,165,250,0.1)",
                  border: "1px solid rgba(96,165,250,0.2)",
                  borderRadius: "8px",
                  padding: "4px 12px",
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
              >
                Edit
              </button>
              <button
                onClick={() => onDelete(job.id)}
                style={{
                  fontSize: "11px",
                  color: "#f87171",
                  background: "rgba(248,113,113,0.1)",
                  border: "1px solid rgba(248,113,113,0.2)",
                  borderRadius: "8px",
                  padding: "4px 12px",
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
              >
                Delete
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
