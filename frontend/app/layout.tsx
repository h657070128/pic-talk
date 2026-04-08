import type { Metadata } from "next";
import "./globals.css";
import ClientLayout from "./components/ClientLayout";

export const metadata: Metadata = {
  title: "Pic-Talk - AI English Speaking Practice",
  description: "AI-powered English speaking practice with image descriptions",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  );
}
