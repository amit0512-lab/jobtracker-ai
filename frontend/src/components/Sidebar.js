import { NAV_ITEMS } from '../constants/config';
import { useAuth } from '../context/AuthContext';

export default function Sidebar({ activeNav, setActiveNav, isOpen, onToggle, isMobile }) {
  const { user, logout } = useAuth();

  const handleNavClick = (navId) => {
    setActiveNav(navId);
    if (isMobile && onToggle) {
      onToggle(); // Close sidebar on mobile after selection
    }
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        width: isMobile ? "80%" : "240px",
        maxWidth: isMobile ? "280px" : "240px",
        flexShrink: 0,
        background: "rgba(255,255,255,0.02)",
        borderRight: "1px solid rgba(255,255,255,0.06)",
        backdropFilter: "blur(20px)",
        display: "flex",
        flexDirection: "column",
        padding: isMobile ? "20px 12px" : "28px 16px",
        position: "fixed",
        left: 0,
        top: 0,
        height: "100vh",
        zIndex: 99,
        animation: "fadeSlideUp 0.5s ease",
        overflowY: "auto",
      }}
    >
      {/* Logo */}
      <div style={{ padding: isMobile ? "8px 12px 24px" : "8px 16px 32px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div
            style={{
              width: isMobile ? "34px" : "38px",
              height: isMobile ? "34px" : "38px",
              background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              borderRadius: "12px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: isMobile ? "16px" : "18px",
              animation: "pulse-glow 3s ease-in-out infinite",
            }}
          >
            ◈
          </div>
          <div>
            <div
              style={{
                fontSize: isMobile ? "15px" : "17px",
                fontWeight: "700",
                fontFamily: "'Playfair Display', serif",
                letterSpacing: "-0.02em",
              }}
            >
              JobTracker
            </div>
            <div
              style={{
                fontSize: "10px",
                color: "rgba(255,255,255,0.3)",
                letterSpacing: "0.1em",
                textTransform: "uppercase",
              }}
            >
              AI Powered
            </div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, display: "flex", flexDirection: "column", gap: "4px" }}>
        {NAV_ITEMS.map((item, i) => {
          const active = activeNav === item.id;
          return (
            <button
              key={item.id}
              onClick={() => handleNavClick(item.id)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                padding: isMobile ? "10px 12px" : "12px 16px",
                borderRadius: "12px",
                border: "none",
                cursor: "pointer",
                textAlign: "left",
                width: "100%",
                transition: "all 0.2s ease",
                animation: `fadeSlideUp 0.5s ease ${0.1 + i * 0.05}s both`,
                background: active ? "rgba(99,102,241,0.15)" : "transparent",
                color: active ? "#a5b4fc" : "rgba(255,255,255,0.45)",
                borderLeft: active ? "2px solid #6366f1" : "2px solid transparent",
              }}
            >
              <span style={{ fontSize: isMobile ? "16px" : "18px" }}>{item.icon}</span>
              <span style={{ fontSize: isMobile ? "13px" : "14px", fontWeight: active ? "600" : "400" }}>
                {item.label}
              </span>
              {active && (
                <span
                  style={{
                    marginLeft: "auto",
                    width: "6px",
                    height: "6px",
                    borderRadius: "50%",
                    background: "#6366f1",
                  }}
                />
              )}
            </button>
          );
        })}
      </nav>

      {/* Bottom user card */}
      <div
        style={{
          background: "rgba(255,255,255,0.04)",
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: "14px",
          padding: isMobile ? "12px 14px" : "14px 16px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "10px" }}>
          <div
            style={{
              width: isMobile ? "32px" : "36px",
              height: isMobile ? "32px" : "36px",
              borderRadius: "10px",
              background: "linear-gradient(135deg, #6366f1, #34d399)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: isMobile ? "13px" : "15px",
              fontWeight: "700",
              flexShrink: 0,
            }}
          >
            {user?.full_name?.charAt(0).toUpperCase() || "U"}
          </div>
          <div style={{ minWidth: 0, flex: 1 }}>
            <div
              style={{
                fontSize: isMobile ? "12px" : "13px",
                fontWeight: "600",
                color: "#f1f5f9",
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              {user?.full_name || "User"}
            </div>
            <div style={{ 
              fontSize: isMobile ? "10px" : "11px", 
              color: "rgba(255,255,255,0.3)",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}>
              {user?.email}
            </div>
          </div>
        </div>
        <button
          onClick={logout}
          style={{
            width: "100%",
            padding: isMobile ? "7px" : "8px",
            background: "rgba(248,113,113,0.1)",
            border: "1px solid rgba(248,113,113,0.2)",
            borderRadius: "8px",
            color: "#f87171",
            cursor: "pointer",
            fontSize: isMobile ? "11px" : "12px",
            fontWeight: "600",
            transition: "all 0.2s",
          }}
        >
          Logout
        </button>
      </div>
    </div>
  );
}
