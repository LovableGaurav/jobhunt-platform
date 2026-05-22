"use client";

import { useEffect, useState } from "react";
import { JobCard } from "@/components/jobs/job-card";
import { Button } from "@/components/ui/button";
import { useAppStore } from "@/stores/app-store";

type Tab = "all" | "matches";

export default function JobsPage() {
  const { jobs, matchedJobs, fetchJobs, fetchMatchedJobs, isLoading, error } =
    useAppStore();
  const [tab, setTab] = useState<Tab>("matches");

  useEffect(() => {
    void fetchJobs();
    void fetchMatchedJobs();
  }, [fetchJobs, fetchMatchedJobs]);

  const list = tab === "matches" ? matchedJobs : jobs;

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Jobs</h1>
          <p className="text-slate-600">
            Entry-level remote & hybrid roles from daily scrapers.
          </p>
        </div>
        <div className="flex rounded-lg border border-slate-200 bg-white p-1">
          <Button
            size="sm"
            variant={tab === "matches" ? "primary" : "ghost"}
            onClick={() => setTab("matches")}
          >
            Matches ({matchedJobs.length})
          </Button>
          <Button
            size="sm"
            variant={tab === "all" ? "primary" : "ghost"}
            onClick={() => setTab("all")}
          >
            All ({jobs.length})
          </Button>
        </div>
      </div>

      {error && (
        <p className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </p>
      )}

      {isLoading && list.length === 0 ? (
        <div className="flex justify-center py-16">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-600 border-t-transparent" />
        </div>
      ) : list.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-12 text-center text-slate-600">
          {tab === "matches"
            ? "No strong matches yet. Check back after the next scrape + embed run."
            : "No jobs in the database. Start Celery workers to scrape boards."}
        </div>
      ) : (
        <div className="grid gap-4">
          {list.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      )}
    </div>
  );
}
