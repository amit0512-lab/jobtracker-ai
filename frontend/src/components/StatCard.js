export default function StatCard({ value, label, color, icon, delay }) {
  return (
    <div
      style={{
        background: "rgba(255,255,255,0.04)",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: "20px",
        padding: "28px",
        backdropFilter: "blur(20px)",
        position: "relative",
        overflow: "hidden",
        animation: `fadeSlideUp 0.6s ease ${delay}s both`,
        cursor: "default",
        transition: "transform 0.2s ease, border-color 0.2s ease",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-4px)";
        e.currentTarget.style.borderColor = color + "55";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)";
      }}
    >
      <div
        style={{
          position: "absolute",
          top: 0,
          right: 0,
          width: "120px",
          height: "120px",
          background: `radial-gradient(circle at top right, ${color}18, transparent 70%)`,
          borderRadius: "0 20px 0 0",
        }}
      />
      <div style={{ fontSize: "28px", marginBottom: "12px" }}>{icon}</div>
      <div
        style={{
          fontSize: "42px",
          fontWeight: "800",
          color,
          fontFamily: "'Playfair Display', serif",
          lineHeight: 1,
          marginBottom: "8px",
        }}
      >
        {value}
      </div>
      <div
        style={{
          fontSize: "13px",
          color: "rgba(255,255,255,0.45)",
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          fontWeight: "500",
        }}
      >
        {label}
      </div>
    </div>
  );
}
