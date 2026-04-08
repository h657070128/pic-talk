"use client";
import { AuthProvider } from "./AuthProvider";
import Navbar from "./Navbar";
import { ReactNode } from "react";

export default function ClientLayout({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <Navbar />
      {children}
    </AuthProvider>
  );
}
