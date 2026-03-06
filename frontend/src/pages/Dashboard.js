import { useEffect, useState } from "react";
import { jobsAPI } from "../services/api";
import StatCard from "../components/StatCard";
import { STATUS_CONFIG } from "../constants/config";

export default function Dashboard() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  // Get dynamic greeting based on time of day
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning ✦";
    if (hour < 17) return "Good afternoon ☀";
    return "Good evening ✧";
  };

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      const response = await jobsAPI.getAll();
      // Handle both array and object responses
      const jobsData = Array.isArray(response.data) ? response.data : response.data.jobs || [];
      setJobs(jobsData);
    } catch (error) {
      console.error("Failed to load jobs:", error);
      setJobs([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  const stats = {
    total: jobs.length,
    applied: jobs.filter((j) => j.status === "applied").length,
    interview: jobs.filter((j) => j.status === "interview").length,
    offer: jobs.filter((j) => j.status === "offer").length,
  };

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "60px", color: "rgba(255,255,255,0.4)" }}>
        Loading...
      </div>
    );
  }

  return (
    <div style={{ animation: "fadeSlideUp 0.5s ease" }}>
      <div style={{ marginBottom: "36px" }}>
        <h1
          style={{
            fontSize: "34px",
            fontWeight: "800",
            fontFamily: "'Playfair Display', serif",
            letterSpacing: "-0.02em",
            marginBottom: "8px",
          }}
        >
          {getGreeting()}
        </h1>
        <p style={{ color: "rgba(255,255,255,0.4)", fontSize: "15px" }}>
          Here's your job search overview
        </p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "16px",
          marginBottom: "32px",
        }}
      >
        <StatCard value={stats.total} label="Total Jobs" color="#60a5fa" icon="◈" delay={0} />
        <StatCard value={stats.applied} label="Applied" color="#fbbf24" icon="◎" delay={0.1} />
        <StatCard
          value={stats.interview}
          label="Interviews"
          color="#a78bfa"
          icon="◉"
          delay={0.2}
        />
        <StatCard value={stats.offer} label="Offers" color="#34d399" icon="⬡" delay={0.3} />
      </div>

      <div
        style={{
          background: "rgba(255,255,255,0.02)",
          border: "1px solid rgba(255,255,255,0.06)",
          borderRadius: "20px",
          padding: "24px",
          backdropFilter: "blur(20px)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "20px",
          }}
        >
          <h2
            style={{
              fontSize: "17px",
              fontWeight: "700",
              fontFamily: "'Playfair Display', serif",
            }}
          >
            Recent Applications
          </h2>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          {jobs.slice(0, 5).map((job) => {
            const status = STATUS_CONFIG[job.status];
            return (
              <div
                key={job.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "14px 16px",
                  background: "rgba(255,255,255,0.02)",
                  borderRadius: "12px",
                  border: "1px solid rgba(255,255,255,0.05)",
                }}
              >
                <div>
                  <div
                    style={{
                      fontSize: "14px",
                      fontWeight: "600",
                      color: "#f1f5f9",
                      marginBottom: "3px",
                    }}
                  >
                    {job.title}
                  </div>
                  <div style={{ fontSize: "12px", color: "rgba(255,255,255,0.4)" }}>
                    {job.company} • {job.location}
                  </div>
                </div>
                <span
                  style={{
                    fontSize: "11px",
                    fontWeight: "600",
                    color: status.color,
                    background: status.bg,
                    border: `1px solid ${status.color}33`,
                    borderRadius: "16px",
                    padding: "4px 12px",
                  }}
                >
                  {status.label}
                </span>
              </div>
            );
          })}
          {jobs.length === 0 && (
            <div style={{ textAlign: "center", padding: "40px", color: "rgba(255,255,255,0.3)" }}>
              No jobs yet. Start adding jobs to track your applications!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
