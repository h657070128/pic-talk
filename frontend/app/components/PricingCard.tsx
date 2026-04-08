"use client";

interface PricingCardProps {
  name: string;
  displayName: string;
  priceDisplay: string;
  perMonthDisplay: string;
  durationDays: number;
  highlighted?: boolean;
  onSubscribe: () => void;
}

export default function PricingCard({
  displayName,
  priceDisplay,
  perMonthDisplay,
  durationDays,
  highlighted = false,
  onSubscribe,
}: PricingCardProps) {
  return (
    <div
      style={{
        border: highlighted ? "2px solid #2563eb" : "1px solid #e5e7eb",
        borderRadius: "12px",
        padding: "32px 24px",
        textAlign: "center",
        background: highlighted ? "#eff6ff" : "#fff",
        position: "relative",
        flex: "1",
        maxWidth: "320px",
      }}
    >
      {highlighted && (
        <div
          style={{
            position: "absolute",
            top: "-12px",
            left: "50%",
            transform: "translateX(-50%)",
            background: "#2563eb",
            color: "#fff",
            padding: "2px 16px",
            borderRadius: "9999px",
            fontSize: "12px",
            fontWeight: 600,
          }}
        >
          Most Popular
        </div>
      )}
      <h3 style={{ fontSize: "20px", marginBottom: "8px" }}>{displayName}</h3>
      <div style={{ fontSize: "36px", fontWeight: 700, margin: "16px 0" }}>
        {priceDisplay}
      </div>
      <p style={{ color: "#6b7280", marginBottom: "8px" }}>
        {perMonthDisplay}
      </p>
      <p style={{ color: "#9ca3af", fontSize: "14px", marginBottom: "24px" }}>
        {durationDays} days
      </p>
      <ul
        style={{
          listStyle: "none",
          padding: 0,
          textAlign: "left",
          marginBottom: "24px",
          fontSize: "14px",
          color: "#374151",
        }}
      >
        <li style={{ marginBottom: "8px" }}>Unlimited daily practices</li>
        <li style={{ marginBottom: "8px" }}>AI task generation</li>
        <li style={{ marginBottom: "8px" }}>Full practice history</li>
        <li style={{ marginBottom: "8px" }}>Detailed AI feedback</li>
        <li>All difficulty levels</li>
      </ul>
      <button
        onClick={onSubscribe}
        style={{
          width: "100%",
          padding: "12px",
          background: highlighted ? "#2563eb" : "#374151",
          color: "#fff",
          border: "none",
          borderRadius: "8px",
          fontSize: "16px",
          cursor: "pointer",
          fontWeight: 600,
        }}
      >
        Subscribe
      </button>
    </div>
  );
}
