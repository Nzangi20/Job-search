import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Bookmark, Building2, MapPin, ArrowRight } from "lucide-react";

type SavedMatch = {
  id: number;
  overall_score: number;
  job: {
    id: number;
    title: string;
    company: string;
    location: string | null;
    remote: boolean;
    source: string;
    source_url: string;
  };
};

export default function SavedJobsPage() {
  const [matches, setMatches] = useState<SavedMatch[]>([]);

  useEffect(() => {
    api<SavedMatch[]>("/matches?status=saved").then(setMatches).catch(() => {});
  }, []);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <Bookmark className="h-6 w-6 text-amber-400" />
          <span>Saved Opportunities</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Opportunities you have bookmarked for review or future application.
        </p>
      </div>

      <div className="space-y-3">
        {matches.map((m) => (
          <div
            key={m.id}
            className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4 hover:border-slate-700 transition-all"
          >
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <Link
                  to={`/jobs/${m.job.id}`}
                  className="text-lg font-bold text-white hover:text-indigo-400 transition-colors"
                >
                  {m.job.title}
                </Link>
                <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-semibold border border-slate-700">
                  {m.job.source}
                </span>
              </div>
              <div className="flex items-center gap-3 text-xs text-slate-400">
                <span className="flex items-center gap-1 font-medium text-slate-300">
                  <Building2 className="h-3.5 w-3.5 text-slate-400" />
                  {m.job.company}
                </span>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <MapPin className="h-3.5 w-3.5 text-slate-400" />
                  {m.job.remote ? "Remote" : m.job.location || "On-site"}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3 shrink-0">
              <div className="px-3 py-1.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold text-sm">
                {Math.round(m.overall_score)}% Match
              </div>

              <Link
                to={`/jobs/${m.job.id}`}
                className="inline-flex items-center gap-1 px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-all"
              >
                <span>View</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </div>
        ))}

        {!matches.length && (
          <div className="text-center py-12 px-4 rounded-2xl bg-slate-900/40 border border-slate-800">
            <Bookmark className="h-10 w-10 text-slate-500 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-white mb-1">No Saved Jobs Yet</h3>
            <p className="text-slate-400 text-sm max-w-md mx-auto mb-4">
              Click the bookmark icon on any job card in your feed to save it here for later.
            </p>
            <Link
              to="/jobs"
              className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl transition-all"
            >
              Explore Job Matches
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

