"use client";

import { useEffect } from "react";
import { StatusBadge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import { useAppStore } from "@/stores/app-store";

export default function ApplicationsPage() {
  const { applications, fetchApplications, isLoading, error } = useAppStore();

  useEffect(() => {
    void fetchApplications();
  }, [fetchApplications]);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Applications</h1>
        <p className="text-slate-600">
          Full status history for every auto and semi-auto submission.
        </p>
      </div>

      {error && (
        <p className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </p>
      )}

      {isLoading && applications.length === 0 ? (
        <div className="flex justify-center py-16">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-600 border-t-transparent" />
        </div>
      ) : applications.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-12 text-center text-slate-600">
          No applications yet. Apply to a matched job from the Jobs page.
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-slate-200 bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Role</th>
                <th className="px-4 py-3 font-medium">Company</th>
                <th className="px-4 py-3 font-medium">Match</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Applied</th>
              </tr>
            </thead>
            <tbody>
              {applications.map((app) => (
                <tr
                  key={app.id}
                  className="border-b border-slate-100 last:border-0"
                >
                  <td className="px-4 py-3 font-medium text-slate-900">
                    {app.job?.title ?? app.job_id}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {app.job?.company ?? "—"}
                  </td>
                  <td className="px-4 py-3 text-brand-700">
                    {Math.round(app.match_score * 100)}%
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={app.status} />
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {formatDate(app.applied_at ?? app.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
