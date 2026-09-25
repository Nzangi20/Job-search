import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import {
  Sparkles,
  TrendingUp,
  Award,
  CheckCircle2,
  Bookmark,
  XCircle,
  ArrowRight,
  MapPin,
  Building2,
  Zap,
  Search,
  Check,
} from "lucide-react";

type Stats = {
  new_matches: number;
  high_matches: number;
  applied: number;
  saved: number;
  rejected: number;
};

type Match = {
  id: number;
  overall_score: number;
  match_reasons: string[];
  gap_reasons: string[];
  status: string;
  job: {
    id: number;
    title: string;
    company: string;
    location: string | null;
    remote: boolean;
    source: string;
    source_url: string;
    posted_at: string | null;
    skills: string[];
  };
};

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const loadData = () => {
    api<Stats>("/dashboard/stats").then(setStats).catch(() => {});
    api<Match[]>("/matches?min_match=70").then(setMatches).catch(() => {});
  };

  useEffect(() => {
    loadData();
  }, []);

  const triggerSearch = async () => {
    setSearching(true);
    try {
      await api("/jobs/search", {
        method: "POST",
        body: JSON.stringify({ query: searchQuery || undefined }),
      });
      loadData();
    } finally {
      setSearching(false);
    }
  };

  const handleSave = async (e: React.MouseEvent, jobId: number) => {
    e.preventDefault();
    e.stopPropagation();
    await api(`/jobs/${jobId}/save`, { method: "POST" });
    loadData();
  };

  return (
    <div className="space-y-8">
      {/* Top Banner / Hero Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-900/40 via-purple-900/30 to-slate-900 border border-indigo-500/20 p-6 md:p-8 backdrop-blur-xl">
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold mb-3">
              <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
              Automated Job Discovery & Matching
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Welcome back to AI Job Hunter
            </h1>
            <p className="text-slate-300 text-sm mt-1 max-w-2xl">
              Continuous candidate-to-job matching enabled. Review your highest compatibility job opportunities below.
            </p>
          </div>

          {/* Quick Search Box */}
          <div className="w-full md:w-auto flex flex-col sm:flex-row gap-2.5">
            <div className="relative flex-1 sm:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Target role or keyword..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && triggerSearch()}
                className="w-full pl-9 pr-3 py-2 bg-slate-950/80 border border-slate-700/80 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
            <button
              onClick={triggerSearch}
              disabled={searching}
              className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl transition-all shadow-lg shadow-indigo-600/30 disabled:opacity-50"
            >
              <Zap className={`h-4 w-4 ${searching ? "animate-spin" : ""}`} />
              <span>{searching ? "Searching..." : "Find Jobs"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Metric Tiles */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3.5">
          {[
            { label: "New Matches", val: stats.new_matches, icon: TrendingUp, color: "text-indigo-400", bg: "bg-indigo-500/10", border: "border-indigo-500/20" },
            { label: "High Matches (80%+)", val: stats.high_matches, icon: Award, color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20" },
            { label: "Applied", val: stats.applied, icon: CheckCircle2, color: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/20" },
            { label: "Saved", val: stats.saved, icon: Bookmark, color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/20" },
            { label: "Rejected", val: stats.rejected, icon: XCircle, color: "text-slate-400", bg: "bg-slate-500/10", border: "border-slate-500/20" },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.label}
                className={`bg-slate-900/90 border ${item.border} rounded-2xl p-4 hover:border-slate-700 transition-colors shadow-sm`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-slate-400">{item.label}</span>
                  <div className={`p-1.5 rounded-lg ${item.bg}`}>
                    <Icon className={`h-4 w-4 ${item.color}`} />
                  </div>
                </div>
                <div className={`text-2xl md:text-3xl font-extrabold ${item.color}`}>{item.val}</div>
              </div>
            );
          })}
        </div>
      )}

      {/* Top Recommendations Feed Header */}
      <div className="flex justify-between items-center pt-2">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <span>Top Compatibility Matches</span>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Personalized
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Jobs discovered across configured sources, ordered by explainable match score
          </p>
        </div>
        <Link
          to="/jobs"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
        >
          <span>View All Matches</span>
          <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>

      {/* Matches Grid / List */}
      <div className="space-y-4">
        {matches.slice(0, 6).map((m) => {
          const score = Math.round(m.overall_score);
          let scoreBadgeColor = "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
          if (score < 80) scoreBadgeColor = "text-indigo-400 bg-indigo-500/10 border-indigo-500/30";
          if (score < 70) scoreBadgeColor = "text-amber-400 bg-amber-500/10 border-amber-500/30";

          return (
            <div
              key={m.id}
              className="group bg-slate-900/90 border border-slate-800 hover:border-indigo-500/50 rounded-2xl p-5 transition-colors shadow-md hover:shadow-indigo-950/20"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-1">
                    <Link
                      to={`/jobs/${m.job.id}`}
                      className="text-lg font-bold text-white hover:text-indigo-400 truncate transition-colors"
                    >
                      {m.job.title}
                    </Link>
                    <span className="shrink-0 text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                      {m.job.source}
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400">
                    <span className="flex items-center gap-1 font-medium text-slate-300">
                      <Building2 className="h-3.5 w-3.5 text-slate-400" />
                      {m.job.company}
                    </span>
                    <span className="flex items-center gap-1">
                      <MapPin className="h-3.5 w-3.5 text-slate-400" />
                      {m.job.remote ? "Remote" : m.job.location || "On-site"}
                    </span>
                  </div>
                </div>

                {/* Score Pill & Actions */}
                <div className="flex items-center justify-between md:justify-end gap-3 border-t md:border-t-0 pt-3 md:pt-0 border-slate-800">
                  <div className={`px-4 py-2 rounded-xl border font-bold text-lg md:text-xl flex items-center gap-1.5 ${scoreBadgeColor}`}>
                    <span>{score}%</span>
                    <span className="text-[10px] font-normal uppercase tracking-wider opacity-80">Match</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={(e) => handleSave(e, m.job.id)}
                      className="p-2 rounded-xl border border-slate-800 hover:border-amber-500/50 text-slate-400 hover:text-amber-400 bg-slate-900 hover:bg-amber-500/10 transition-all"
                      title="Save Job"
                    >
                      <Bookmark className="h-4 w-4" />
                    </button>
                    <Link
                      to={`/jobs/${m.job.id}`}
                      className="px-3.5 py-2 rounded-xl bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white border border-indigo-500/30 text-xs font-semibold transition-all flex items-center gap-1.5"
                    >
                      <span>Analyze</span>
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  </div>
                </div>
              </div>

              {/* Match Reason Highlights */}
              {m.match_reasons && m.match_reasons.length > 0 && (
                <div className="mt-3.5 pt-3 border-t border-slate-800/60 flex flex-wrap gap-2 text-xs">
                  {m.match_reasons.slice(0, 3).map((r, i) => (
                    <span key={i} className="flex items-center gap-1 text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-lg border border-emerald-500/20">
                      <Check className="h-3 w-3 shrink-0" />
                      <span>{r}</span>
                    </span>
                  ))}
                </div>
              )}
            </div>
          );
        })}

        {!matches.length && (
          <div className="text-center py-12 px-4 rounded-2xl bg-slate-900/40 border border-slate-800">
            <Sparkles className="h-10 w-10 text-indigo-400 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-white mb-1">No Job Matches Discovered Yet</h3>
            <p className="text-slate-400 text-sm max-w-md mx-auto mb-6">
              Upload your CV and define your job preferences to let the AI search engine collect and rank opportunities.
            </p>
            <div className="flex justify-center gap-3">
              <Link
                to="/resume"
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl transition-all"
              >
                Upload CV First
              </Link>
              <button
                onClick={triggerSearch}
                disabled={searching}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-sm rounded-xl border border-slate-700 transition-all"
              >
                Run Search Now
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

