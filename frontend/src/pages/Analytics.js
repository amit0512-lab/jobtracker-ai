import { useEffect, useState } from "react";
import { analyticsAPI } from "../services/api";
import { STATUS_CONFIG, PRIORITY_CONFIG } from "../constants/config";
import { TopBannerAd, InFeedAd } from "../components/AdBanner";

export default function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const response = await analyticsAPI.getDashboard();
      setData(response.data);
    } catch (error) {
      console.error("Failed to load analytics:", error);
      setData({
        summary: { total_jobs: 0 },
        status_breakdown: {},
        priority_breakdown: {},
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "60px", color: "rgba(255,255,255,0.4)" }}>
        Loading...
      </div>
    );
  }

  if (!data) {
    return (
      <div style={{ textAlign: "center", padding: "60px", color: "rgba(255,255,255,0.4)" }}>
        No analytics data available
      </div>
    );
  }

  const statusCounts = Object.keys(STATUS_CONFIG).map((k) => ({
    key: k,
    count: data.status_breakdown?.[k] || 0,
    ...STATUS_CONFIG[k],
  }));

  const total = data.summary?.total_jobs || 1;

  return (
    <div style={{ animation: "fadeSlideUp 0.5s ease" }}>
      <h1
        style={{
          fontSize: "32px",
          fontWeight: "800",
          fontFamily: "'Playfair Display', serif",
          letterSpacing: "-0.02em",
          marginBottom: "8px",
        }}
      >
        Analytics
      </h1>
      <p style={{ color: "rgba(255,255,255,0.4)", fontSize: "14px", marginBottom: "32px" }}>
        Track your job search performance
      </p>

      <TopBannerAd />

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        {/* Status Breakdown */}
        <div
          style={{
            background: "rgba(255,255,255,0.03)",
            border: "1px solid rgba(255,255,255,0.07)",
            borderRadius: "20px",
            padding: "28px",
            backdropFilter: "blur(20px)",
          }}
        >
          <h3
            style={{
              margin: "0 0 24px",
              fontSize: "16px",
              color: "rgba(255,255,255,0.7)",
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              fontWeight: "600",
            }}
          >
            Status Breakdown
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
            {statusCounts.map((s) => (
              <div key={s.key}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: "6px",
                  }}
                >
                  <span style={{ fontSize: "13px", color: s.color, fontWeight: "600" }}>
                    {s.label}
                  </span>
                  <span style={{ fontSize: "13px", color: "rgba(255,255,255,0.4)" }}>
                    {s.count} / {total}
                  </span>
                </div>
                <div
                  style={{
                    height: "6px",
                    background: "rgba(255,255,255,0.06)",
                    borderRadius: "3px",
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      height: "100%",
                      width: `${total ? (s.count / total) * 100 : 0}%`,
                      background: `linear-gradient(90deg, ${s.color}, ${s.color}88)`,
                      borderRadius: "3px",
                      transition: "width 1s ease",
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Priority Distribution */}
        <div
          style={{
            background: "rgba(255,255,255,0.03)",
            border: "1px solid rgba(255,255,255,0.07)",
            borderRadius: "20px",
            padding: "28px",
            backdropFilter: "blur(20px)",
          }}
        >
          <h3
            style={{
              margin: "0 0 20px",
              fontSize: "16px",
              color: "rgba(255,255,255,0.7)",
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              fontWeight: "600",
            }}
          >
            Priority Distribution
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {Object.entries(PRIORITY_CONFIG).map(([key, cfg]) => {
              const count = data.priority_breakdown?.[key] || 0;
              return (
                <div
                  key={key}
                  style={{
                    background: `${cfg.color}10`,
                    border: `1px solid ${cfg.color}30`,
                    borderRadius: "14px",
                    padding: "20px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <div
                    style={{
                      fontSize: "12px",
                      color: "rgba(255,255,255,0.4)",
                      textTransform: "uppercase",
                      letterSpacing: "0.08em",
                    }}
                  >
                    {cfg.label} Priority
                  </div>
                  <div
                    style={{
                      fontSize: "36px",
                      fontWeight: "800",
                      color: cfg.color,
                      fontFamily: "'Playfair Display', serif",
                    }}
                  >
                    {count}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Ad between sections */}
        <div style={{ gridColumn: "1/-1" }}>
          <InFeedAd />
        </div>

        {/* Application Funnel */}
        <div
          style={{
            background: "rgba(255,255,255,0.03)",
            border: "1px solid rgba(255,255,255,0.07)",
            borderRadius: "20px",
            padding: "28px",
            backdropFilter: "blur(20px)",
            gridColumn: "1/-1",
          }}
        >
          <h3
            style={{
              margin: "0 0 24px",
              fontSize: "16px",
              color: "rgba(255,255,255,0.7)",
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              fontWeight: "600",
            }}
          >
            Application Funnel
          </h3>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "12px",
              alignItems: "center",
            }}
          >
            {[
              { label: "Saved", key: "saved", color: "#60a5fa" },
              { label: "Applied", key: "applied", color: "#fbbf24" },
              { label: "Interview", key: "interview", color: "#a78bfa" },
              { label: "Offer", key: "offer", color: "#34d399" },
            ].map((f, i) => (
              <div
                key={f.label}
                style={{
                  width: `${100 - i * 12}%`,
                  transition: "width 1s ease",
                }}
              >
                <div
                  style={{
                    background: `${f.color}20`,
                    border: `1px solid ${f.color}44`,
                    borderRadius: "10px",
                    padding: "10px 16px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <span style={{ fontSize: "13px", color: f.color, fontWeight: "600" }}>
                    {f.label}
                  </span>
                  <span
                    style={{
                      fontSize: "20px",
                      fontWeight: "800",
                      color: f.color,
                      fontFamily: "'Playfair Display', serif",
                    }}
                  >
                    {data.status_breakdown?.[f.key] || 0}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
