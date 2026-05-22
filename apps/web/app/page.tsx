import Link from "next/link";
import {
  Bot,
  Filter,
  Sparkles,
  Target,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const features = [
  {
    icon: Filter,
    title: "Entry-level only",
    description:
      "Remote and hybrid roles filtered for 0–2 years experience in ML, DS, and SWE.",
  },
  {
    icon: Sparkles,
    title: "Semantic matching",
    description:
      "Resume embeddings matched to job descriptions via pgvector cosine similarity.",
  },
  {
    icon: Bot,
    title: "AI tailoring",
    description:
      "GPT-4o tailors your resume and cover letter per role — no fabricated experience.",
  },
  {
    icon: Zap,
    title: "Auto-apply",
    description:
      "Easy Apply and semi-automatic flows with full status tracking in one dashboard.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-brand-50 via-white to-white">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-4 py-6">
        <span className="text-xl font-bold text-brand-700">JobHunt</span>
        <div className="flex gap-3">
          <Link href="/login">
            <Button variant="ghost">Log in</Button>
          </Link>
          <Link href="/login">
            <Button>Get started</Button>
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 pb-20 pt-12">
        <section className="text-center">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-brand-100 px-4 py-1.5 text-sm font-medium text-brand-800">
            <Target className="h-4 w-4" />
            Built for freshers · 0–2 years
          </div>
          <h1 className="text-balance text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
            Stop scrolling job boards.
            <br />
            <span className="text-brand-600">Start getting interviews.</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-600">
            JobHunt scrapes LinkedIn, Indeed, Wellfound, and more — filters for
            entry-level remote roles, matches your resume, tailors applications,
            and tracks every submission.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <Link href="/login">
              <Button size="lg">Start free →</Button>
            </Link>
            <Link href="/dashboard">
              <Button size="lg" variant="secondary">
                View demo dashboard
              </Button>
            </Link>
          </div>
        </section>

        <section className="mt-20 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {features.map(({ icon: Icon, title, description }) => (
            <div
              key={title}
              className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
            >
              <div className="mb-4 inline-flex rounded-lg bg-brand-50 p-2 text-brand-600">
                <Icon className="h-5 w-5" />
              </div>
              <h3 className="font-semibold text-slate-900">{title}</h3>
              <p className="mt-2 text-sm text-slate-600">{description}</p>
            </div>
          ))}
        </section>
      </main>
    </div>
  );
}
