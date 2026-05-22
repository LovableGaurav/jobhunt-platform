import { cn } from "@/lib/utils";
import { ApplicationStatus } from "@jobhunt/types";

const statusStyles: Record<ApplicationStatus, string> = {
  draft: "bg-slate-100 text-slate-700",
  queued: "bg-amber-100 text-amber-800",
  submitted: "bg-blue-100 text-blue-800",
  viewed: "bg-indigo-100 text-indigo-800",
  interview: "bg-emerald-100 text-emerald-800",
  rejected: "bg-red-100 text-red-800",
  offer: "bg-green-100 text-green-800",
  withdrawn: "bg-slate-100 text-slate-500",
};

export function StatusBadge({ status }: { status: ApplicationStatus }) {
  return (
    <span
      className={cn(
        "inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium capitalize",
        statusStyles[status],
      )}
    >
      {status}
    </span>
  );
}

export function MatchBadge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color =
    pct >= 85
      ? "bg-emerald-100 text-emerald-800"
      : pct >= 70
        ? "bg-brand-100 text-brand-800"
        : "bg-slate-100 text-slate-700";

  return (
    <span
      className={cn(
        "inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold",
        color,
      )}
    >
      {pct}% match
    </span>
  );
}
