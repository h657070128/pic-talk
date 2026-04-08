"use client";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Suspense } from "react";

function PaymentCallbackContent() {
  const params = useSearchParams();
  const status = params.get("status");

  const isSuccess = status === "success";

  return (
    <main
      style={{
        maxWidth: "480px",
        margin: "80px auto",
        padding: "32px",
        textAlign: "center",
        border: "1px solid #e5e7eb",
        borderRadius: "12px",
        background: "#fff",
      }}
    >
      {isSuccess ? (
        <>
          <div style={{ fontSize: "48px", marginBottom: "16px" }}>&#10003;</div>
          <h1 style={{ color: "#16a34a", marginBottom: "12px" }}>
            Payment Successful
          </h1>
          <p style={{ color: "#6b7280", marginBottom: "24px" }}>
            Your subscription has been activated. Enjoy unlimited practice!
          </p>
        </>
      ) : (
        <>
          <div style={{ fontSize: "48px", marginBottom: "16px" }}>&#10007;</div>
          <h1 style={{ color: "#ef4444", marginBottom: "12px" }}>
            Payment Failed
          </h1>
          <p style={{ color: "#6b7280", marginBottom: "24px" }}>
            Something went wrong with your payment. Please try again.
          </p>
        </>
      )}
      <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
        <Link
          href="/"
          style={{
            padding: "10px 20px",
            background: "#2563eb",
            color: "#fff",
            borderRadius: "8px",
            textDecoration: "none",
          }}
        >
          Start Practicing
        </Link>
        <Link
          href="/pricing"
          style={{
            padding: "10px 20px",
            background: "#f3f4f6",
            color: "#374151",
            borderRadius: "8px",
            textDecoration: "none",
          }}
        >
          View Plans
        </Link>
      </div>
    </main>
  );
}

export default function PaymentCallbackPage() {
  return (
    <Suspense
      fallback={
        <div style={{ textAlign: "center", padding: "60px" }}>Loading...</div>
      }
    >
      <PaymentCallbackContent />
    </Suspense>
  );
}
