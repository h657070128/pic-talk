"use client";
import Link from "next/link";
import { useAuth } from "./AuthProvider";
import SubscriptionBadge from "./SubscriptionBadge";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "12px 24px",
        borderBottom: "1px solid #e5e7eb",
        background: "#fff",
      }}
    >
      <Link
        href="/"
        style={{
          fontWeight: 700,
          fontSize: "20px",
          color: "#2563eb",
          textDecoration: "none",
        }}
      >
        Pic-Talk
      </Link>

      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        <Link href="/pricing" style={{ color: "#374151", textDecoration: "none" }}>
          Pricing
        </Link>
        {user ? (
          <>
            <SubscriptionBadge subscription={user.subscription} />
            <Link
              href="/dashboard"
              style={{ color: "#374151", textDecoration: "none" }}
            >
              Dashboard
            </Link>
            <span style={{ color: "#6b7280", fontSize: "14px" }}>
              {user.nickname || user.email}
            </span>
            <button
              onClick={logout}
              style={{
                padding: "6px 14px",
                background: "#ef4444",
                color: "#fff",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "14px",
              }}
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link
              href="/login"
              style={{
                padding: "6px 14px",
                color: "#2563eb",
                textDecoration: "none",
              }}
            >
              Login
            </Link>
            <Link
              href="/register"
              style={{
                padding: "6px 14px",
                background: "#2563eb",
                color: "#fff",
                borderRadius: "6px",
                textDecoration: "none",
              }}
            >
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
