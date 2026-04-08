"use client";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import Link from "next/link";
import ProtectedRoute from "@/app/components/ProtectedRoute";

function PaymentContent() {
  const searchParams = useSearchParams();
  const orderId = searchParams.get("order_id") || "";

  return (
    <ProtectedRoute>
      <main
        style={{
          maxWidth: "480px",
          margin: "60px auto",
          padding: "32px",
          textAlign: "center",
          border: "1px solid #e5e7eb",
          borderRadius: "12px",
        }}
      >
        <h1 style={{ marginBottom: "16px" }}>Complete Payment</h1>
        <p style={{ color: "#6b7280", marginBottom: "24px" }}>
          Scan the QR code with WeChat to complete your payment
        </p>

        {/* QR code placeholder */}
        <div
          style={{
            width: "200px",
            height: "200px",
            margin: "0 auto 24px",
            border: "2px dashed #d1d5db",
            borderRadius: "12px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#9ca3af",
          }}
        >
          QR Code
        </div>

        <p style={{ fontSize: "14px", color: "#6b7280", marginBottom: "8px" }}>
          Order: {orderId}
        </p>
        <p style={{ fontSize: "14px", color: "#9ca3af" }}>
          Waiting for payment confirmation...
        </p>

        <Link
          href="/pricing"
          style={{
            display: "inline-block",
            marginTop: "24px",
            color: "#2563eb",
          }}
        >
          Back to pricing
        </Link>
      </main>
    </ProtectedRoute>
  );
}

export default function PaymentPage() {
  return (
    <Suspense
      fallback={
        <div style={{ textAlign: "center", padding: "60px" }}>Loading...</div>
      }
    >
      <PaymentContent />
    </Suspense>
  );
}
