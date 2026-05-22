import { AuthGuard } from "@/components/auth/auth-guard";
import { SiteHeader } from "@/components/layout/site-header";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <div className="min-h-screen bg-slate-50">
        <SiteHeader />
        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
      </div>
    </AuthGuard>
  );
}
