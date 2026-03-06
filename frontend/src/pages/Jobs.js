import { useEffect, useState } from "react";
import { jobsAPI } from "../services/api";
import JobCard from "../components/JobCard";
import AddJobModal from "../components/AddJobModal";
import { STATUS_CONFIG } from "../constants/config";
import { TopBannerAd, InFeedAd } from "../components/AdBanner";

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingJob, setEditingJob] = useState(null);

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

  const filteredJobs = jobs.filter((j) => {
    const matchStatus = statusFilter === "all" || j.status === statusFilter;
    const matchSearch =
      !searchQuery ||
      j.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      j.company.toLowerCase().includes(searchQuery.toLowerCase());
    return matchStatus && matchSearch;
  });

  const handleDelete = async (id) => {
    try {
      await jobsAPI.delete(id);
      setJobs((j) => j.filter((x) => x.id !== id));
    } catch (error) {
      console.error("Failed to delete job:", error);
      alert("Failed to delete job");
    }
  };

  const handleStatusChange = async (id, status) => {
    try {
      await jobsAPI.updateStatus(id, status);
      setJobs((j) => j.map((x) => (x.id === id ? { ...x, status } : x)));
    } catch (error) {
      console.error("Failed to update status:", error);
      alert("Failed to update status");
    }
  };

  const handleAdd = async (form) => {
    try {
      const response = await jobsAPI.create(form);
      setJobs((j) => [response.data, ...j]);
    } catch (error) {
      console.error("Failed to add job:", error);
      alert("Failed to add job");
    }
  };

  const handleEdit = async (id, form) => {
    try {
      const response = await jobsAPI.update(id, form);
      setJobs((j) => j.map((x) => (x.id === id ? response.data : x)));
    } catch (error) {
      console.error("Failed to update job:", error);
      alert("Failed to update job");
    }
  };

  const openEditModal = (job) => {
    setEditingJob(job);
    setShowAddModal(true);
  };

  const closeModal = () => {
    setShowAddModal(false);
    setEditingJob(null);
  };

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "60px", color: "rgba(255,255,255,0.4)" }}>
        Loading...
      </div>
    );
  }

  return (
    <>
      <div style={{ animation: "fadeSlideUp 0.5s ease" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-end",
            marginBottom: "28px",
          }}
        >
          <div>
            <h1
              style={{
                fontSize: "32px",
                fontWeight: "800",
                fontFamily: "'Playfair Display', serif",
                letterSpacing: "-0.02em",
                marginBottom: "6px",
              }}
            >
              Job Applications
            </h1>
            <p style={{ color: "rgba(255,255,255,0.4)", fontSize: "14px" }}>
              {filteredJobs.length} of {jobs.length} jobs
            </p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              padding: "12px 22px",
              background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              border: "none",
              borderRadius: "12px",
              color: "#fff",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: "700",
              letterSpacing: "0.04em",
              transition: "opacity 0.2s",
              boxShadow: "0 4px 20px rgba(99,102,241,0.35)",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.opacity = "0.85")}
            onMouseLeave={(e) => (e.currentTarget.style.opacity = "1")}
          >
            ✦ Add Job
          </button>
        </div>

        <div style={{ display: "flex", gap: "12px", marginBottom: "24px", flexWrap: "wrap" }}>
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search jobs or companies..."
            style={{
              flex: 1,
              minWidth: "200px",
              background: "rgba(255,255,255,0.04)",
              border: "1px solid rgba(255,255,255,0.08)",
              borderRadius: "12px",
              padding: "11px 16px",
              color: "#f1f5f9",
              fontSize: "14px",
              outline: "none",
              fontFamily: "inherit",
            }}
          />
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
            {["all", ...Object.keys(STATUS_CONFIG)].map((s) => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                style={{
                  padding: "10px 16px",
                  borderRadius: "10px",
                  border: `1px solid ${
                    statusFilter === s
                      ? (STATUS_CONFIG[s]?.color || "#6366f1") + "55"
                      : "rgba(255,255,255,0.08)"
                  }`,
                  background:
                    statusFilter === s
                      ? STATUS_CONFIG[s]?.bg || "rgba(99,102,241,0.15)"
                      : "transparent",
                  color:
                    statusFilter === s
                      ? STATUS_CONFIG[s]?.color || "#a5b4fc"
                      : "rgba(255,255,255,0.4)",
                  cursor: "pointer",
                  fontSize: "12px",
                  fontWeight: "600",
                  transition: "all 0.2s",
                  textTransform: "capitalize",
                }}
              >
                {s === "all" ? "All" : STATUS_CONFIG[s].label}
              </button>
            ))}
          </div>
        </div>

        <TopBannerAd />

        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {filteredJobs.length === 0 ? (
            <div style={{ textAlign: "center", padding: "60px", color: "rgba(255,255,255,0.3)" }}>
              No jobs found. Try adjusting filters.
            </div>
          ) : (
            <>
              {filteredJobs.slice(0, 3).map((job) => (
                <JobCard
                  key={job.id}
                  job={job}
                  onDelete={handleDelete}
                  onStatusChange={handleStatusChange}
                  onEdit={openEditModal}
                />
              ))}
              {filteredJobs.length > 3 && <InFeedAd />}
              {filteredJobs.slice(3).map((job) => (
                <JobCard
                  key={job.id}
                  job={job}
                  onDelete={handleDelete}
                  onStatusChange={handleStatusChange}
                  onEdit={openEditModal}
                />
              ))}
            </>
          )}
        </div>
      </div>

      {showAddModal && (
        <AddJobModal
          onClose={closeModal}
          onAdd={handleAdd}
          onEdit={handleEdit}
          editJob={editingJob}
        />
      )}
    </>
  );
}
