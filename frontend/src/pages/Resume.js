import { useEffect, useState } from "react";
import { resumeAPI, jobsAPI } from "../services/api";
import { TopBannerAd, InFeedAd } from "../components/AdBanner";

export default function Resume() {
  const [resumes, setResumes] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(null);
  const [selectedResume, setSelectedResume] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [resumesRes, jobsRes] = await Promise.all([
        resumeAPI.getAll(),
        jobsAPI.getAll(),
      ]);
      const resumesData = Array.isArray(resumesRes.data) ? resumesRes.data : resumesRes.data.resumes || [];
      const jobsData = Array.isArray(jobsRes.data) ? jobsRes.data : jobsRes.data.jobs || [];
      setResumes(resumesData);
      setJobs(jobsData);
    } catch (error) {
      console.error("Failed to load data:", error);
      setResumes([]);
      setJobs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    try {
      const response = await resumeAPI.upload(formData);
      setResumes((r) => [response.data, ...r]);
      alert("Resume uploaded successfully!");
      e.target.value = "";
    } catch (error) {
      console.error("Failed to upload resume:", error);
      alert(error.response?.data?.detail || "Failed to upload resume");
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyze = async (resumeId, jobId) => {
    setAnalyzing(resumeId);
    setSelectedResume(resumeId);
    try {
      const response = await resumeAPI.analyze(resumeId, jobId);
      setAnalysisResult(response.data);
      setResumes((r) =>
        r.map((resume) =>
          resume.id === resumeId
            ? { 
                ...resume, 
                match_score: response.data.match_score,
                analysis: response.data 
              }
            : resume
        )
      );
    } catch (error) {
      console.error("Failed to analyze resume:", error);
      alert(error.response?.data?.detail || "Failed to analyze resume");
    } finally {
      setAnalyzing(null);
    }
  };

  const handleDelete = async (id) => {
    try {
      await resumeAPI.delete(id);
      setResumes((r) => r.filter((x) => x.id !== id));
      if (selectedResume === id) {
        setSelectedResume(null);
        setAnalysisResult(null);
      }
    } catch (error) {
      console.error("Failed to delete resume:", error);
      alert("Failed to delete resume");
    }
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
      <h1
        style={{
          fontSize: "32px",
          fontWeight: "800",
          fontFamily: "'Playfair Display', serif",
          letterSpacing: "-0.02em",
          marginBottom: "8px",
        }}
      >
        Resume Manager
      </h1>
      <p style={{ color: "rgba(255,255,255,0.4)", fontSize: "14px", marginBottom: "32px" }}>
        Upload resumes and match against job descriptions
      </p>

      <TopBannerAd />

      <label
        style={{
          display: "block",
          border: "2px dashed rgba(99,102,241,0.3)",
          borderRadius: "20px",
          padding: "60px 40px",
          textAlign: "center",
          background: "rgba(99,102,241,0.04)",
          marginBottom: "24px",
          cursor: "pointer",
          transition: "all 0.3s",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = "rgba(99,102,241,0.6)";
          e.currentTarget.style.background = "rgba(99,102,241,0.08)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = "rgba(99,102,241,0.3)";
          e.currentTarget.style.background = "rgba(99,102,241,0.04)";
        }}
      >
        <input
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={handleFileUpload}
          style={{ display: "none" }}
          disabled={uploading}
        />
        <div style={{ fontSize: "48px", marginBottom: "16px" }}>◉</div>
        <div
          style={{
            fontSize: "18px",
            fontWeight: "700",
            fontFamily: "'Playfair Display', serif",
            marginBottom: "8px",
          }}
        >
          {uploading ? "Uploading..." : "Drop your resume here"}
        </div>
        <div style={{ fontSize: "13px", color: "rgba(255,255,255,0.35)", marginBottom: "20px" }}>
          PDF or DOCX — Max 10MB
        </div>
        <div
          style={{
            display: "inline-block",
            padding: "11px 28px",
            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            border: "none",
            borderRadius: "10px",
            color: "#fff",
            fontSize: "14px",
            fontWeight: "600",
          }}
        >
          Choose File
        </div>
      </label>

      <div style={{ display: "grid", gridTemplateColumns: analysisResult ? "1fr 1fr" : "1fr", gap: "20px" }}>
        {/* Resumes List */}
        <div
          style={{
            background: "rgba(255,255,255,0.03)",
            border: "1px solid rgba(255,255,255,0.07)",
            borderRadius: "20px",
            padding: "24px",
            backdropFilter: "blur(20px)",
          }}
        >
          <h3
            style={{
              fontSize: "16px",
              fontWeight: "700",
              marginBottom: "16px",
              fontFamily: "'Playfair Display', serif",
            }}
          >
            Uploaded Resumes
          </h3>
          {resumes.length === 0 ? (
            <div style={{ textAlign: "center", padding: "40px", color: "rgba(255,255,255,0.3)" }}>
              No resumes uploaded yet
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              {resumes.map((resume) => (
                <div
                  key={resume.id}
                  style={{
                    padding: "16px",
                    background: selectedResume === resume.id ? "rgba(99,102,241,0.1)" : "rgba(255,255,255,0.02)",
                    borderRadius: "12px",
                    border: `1px solid ${selectedResume === resume.id ? "rgba(99,102,241,0.3)" : "rgba(255,255,255,0.05)"}`,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "12px" }}>
                    <div
                      style={{
                        width: "44px",
                        height: "44px",
                        background: "rgba(99,102,241,0.15)",
                        borderRadius: "12px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "20px",
                        flexShrink: 0,
                      }}
                    >
                      ◉
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: "14px", fontWeight: "600", marginBottom: "4px" }}>
                        {resume.filename}
                      </div>
                      <div style={{ fontSize: "12px", color: "rgba(255,255,255,0.4)" }}>
                        Uploaded: {new Date(resume.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    {resume.match_score > 0 && (
                      <div style={{ textAlign: "center", flexShrink: 0 }}>
                        <div
                          style={{
                            fontSize: "26px",
                            fontWeight: "800",
                            color: resume.match_score >= 70 ? "#34d399" : resume.match_score >= 50 ? "#fbbf24" : "#f87171",
                            fontFamily: "'Playfair Display', serif",
                          }}
                        >
                          {Math.round(resume.match_score)}%
                        </div>
                        <div
                          style={{
                            fontSize: "10px",
                            color: "rgba(255,255,255,0.3)",
                            textTransform: "uppercase",
                            letterSpacing: "0.06em",
                          }}
                        >
                          Match
                        </div>
                      </div>
                    )}
                  </div>

                  {jobs.length > 0 && (
                    <div style={{ paddingTop: "12px", borderTop: "1px solid rgba(255,255,255,0.06)" }}>
                      <div style={{ fontSize: "12px", color: "rgba(255,255,255,0.4)", marginBottom: "8px" }}>
                        Analyze against job:
                      </div>
                      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "8px" }}>
                        {jobs.slice(0, 5).map((job) => (
                          <button
                            key={job.id}
                            onClick={() => handleAnalyze(resume.id, job.id)}
                            disabled={analyzing === resume.id}
                            style={{
                              padding: "6px 12px",
                              background: "rgba(99,102,241,0.1)",
                              border: "1px solid rgba(99,102,241,0.2)",
                              borderRadius: "8px",
                              color: "#a5b4fc",
                              cursor: analyzing === resume.id ? "not-allowed" : "pointer",
                              fontSize: "11px",
                              fontWeight: "600",
                              opacity: analyzing === resume.id ? 0.5 : 1,
                            }}
                          >
                            {analyzing === resume.id ? "Analyzing..." : job.title}
                          </button>
                        ))}
                      </div>
                      <button
                        onClick={() => handleDelete(resume.id)}
                        style={{
                          padding: "6px 12px",
                          background: "rgba(248,113,113,0.1)",
                          border: "1px solid rgba(248,113,113,0.2)",
                          borderRadius: "8px",
                          color: "#f87171",
                          cursor: "pointer",
                          fontSize: "11px",
                          fontWeight: "600",
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Ad between list and results */}
        {!analysisResult && resumes.length > 0 && (
          <div style={{ gridColumn: "1/-1" }}>
            <InFeedAd />
          </div>
        )}

        {/* Analysis Results */}
        {analysisResult && (
          <div
            style={{
              background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.07)",
              borderRadius: "20px",
              padding: "24px",
              backdropFilter: "blur(20px)",
              animation: "fadeSlideUp 0.3s ease",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h3
                style={{
                  fontSize: "16px",
                  fontWeight: "700",
                  fontFamily: "'Playfair Display', serif",
                }}
              >
                Analysis Results
              </h3>
              <button
                onClick={() => {
                  setAnalysisResult(null);
                  setSelectedResume(null);
                }}
                style={{
                  background: "rgba(255,255,255,0.06)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "8px",
                  padding: "4px 8px",
                  cursor: "pointer",
                  color: "rgba(255,255,255,0.6)",
                  fontSize: "12px",
                }}
              >
                ✕
              </button>
            </div>

            {/* Match Score */}
            <div
              style={{
                textAlign: "center",
                padding: "24px",
                background: analysisResult.match_score >= 65 ? "rgba(16,185,129,0.1)" : analysisResult.match_score >= 35 ? "rgba(245,158,11,0.1)" : "rgba(239,68,68,0.1)",
                border: `1px solid ${analysisResult.match_score >= 65 ? "rgba(16,185,129,0.2)" : analysisResult.match_score >= 35 ? "rgba(245,158,11,0.2)" : "rgba(239,68,68,0.2)"}`,
                borderRadius: "16px",
                marginBottom: "20px",
              }}
            >
              <div
                style={{
                  fontSize: "48px",
                  fontWeight: "800",
                  color: analysisResult.match_score >= 65 ? "#10b981" : analysisResult.match_score >= 35 ? "#f59e0b" : "#ef4444",
                  fontFamily: "'Playfair Display', serif",
                  marginBottom: "8px",
                }}
              >
                {Math.round(analysisResult.match_score)}%
              </div>
              <div style={{ fontSize: "13px", color: "rgba(255,255,255,0.5)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                Match Score
              </div>
              
              {/* Recommendation */}
              <div style={{ 
                marginTop: "16px", 
                padding: "12px 16px",
                background: analysisResult.match_score >= 65 ? "rgba(16,185,129,0.15)" : analysisResult.match_score >= 35 ? "rgba(245,158,11,0.15)" : "rgba(239,68,68,0.15)",
                border: `1px solid ${analysisResult.match_score >= 65 ? "rgba(16,185,129,0.3)" : analysisResult.match_score >= 35 ? "rgba(245,158,11,0.3)" : "rgba(239,68,68,0.3)"}`,
                borderRadius: "10px",
              }}>
                <div style={{ 
                  fontSize: "13px", 
                  fontWeight: "600",
                  color: analysisResult.match_score >= 65 ? "#10b981" : analysisResult.match_score >= 35 ? "#f59e0b" : "#ef4444",
                  marginBottom: "4px"
                }}>
                  {analysisResult.match_score >= 65 ? "✓ Excellent Match!" : analysisResult.match_score >= 35 ? "⚠ Moderate Match" : "✗ Low Match"}
                </div>
                <div style={{ 
                  fontSize: "11px", 
                  color: analysisResult.match_score >= 65 ? "#10b981" : analysisResult.match_score >= 35 ? "#f59e0b" : "#ef4444",
                  lineHeight: "1.4"
                }}>
                  {analysisResult.match_score >= 65 
                    ? "Your resume is a great fit for this job. Go ahead and apply!" 
                    : analysisResult.match_score >= 35 
                    ? "Consider updating your resume to better match the job requirements" 
                    : "Your resume needs significant updates. Review suggestions below or choose a different job."}
                </div>
              </div>
              
              {/* Experience Info */}
              {analysisResult.experience_match && analysisResult.experience_match.required_years > 0 && (
                <div style={{ marginTop: "16px", paddingTop: "16px", borderTop: "1px solid rgba(255,255,255,0.1)" }}>
                  <div style={{ fontSize: "12px", color: "rgba(255,255,255,0.4)", marginBottom: "8px" }}>
                    Experience
                  </div>
                  <div style={{ display: "flex", justifyContent: "center", gap: "20px", fontSize: "13px" }}>
                    <div>
                      <span style={{ color: "rgba(255,255,255,0.5)" }}>Your: </span>
                      <span style={{ color: "#a5b4fc", fontWeight: "600" }}>
                        {analysisResult.experience_match.resume_years} years
                      </span>
                    </div>
                    <div>
                      <span style={{ color: "rgba(255,255,255,0.5)" }}>Required: </span>
                      <span style={{ color: "#fbbf24", fontWeight: "600" }}>
                        {analysisResult.experience_match.required_years}+ years
                      </span>
                    </div>
                  </div>
                  {!analysisResult.experience_match.meets_requirement && (
                    <div style={{ marginTop: "8px", fontSize: "11px", color: "#f87171" }}>
                      ⚠️ {analysisResult.experience_match.gap} years gap
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Suggestions */}
            {analysisResult.suggestions && analysisResult.suggestions.length > 0 && (
              <div style={{ marginBottom: "20px" }}>
                <h4 style={{ fontSize: "14px", fontWeight: "600", marginBottom: "12px", color: "rgba(255,255,255,0.7)" }}>
                  💡 Suggestions
                </h4>
                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  {analysisResult.suggestions.map((suggestion, i) => (
                    <div
                      key={i}
                      style={{
                        padding: "10px 12px",
                        background: "rgba(255,255,255,0.02)",
                        border: "1px solid rgba(255,255,255,0.05)",
                        borderRadius: "10px",
                        fontSize: "12px",
                        color: "rgba(255,255,255,0.7)",
                        lineHeight: "1.5",
                      }}
                    >
                      {suggestion}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Matched Keywords */}
            {analysisResult.matched_keywords && analysisResult.matched_keywords.length > 0 && (
              <div style={{ marginBottom: "20px" }}>
                <h4 style={{ fontSize: "14px", fontWeight: "600", marginBottom: "12px", color: "rgba(255,255,255,0.7)" }}>
                  ✅ Matched Keywords
                </h4>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                  {analysisResult.matched_keywords.slice(0, 15).map((kw, i) => (
                    <span
                      key={i}
                      style={{
                        padding: "4px 10px",
                        background: "rgba(52,211,153,0.1)",
                        border: "1px solid rgba(52,211,153,0.2)",
                        borderRadius: "6px",
                        fontSize: "11px",
                        color: "#34d399",
                        fontWeight: "600",
                      }}
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Missing Keywords */}
            {analysisResult.missing_keywords && analysisResult.missing_keywords.length > 0 && (
              <div>
                <h4 style={{ fontSize: "14px", fontWeight: "600", marginBottom: "12px", color: "rgba(255,255,255,0.7)" }}>
                  ⚠️ Missing Keywords
                </h4>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                  {analysisResult.missing_keywords.slice(0, 12).map((kw, i) => (
                    <span
                      key={i}
                      style={{
                        padding: "4px 10px",
                        background: "rgba(248,113,113,0.1)",
                        border: "1px solid rgba(248,113,113,0.2)",
                        borderRadius: "6px",
                        fontSize: "11px",
                        color: "#f87171",
                        fontWeight: "600",
                      }}
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
