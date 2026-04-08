"use client";
import { useEffect, useState } from "react";
import ProtectedRoute from "@/app/components/ProtectedRoute";
import { useAuth } from "@/app/components/AuthProvider";
import { apiFetch } from "@/app/lib/api";
import Link from "next/link";

interface PracticeRecord {
  id: number;
  task_id: number;
  asr_text: string;
  relevance_score: number;
  fluency_score: number;
  created_at: string;
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [records, setRecords] = useState<PracticeRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch("/api/user/practice-history?limit=10&offset=0")
      .then((res) => res.json())
      .then((data) => {
        setRecords(data.records || []);
        setTotal(data.total || 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <ProtectedRoute>
      <main style={{ maxWidth: "800px", margin: "40px auto", padding: "0 24px" }}>
        <h1 style={{ marginBottom: "24px" }}>Dashboard</h1>

        {/* Subscription status */}
        <div
          style={{
            padding: "20px",
            border: "1px solid #e5e7eb",
            borderRadius: "12px",
            marginBottom: "32px",
          }}
        >
          <h2 style={{ fontSize: "18px", marginBottom: "12px" }}>
            Subscription Status
          </h2>
          {user?.subscription ? (
            <div>
              <p>
                <strong>Plan:</strong> {user.subscription.display_name}
              </p>
              <p>
                <strong>Status:</strong>{" "}
                <span style={{ color: "#16a34a" }}>
                  {user.subscription.status}
                </span>
              </p>
              <p>
                <strong>Expires:</strong>{" "}
                {new Date(user.subscription.end_date).toLocaleDateString()}
              </p>
            </div>
          ) : (
            <div>
              <p style={{ color: "#6b7280", marginBottom: "12px" }}>
                You are on the Free tier (3 practices/day).
              </p>
              <Link
                href="/pricing"
                style={{
                  padding: "8px 16px",
                  background: "#2563eb",
                  color: "#fff",
                  borderRadius: "6px",
                  textDecoration: "none",
                  fontSize: "14px",
                }}
              >
                Upgrade
              </Link>
            </div>
          )}
        </div>

        {/* Account info */}
        <div
          style={{
            padding: "20px",
            border: "1px solid #e5e7eb",
            borderRadius: "12px",
            marginBottom: "32px",
          }}
        >
          <h2 style={{ fontSize: "18px", marginBottom: "12px" }}>
            Account Settings
          </h2>
          <p>
            <strong>Email:</strong> {user?.email}
          </p>
          <p>
            <strong>Nickname:</strong> {user?.nickname || "Not set"}
          </p>
        </div>

        {/* Practice history */}
        <div
          style={{
            padding: "20px",
            border: "1px solid #e5e7eb",
            borderRadius: "12px",
          }}
        >
          <h2 style={{ fontSize: "18px", marginBottom: "12px" }}>
            Practice History ({total} total)
          </h2>
          {loading ? (
            <p>Loading...</p>
          ) : records.length === 0 ? (
            <p style={{ color: "#6b7280" }}>
              No practice records yet.{" "}
              <Link href="/" style={{ color: "#2563eb" }}>
                Start practicing
              </Link>
            </p>
          ) : (
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                fontSize: "14px",
              }}
            >
              <thead>
                <tr style={{ borderBottom: "1px solid #e5e7eb" }}>
                  <th style={{ textAlign: "left", padding: "8px" }}>Date</th>
                  <th style={{ textAlign: "left", padding: "8px" }}>
                    Transcript
                  </th>
                  <th style={{ textAlign: "center", padding: "8px" }}>
                    Relevance
                  </th>
                  <th style={{ textAlign: "center", padding: "8px" }}>
                    Fluency
                  </th>
                </tr>
              </thead>
              <tbody>
                {records.map((r) => (
                  <tr
                    key={r.id}
                    style={{ borderBottom: "1px solid #f3f4f6" }}
                  >
                    <td style={{ padding: "8px", whiteSpace: "nowrap" }}>
                      {new Date(r.created_at).toLocaleDateString()}
                    </td>
                    <td
                      style={{
                        padding: "8px",
                        maxWidth: "300px",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {r.asr_text}
                    </td>
                    <td style={{ padding: "8px", textAlign: "center" }}>
                      {r.relevance_score}
                    </td>
                    <td style={{ padding: "8px", textAlign: "center" }}>
                      {r.fluency_score}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>
    </ProtectedRoute>
  );
}
