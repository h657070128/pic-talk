"use client";
import { useAuth } from "./AuthProvider";
import { useRouter } from "next/navigation";
import { useEffect, ReactNode } from "react";

export default function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "60px" }}>Loading...</div>
    );
  }

  if (!user) return null;

  return <>{children}</>;
}
