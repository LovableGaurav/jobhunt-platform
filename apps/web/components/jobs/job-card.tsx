"use client";

import { useState } from "react";
import { ExternalLink, MapPin } from "lucide-react";
import type { JobPosting } from "@jobhunt/types";
import { Button } from "@/components/ui/button";
import { MatchBadge } from "@/components/ui/badge";
import { useAppStore } from "@/stores/app-store";

export function JobCard({ job }: { job: JobPosting }) {
  const applyToJob = useAppStore((s) => s.applyToJob);
  const [applying, setApplying] = useState(false);
  const [applied, setApplied] = useState(false);

  async function handleApply() {
    setApplying(true);
    try {
      await applyToJob(job.id);
      setApplied(true);
    } catch {
      /* store surfaces error */
    } finally {
      setApplying(false);
    }
  }

  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">{job.title}</h3>
          <p className="text-sm font-medium text-slate-600">{job.company}</p>
        </div>
        {job.match_score != null && <MatchBadge score={job.match_score} />}
      </div>
      <div className="mt-3 flex flex-wrap gap-3 text-sm text-slate-500">
        <span className="inline-flex items-center gap-1">
          <MapPin className="h-3.5 w-3.5" />
          {job.location} · {job.work_mode}
        </span>
        <span className="capitalize">{job.experience_level}</span>
        <span className="capitalize">{job.source}</span>
      </div>
      <p className="mt-3 line-clamp-2 text-sm text-slate-600">
        {job.description}
      </p>
      <div className="mt-4 flex flex-wrap gap-2">
        <Button
          size="sm"
          onClick={handleApply}
          disabled={applying || applied}
        >
          {applied ? "Queued" : applying ? "Applying…" : "Auto-apply"}
        </Button>
        <a
          href={job.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex h-8 items-center gap-1 rounded-lg px-3 text-sm font-medium text-brand-700 hover:bg-brand-50"
        >
          View posting
          <ExternalLink className="h-3.5 w-3.5" />
        </a>
      </div>
    </article>
  );
}
