import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "JobHunt — Automated Applications for Freshers",
  description:
    "Scrape, match, tailor, and apply to entry-level ML, DS, and SWE roles automatically.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
