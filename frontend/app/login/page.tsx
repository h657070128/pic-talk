"use client";
import { useState, FormEvent } from "react";
import { useAuth } from "@/app/components/AuthProvider";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function LoginPage() {
  const { login, user } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (user) {
    router.push("/");
    return null;
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      router.push("/");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main
      style={{
        maxWidth: "400px",
        margin: "80px auto",
        padding: "32px",
        border: "1px solid #e5e7eb",
        borderRadius: "12px",
        background: "#fff",
      }}
    >
      <h1 style={{ textAlign: "center", marginBottom: "24px" }}>Login</h1>
      {error && (
        <p style={{ color: "#ef4444", marginBottom: "16px", textAlign: "center" }}>
          {error}
        </p>
      )}
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "16px" }}>
          <label style={{ display: "block", marginBottom: "4px", fontSize: "14px" }}>
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{
              width: "100%",
              padding: "10px",
              border: "1px solid #d1d5db",
              borderRadius: "6px",
              fontSize: "14px",
              boxSizing: "border-box",
            }}
          />
        </div>
        <div style={{ marginBottom: "24px" }}>
          <label style={{ display: "block", marginBottom: "4px", fontSize: "14px" }}>
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            style={{
              width: "100%",
              padding: "10px",
              border: "1px solid #d1d5db",
              borderRadius: "6px",
              fontSize: "14px",
              boxSizing: "border-box",
            }}
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          style={{
            width: "100%",
            padding: "12px",
            background: "#2563eb",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            fontSize: "16px",
            cursor: loading ? "not-allowed" : "pointer",
            opacity: loading ? 0.7 : 1,
          }}
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
      <p style={{ textAlign: "center", marginTop: "16px", fontSize: "14px" }}>
        Don&apos;t have an account?{" "}
        <Link href="/register" style={{ color: "#2563eb" }}>
          Register
        </Link>
      </p>
    </main>
  );
}
