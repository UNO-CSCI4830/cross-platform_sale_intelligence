import { COLORS } from "../constants/data";

// ── Badge ─────────────────────────────────────────────────────────────────
// Props: label (string), color (hex string)
export function Badge({ label, color }) {
  return (
    <span style={{
      fontSize: "10px",
      fontWeight: 700,
      letterSpacing: "0.06em",
      textTransform: "uppercase",
      padding: "2px 8px",
      borderRadius: "3px",
      background: color + "22",
      color: color,
      border: `1px solid ${color}44`,
    }}>
      {label}
    </span>
  );
}

// ── ConditionDots ─────────────────────────────────────────────────────────
// Renders 1–5 filled dots based on condition string
// Props: condition (string matching CONDITIONS array)
export function ConditionDots({ condition }) {
  const levels = {
    "New with Tags": 5,
    "Like New": 4,
    "Good": 3,
    "Fair": 2,
    "Poor": 1,
  };
  const level = levels[condition] || 0;

  return (
    <div style={{ display: "flex", gap: "3px", alignItems: "center" }}>
      {[1, 2, 3, 4, 5].map((i) => (
        <div
          key={i}
          style={{
            width: 6,
            height: 6,
            borderRadius: "50%",
            background: i <= level ? COLORS.accent : COLORS.border,
          }}
        />
      ))}
    </div>
  );
}
