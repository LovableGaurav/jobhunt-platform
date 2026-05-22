"use client";

import { useEffect } from "react";
import Link from "next/link";
import {
  ArrowRight,
  Briefcase,
  CheckCircle2,
  Send,
  TrendingUp,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { formatPercent } from "@/lib/utils";
import { useAppStore } from "@/stores/app-store";

export default function DashboardPage() {
  const { stats, fetchDashboard, fetchMatchedJobs, matchedJobs, user } =
    useAppStore();

  useEffect(() => {
    void fetchDashboard();
    void fetchMatchedJobs();
  }, [fetchDashboard, fetchMatchedJobs]);

  const cards = [
    {
      label: "Jobs scraped",
      value: stats?.total_jobs ?? "—",
      icon: Briefcase,
      href: "/jobs",
    },
    {
      label: "Strong matches",
      value: stats?.matched_jobs ?? matchedJobs.length,
      icon: TrendingUp,
      href: "/jobs",
    },
    {
      label: "Applications sent",
      value: stats?.applications_submitted ?? "—",
      icon: Send,
      href: "/applications",
    },
    {
      label: "Interviews",
      value: stats?.interviews ?? "—",
      icon: CheckCircle2,
      href: "/applications",
    },
  ];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">
          Welcome back{user ? `, ${user.full_name.split(" ")[0]}` : ""}
        </h1>
        <p className="mt-1 text-slate-600">
          Your automated job hunt at a glance.
          {stats?.match_rate != null && (
            <span className="ml-2 font-medium text-brand-700">
              Match rate: {formatPercent(stats.match_rate)}
            </span>
          )}
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map(({ label, value, icon: Icon, href }) => (
          <Link
            key={label}
            href={href}
            className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-600">
                {label}
              </span>
              <Icon className="h-4 w-4 text-brand-600" />
            </div>
            <p className="mt-2 text-3xl font-bold text-slate-900">{value}</p>
          </Link>
        ))}
      </div>

      <section className="mt-10">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Top matches</h2>
          <Link href="/jobs">
            <Button variant="ghost" size="sm">
              View all <ArrowRight className="ml-1 h-4 w-4" />
            </Button>
          </Link>
        </div>
        {matchedJobs.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
            No matches yet. Upload your resume and run the embedder worker.
          </div>
        ) : (
          <ul className="space-y-3">
            {matchedJobs.slice(0, 5).map((job) => (
              <li
                key={job.id}
                className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-3"
              >
                <div>
                  <p className="font-medium text-slate-900">{job.title}</p>
                  <p className="text-sm text-slate-600">
                    {job.company} · {job.work_mode}
                  </p>
                </div>
                {job.match_score != null && (
                  <span className="text-sm font-semibold text-brand-700">
                    {Math.round(job.match_score * 100)}%
                  </span>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
