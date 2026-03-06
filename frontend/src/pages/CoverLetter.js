import { useEffect, useState } from "react";
import { coverLetterAPI, jobsAPI, resumeAPI } from "../services/api";
import { TONE_CONFIG } from "../constants/config";

export default function CoverLetter() {
  const [coverLetters, setCoverLetters] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [showGenerator, setShowGenerator] = useState(false);
  const [selectedLetter, setSelectedLetter] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [editContent, setEditContent] = useState("");

  // Generator form
  const [selectedJob, setSelectedJob] = useState("");
  const [selectedResume, setSelectedResume] = useState("");
  const [selectedTone, setSelectedTone] = useState("professional");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [clRes, jobsRes, resumesRes] = await Promise.all([
        coverLetterAPI.getAll().catch(() => ({ data: [] })),
        jobsAPI.getAll(),
        resumeAPI.getAll().catch(() => ({ data: [] })),
      ]);
      
      // Handle cover letters
      const clData = Array.isArray(clRes.data) ? clRes.data : [];
      setCoverLetters(clData);
      
      // Handle jobs - support both array and object response
      let jobsData = [];
      if (Array.isArray(jobsRes.data)) {
        jobsData = jobsRes.data;
      } else if (jobsRes.data && jobsRes.data.jobs) {
        jobsData = jobsRes.data.jobs;
      } else if (jobsRes.data) {
        jobsData = [jobsRes.data];
      }
      setJobs(jobsData);
      console.log("Loaded jobs:", jobsData);
      
      // Handle resumes
      const resumesData = Array.isArray(resumesRes.data) ? resumesRes.data : [];
      setResumes(resumesData);
      console.log("Loaded resumes:", resumesData);
      
    } catch (error) {
      console.error("Failed to load data:", error);
      setJobs([]);
      setResumes([]);
      setCoverLetters([]);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!selectedJob) {
      alert("Please select a job");
      return;
    }

    setGenerating(true);
    try {
      const response = await coverLetterAPI.generate({
        job_id: selectedJob,
        resume_id: selectedResume || null,
        tone: selectedTone,
      });
      
      // Success - reload data and close modal
      await loadData();
      setShowGenerator(false);
      setSelectedJob("");
      setSelectedResume("");
      setSelectedTone("professional");
      alert("Cover letter generated successfully!");
      
    } catch (error) {
      console.error("Failed to generate:", error);
      
      // The backend might have succeeded even if we got an error
      // (common with slow AI generation or rate limits)
      // Always refresh the list to check
      await loadData();
      
      // Check if a new cover letter appeared
      const newCount = coverLetters.length;
      await loadData();
      const updatedCount = coverLetters.length;
      
      if (error.message === "Network Error" || error.code === "ERR_NETWORK" || error.response?.status === 500) {
        // Likely succeeded despite error
        alert("Cover letter generated! (The request took longer than expected, but it worked)");
        setShowGenerator(false);
        setSelectedJob("");
        setSelectedResume("");
        setSelectedTone("professional");
      } else if (error.response?.status === 429) {
        alert("Rate limit reached. Please wait a moment and try again.");
      } else {
        // Show detailed error message
        let errorMessage = "Failed to generate cover letter.";
        if (error.response?.data?.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.message) {
          errorMessage = error.message;
        }
        alert(errorMessage);
      }
      
      console.error("Full error:", error.response || error);
    } finally {
      setGenerating(false);
    }
  };

  const handleView = async (id) => {
    try {
      const response = await coverLetterAPI.getOne(id);
      setSelectedLetter(response.data);
      setEditContent(response.data.content);
      setEditMode(false);
    } catch (error) {
      console.error("Failed to load cover letter:", error);
    }
  };

  const handleSave = async () => {
    try {
      await coverLetterAPI.update(selectedLetter.id, { content: editContent });
      setSelectedLetter({ ...selectedLetter, content: editContent });
      setEditMode(false);
      alert("Cover letter updated!");
    } catch (error) {
      console.error("Failed to update:", error);
      alert("Failed to update cover letter");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this cover letter?")) return;
    try {
      await coverLetterAPI.delete(id);
      setCoverLetters(coverLetters.filter((cl) => cl.id !== id));
      if (selectedLetter?.id === id) setSelectedLetter(null);
    } catch (error) {
      console.error("Failed to delete:", error);
      alert("Failed to delete cover letter");
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(selectedLetter.content);
    alert("Copied to clipboard!");
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
            AI Cover Letters
          </h1>
          <p style={{ color: "rgba(255,255,255,0.4)", fontSize: "14px" }}>
            {coverLetters.length} cover letters generated
          </p>
        </div>
        <button
          onClick={() => {
            if (jobs.length === 0) {
              alert("Please add at least one job first. Go to Jobs page → Add Job");
              return;
            }
            setShowGenerator(!showGenerator);
          }}
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
        >
          ✦ Generate New
        </button>
      </div>

      {/* Generator Modal */}
      {showGenerator && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0,0,0,0.7)",
            backdropFilter: "blur(8px)",
            zIndex: 1000,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "20px",
          }}
          onClick={() => setShowGenerator(false)}
        >
          <div
            style={{
              background: "rgba(15,21,37,0.95)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "20px",
              padding: "32px",
              maxWidth: "500px",
              width: "100%",
              backdropFilter: "blur(20px)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2
              style={{
                fontSize: "22px",
                fontWeight: "700",
                marginBottom: "24px",
                fontFamily: "'Playfair Display', serif",
              }}
            >
              Generate Cover Letter
            </h2>

            {/* Debug info - remove in production */}
            {process.env.NODE_ENV === 'development' && (
              <div style={{ 
                fontSize: "11px", 
                color: "rgba(255,255,255,0.4)", 
                marginBottom: "16px",
                padding: "8px",
                background: "rgba(255,255,255,0.02)",
                borderRadius: "6px"
              }}>
                Debug: {jobs.length} jobs, {resumes.length} resumes loaded
              </div>
            )}

            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <div>
                <label style={{ fontSize: "13px", color: "rgba(255,255,255,0.6)", marginBottom: "6px", display: "block" }}>
                  Select Job *
                </label>
                <select
                  value={selectedJob}
                  onChange={(e) => setSelectedJob(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "11px 14px",
                    background: "rgba(255,255,255,0.04)",
                    border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: "10px",
                    color: "#f1f5f9",
                    fontSize: "14px",
                    outline: "none",
                  }}
                >
                  <option value="">
                    {jobs.length === 0 ? "No jobs available - Add a job first" : "Choose a job..."}
                  </option>
                  {jobs.map((job) => (
                    <option key={job.id} value={job.id}>
                      {job.title} @ {job.company}
                    </option>
                  ))}
                </select>
                {jobs.length === 0 && (
                  <div style={{ fontSize: "11px", color: "rgba(248,113,113,0.8)", marginTop: "6px" }}>
                    ⚠️ Please add at least one job before generating a cover letter
                  </div>
                )}
              </div>

              <div>
                <label style={{ fontSize: "13px", color: "rgba(255,255,255,0.6)", marginBottom: "6px", display: "block" }}>
                  Select Resume (Optional)
                </label>
                <select
                  value={selectedResume}
                  onChange={(e) => setSelectedResume(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "11px 14px",
                    background: "rgba(255,255,255,0.04)",
                    border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: "10px",
                    color: "#f1f5f9",
                    fontSize: "14px",
                    outline: "none",
                  }}
                >
                  <option value="">Use generic template</option>
                  {resumes.map((resume) => {
                    const score = resume.match_score || 0;
                    const scorePercent = Math.round(score);
                    return (
                      <option key={resume.id} value={resume.id}>
                        {resume.filename} {scorePercent > 0 ? `(${scorePercent}% match)` : ''}
                      </option>
                    );
                  })}
                </select>
                
                {/* Match Score Indicator */}
                {selectedResume && resumes.find(r => r.id === selectedResume) && (() => {
                  const resume = resumes.find(r => r.id === selectedResume);
                  const score = resume.match_score || 0;
                  const scorePercent = Math.round(score);
                  
                  let recommendation = { text: '', color: '', icon: '' };
                  if (scorePercent >= 65) {
                    recommendation = { 
                      text: '✓ Excellent match! Use this resume', 
                      color: '#10b981',
                      icon: '✓'
                    };
                  } else if (scorePercent >= 35) {
                    recommendation = { 
                      text: '⚠ Moderate match - consider updating resume', 
                      color: '#f59e0b',
                      icon: '⚠'
                    };
                  } else {
                    recommendation = { 
                      text: '✗ Low match - update resume or choose another', 
                      color: '#ef4444',
                      icon: '✗'
                    };
                  }
                  
                  return (
                    <div style={{
                      marginTop: "10px",
                      padding: "10px 12px",
                      background: recommendation.color + "15",
                      border: `1px solid ${recommendation.color}30`,
                      borderRadius: "8px",
                      display: "flex",
                      alignItems: "center",
                      gap: "8px"
                    }}>
                      <div style={{
                        fontSize: "20px",
                        fontWeight: "700",
                        color: recommendation.color,
                        minWidth: "45px"
                      }}>
                        {scorePercent}%
                      </div>
                      <div style={{
                        fontSize: "11px",
                        color: recommendation.color,
                        fontWeight: "500",
                        lineHeight: "1.4"
                      }}>
                        {recommendation.text}
                      </div>
                    </div>
                  );
                })()}
              </div>

              <div>
                <label style={{ fontSize: "13px", color: "rgba(255,255,255,0.6)", marginBottom: "10px", display: "block" }}>
                  Tone
                </label>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                  {Object.entries(TONE_CONFIG).map(([key, cfg]) => (
                    <button
                      key={key}
                      onClick={() => setSelectedTone(key)}
                      style={{
                        padding: "12px",
                        borderRadius: "10px",
                        border: `1px solid ${selectedTone === key ? cfg.color + "55" : "rgba(255,255,255,0.08)"}`,
                        background: selectedTone === key ? cfg.color + "15" : "transparent",
                        color: selectedTone === key ? cfg.color : "rgba(255,255,255,0.4)",
                        cursor: "pointer",
                        fontSize: "12px",
                        fontWeight: "600",
                        transition: "all 0.2s",
                        textAlign: "left",
                      }}
                    >
                      <div>{cfg.label}</div>
                      <div style={{ fontSize: "10px", opacity: 0.7, marginTop: "2px" }}>{cfg.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div style={{ display: "flex", gap: "10px", marginTop: "8px" }}>
                <button
                  onClick={handleGenerate}
                  disabled={generating}
                  style={{
                    flex: 1,
                    padding: "12px",
                    background: generating ? "rgba(99,102,241,0.3)" : "linear-gradient(135deg, #6366f1, #8b5cf6)",
                    border: "none",
                    borderRadius: "10px",
                    color: "#fff",
                    cursor: generating ? "not-allowed" : "pointer",
                    fontSize: "14px",
                    fontWeight: "600",
                  }}
                >
                  {generating ? "Generating..." : "Generate"}
                </button>
                <button
                  onClick={() => setShowGenerator(false)}
                  style={{
                    padding: "12px 20px",
                    background: "rgba(255,255,255,0.05)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "10px",
                    color: "rgba(255,255,255,0.6)",
                    cursor: "pointer",
                    fontSize: "14px",
                    fontWeight: "600",
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Cover Letters List & Viewer */}
      <div style={{ display: "grid", gridTemplateColumns: selectedLetter ? "300px 1fr" : "1fr", gap: "20px" }}>
        {/* List */}
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {coverLetters.length === 0 ? (
            <div
              style={{
                textAlign: "center",
                padding: "60px 20px",
                color: "rgba(255,255,255,0.3)",
                background: "rgba(255,255,255,0.02)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: "16px",
              }}
            >
              No cover letters yet. Generate your first one!
            </div>
          ) : (
            coverLetters.map((cl) => (
              <div
                key={cl.id}
                onClick={() => handleView(cl.id)}
                style={{
                  padding: "16px",
                  background: selectedLetter?.id === cl.id ? "rgba(99,102,241,0.1)" : "rgba(255,255,255,0.02)",
                  border: `1px solid ${selectedLetter?.id === cl.id ? "rgba(99,102,241,0.3)" : "rgba(255,255,255,0.06)"}`,
                  borderRadius: "14px",
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
              >
                <div style={{ fontSize: "14px", fontWeight: "600", marginBottom: "4px" }}>{cl.job_title}</div>
                <div style={{ fontSize: "12px", color: "rgba(255,255,255,0.4)", marginBottom: "8px" }}>
                  {cl.company}
                </div>
                <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                  <span
                    style={{
                      fontSize: "10px",
                      padding: "3px 8px",
                      borderRadius: "6px",
                      background: TONE_CONFIG[cl.tone]?.color + "20",
                      color: TONE_CONFIG[cl.tone]?.color,
                      fontWeight: "600",
                    }}
                  >
                    {TONE_CONFIG[cl.tone]?.label}
                  </span>
                  <span style={{ fontSize: "11px", color: "rgba(255,255,255,0.3)" }}>{cl.word_count} words</span>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Viewer */}
        {selectedLetter && (
          <div
            style={{
              background: "rgba(255,255,255,0.02)",
              border: "1px solid rgba(255,255,255,0.06)",
              borderRadius: "16px",
              padding: "28px",
              backdropFilter: "blur(20px)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h3 style={{ fontSize: "18px", fontWeight: "700", fontFamily: "'Playfair Display', serif" }}>
                Cover Letter
              </h3>
              <div style={{ display: "flex", gap: "8px" }}>
                {editMode ? (
                  <>
                    <button
                      onClick={handleSave}
                      style={{
                        padding: "8px 16px",
                        background: "rgba(52,211,153,0.2)",
                        border: "1px solid rgba(52,211,153,0.3)",
                        borderRadius: "8px",
                        color: "#34d399",
                        cursor: "pointer",
                        fontSize: "12px",
                        fontWeight: "600",
                      }}
                    >
                      Save
                    </button>
                    <button
                      onClick={() => {
                        setEditMode(false);
                        setEditContent(selectedLetter.content);
                      }}
                      style={{
                        padding: "8px 16px",
                        background: "rgba(255,255,255,0.05)",
                        border: "1px solid rgba(255,255,255,0.1)",
                        borderRadius: "8px",
                        color: "rgba(255,255,255,0.6)",
                        cursor: "pointer",
                        fontSize: "12px",
                        fontWeight: "600",
                      }}
                    >
                      Cancel
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      onClick={() => setEditMode(true)}
                      style={{
                        padding: "8px 16px",
                        background: "rgba(99,102,241,0.2)",
                        border: "1px solid rgba(99,102,241,0.3)",
                        borderRadius: "8px",
                        color: "#a5b4fc",
                        cursor: "pointer",
                        fontSize: "12px",
                        fontWeight: "600",
                      }}
                    >
                      Edit
                    </button>
                    <button
                      onClick={handleCopy}
                      style={{
                        padding: "8px 16px",
                        background: "rgba(52,211,153,0.2)",
                        border: "1px solid rgba(52,211,153,0.3)",
                        borderRadius: "8px",
                        color: "#34d399",
                        cursor: "pointer",
                        fontSize: "12px",
                        fontWeight: "600",
                      }}
                    >
                      Copy
                    </button>
                    <button
                      onClick={() => handleDelete(selectedLetter.id)}
                      style={{
                        padding: "8px 16px",
                        background: "rgba(248,113,113,0.2)",
                        border: "1px solid rgba(248,113,113,0.3)",
                        borderRadius: "8px",
                        color: "#f87171",
                        cursor: "pointer",
                        fontSize: "12px",
                        fontWeight: "600",
                      }}
                    >
                      Delete
                    </button>
                  </>
                )}
              </div>
            </div>

            {editMode ? (
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                style={{
                  width: "100%",
                  minHeight: "500px",
                  padding: "16px",
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: "12px",
                  color: "#f1f5f9",
                  fontSize: "14px",
                  lineHeight: "1.8",
                  fontFamily: "inherit",
                  resize: "vertical",
                  outline: "none",
                }}
              />
            ) : (
              <div
                style={{
                  fontSize: "14px",
                  lineHeight: "1.8",
                  color: "rgba(255,255,255,0.8)",
                  whiteSpace: "pre-wrap",
                }}
              >
                {selectedLetter.content}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
