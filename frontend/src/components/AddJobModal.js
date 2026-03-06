import { useState } from "react";
import { STATUS_CONFIG } from "../constants/config";

export default function AddJobModal({ onClose, onAdd, onEdit, editJob }) {
  const isEditMode = !!editJob;
  
  const [form, setForm] = useState(
    editJob || {
      title: "",
      company: "",
      location: "",
      salary_min: "",
      salary_max: "",
      priority: "medium",
      status: "saved",
      notes: "",
      description: "",
    }
  );

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const inputStyle = {
    width: "100%",
    background: "rgba(255,255,255,0.05)",
    border: "1px solid rgba(255,255,255,0.1)",
    borderRadius: "12px",
    padding: "12px 16px",
    color: "#f1f5f9",
    fontSize: "14px",
    outline: "none",
    boxSizing: "border-box",
    fontFamily: "inherit",
  };

  const labelStyle = {
    fontSize: "12px",
    color: "rgba(255,255,255,0.45)",
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    marginBottom: "8px",
    display: "block",
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.7)",
        backdropFilter: "blur(8px)",
        zIndex: 1000,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px",
      }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        style={{
          background: "rgba(15,20,35,0.95)",
          border: "1px solid rgba(255,255,255,0.1)",
          borderRadius: "24px",
          padding: "36px",
          width: "100%",
          maxWidth: "540px",
          backdropFilter: "blur(40px)",
          animation: "fadeSlideUp 0.3s ease",
          maxHeight: "90vh",
          overflowY: "auto",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "28px",
          }}
        >
          <h2
            style={{
              margin: 0,
              fontFamily: "'Playfair Display', serif",
              fontSize: "24px",
              color: "#f1f5f9",
            }}
          >
            {isEditMode ? "Edit Job" : "Add New Job"}
          </h2>
          <button
            onClick={onClose}
            style={{
              background: "rgba(255,255,255,0.06)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "10px",
              width: "36px",
              height: "36px",
              cursor: "pointer",
              color: "rgba(255,255,255,0.6)",
              fontSize: "18px",
            }}
          >
            ×
          </button>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
          <div style={{ gridColumn: "1/-1" }}>
            <label style={labelStyle}>Job Title *</label>
            <input
              style={inputStyle}
              placeholder="Senior Backend Engineer"
              value={form.title}
              onChange={(e) => set("title", e.target.value)}
            />
          </div>
          <div>
            <label style={labelStyle}>Company *</label>
            <input
              style={inputStyle}
              placeholder="Google"
              value={form.company}
              onChange={(e) => set("company", e.target.value)}
            />
          </div>
          <div>
            <label style={labelStyle}>Location</label>
            <input
              style={inputStyle}
              placeholder="Bangalore / Remote"
              value={form.location}
              onChange={(e) => set("location", e.target.value)}
            />
          </div>
          <div>
            <label style={labelStyle}>Min Salary (LPA)</label>
            <input
              style={inputStyle}
              placeholder="20"
              value={form.salary_min}
              onChange={(e) => set("salary_min", e.target.value)}
            />
          </div>
          <div>
            <label style={labelStyle}>Max Salary (LPA)</label>
            <input
              style={inputStyle}
              placeholder="40"
              value={form.salary_max}
              onChange={(e) => set("salary_max", e.target.value)}
            />
          </div>
          <div>
            <label style={labelStyle}>Priority</label>
            <select
              style={inputStyle}
              value={form.priority}
              onChange={(e) => set("priority", e.target.value)}
            >
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <div>
            <label style={labelStyle}>Status</label>
            <select
              style={inputStyle}
              value={form.status}
              onChange={(e) => set("status", e.target.value)}
            >
              {Object.entries(STATUS_CONFIG).map(([k, v]) => (
                <option key={k} value={k}>
                  {v.label}
                </option>
              ))}
            </select>
          </div>
          <div style={{ gridColumn: "1/-1" }}>
            <label style={labelStyle}>Job Description</label>
            <textarea
              style={{ ...inputStyle, height: "100px", resize: "vertical" }}
              placeholder="Paste job description here..."
              value={form.description}
              onChange={(e) => set("description", e.target.value)}
            />
          </div>
          <div style={{ gridColumn: "1/-1" }}>
            <label style={labelStyle}>Notes</label>
            <textarea
              style={{ ...inputStyle, height: "80px", resize: "vertical" }}
              placeholder="Referral, recruiter name, important details..."
              value={form.notes}
              onChange={(e) => set("notes", e.target.value)}
            />
          </div>
        </div>

        <div style={{ display: "flex", gap: "12px", marginTop: "24px" }}>
          <button
            onClick={onClose}
            style={{
              flex: 1,
              padding: "13px",
              background: "rgba(255,255,255,0.04)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "12px",
              color: "rgba(255,255,255,0.6)",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: "600",
            }}
          >
            Cancel
          </button>
          <button
            onClick={() => {
              if (form.title && form.company) {
                if (isEditMode) {
                  onEdit(editJob.id, form);
                } else {
                  onAdd(form);
                }
                onClose();
              }
            }}
            style={{
              flex: 2,
              padding: "13px",
              background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              border: "none",
              borderRadius: "12px",
              color: "#fff",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: "700",
              letterSpacing: "0.04em",
            }}
          >
            {isEditMode ? "Save Changes ✓" : "Add Job ✦"}
          </button>
        </div>
      </div>
    </div>
  );
}
