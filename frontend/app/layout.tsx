import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Financial Risk Signal Aggregator",
  description: "Consolidated, prioritised risk summary for compliance review",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
