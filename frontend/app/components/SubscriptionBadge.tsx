"use client";

interface SubscriptionBadgeProps {
  subscription: {
    plan_name: string;
    display_name: string;
    status: string;
  } | null;
}

export default function SubscriptionBadge({
  subscription,
}: SubscriptionBadgeProps) {
  if (!subscription || subscription.status !== "active") {
    return (
      <span
        style={{
          padding: "2px 8px",
          fontSize: "12px",
          borderRadius: "9999px",
          background: "#f3f4f6",
          color: "#6b7280",
        }}
      >
        Free
      </span>
    );
  }

  return (
    <span
      style={{
        padding: "2px 8px",
        fontSize: "12px",
        borderRadius: "9999px",
        background: "#dbeafe",
        color: "#1d4ed8",
        fontWeight: 600,
      }}
    >
      {subscription.display_name}
    </span>
  );
}
