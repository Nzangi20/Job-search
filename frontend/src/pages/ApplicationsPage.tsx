import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import {
  CheckCircle2,
  Calendar,
  XCircle,
  Trophy,
  ExternalLink,
  Building2,
  Sparkles,
} from "lucide-react";

type AppRow = {
  id: number;
  status: string;
  notes: string | null;
  job: {
    id: number;
    title: string;
    company: string;
    location: string | null;
    source_url: string;
  } | null;
};

export default function ApplicationsPage() {
  const [apps, setApps] = useState<AppRow[]>([]);

  const load = () => api<AppRow[]>("/applications").then(setApps).catch(() => {});

  useEffect(() => {
    load();
  }, []);

  const updateStatus = async (appId: number, status: string) => {
    await api(`/applications/${appId}`, {
      method: "PUT",
      body: JSON.stringify({ status }),
    });
    load();
  };

  const counts = apps.reduce(
    (acc, a) => {
      acc[a.status] = (acc[a.status] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <CheckCircle2 className="h-6 w-6 text-indigo-400" />
          <span>Job Application Tracker</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Track the status of your submitted applications, interview stages, and job offers.
        </p>
      </div>

      {/* Metric Tiles */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
        {[
          { key: "applied", label: "Applied", icon: CheckCircle2, color: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/20" },
          { key: "interview", label: "Interviewing", icon: Calendar, color: "text-indigo-400", bg: "bg-indigo-500/10", border: "border-indigo-500/20" },
          { key: "rejected", label: "Rejected", icon: XCircle, color: "text-slate-400", bg: "bg-slate-500/10", border: "border-slate-500/20" },
          { key: "offer", label: "Job Offer", icon: Trophy, color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20" },
        ].map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.key} className={`bg-slate-900/60 border ${item.border} rounded-2xl p-4 backdrop-blur-sm`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-400">{item.label}</span>
                <div className={`p-1.5 rounded-lg ${item.bg}`}>
                  <Icon className={`h-4 w-4 ${item.color}`} />
                </div>
              </div>
              <div className={`text-2xl font-extrabold ${item.color}`}>{counts[item.key] || 0}</div>
            </div>
          );
        })}
      </div>

      {/* Applications List */}
      <div className="space-y-3">
        {apps.map((a) => (
          <div
            key={a.id}
            className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4 hover:border-slate-700 transition-all"
          >
            <div className="flex-1 min-w-0">
              {a.job ? (
                <div>
                  <Link
                    to={`/jobs/${a.job.id}`}
                    className="text-base font-bold text-white hover:text-indigo-400 transition-colors"
                  >
                    {a.job.title}
                  </Link>
                  <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
                    <span className="flex items-center gap-1 text-slate-300 font-medium">
                      <Building2 className="h-3.5 w-3.5 text-slate-400" />
                      {a.job.company}
                    </span>
                    <span>•</span>
                    <span>{a.job.location || "Remote"}</span>
                  </div>
                </div>
              ) : (
                <span className="font-semibold text-slate-300">Application #{a.id}</span>
              )}
            </div>

            <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-end border-t md:border-t-0 pt-3 md:pt-0 border-slate-800">
              <select
                value={a.status}
                onChange={(e) => updateStatus(a.id, e.target.value)}
                className="px-3 py-1.5 bg-slate-950 border border-slate-700/80 rounded-xl text-xs font-medium text-slate-200 capitalize focus:outline-none focus:border-indigo-500"
              >
                <option value="applied">Applied</option>
                <option value="interview">Interview</option>
                <option value="offer">Offer</option>
                <option value="rejected">Rejected</option>
                <option value="saved">Saved</option>
              </select>

              {a.job?.source_url && (
                <a
                  href={a.job.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition-all"
                  title="Open Original Job Link"
                >
                  <ExternalLink className="h-4 w-4" />
                </a>
              )}
            </div>
          </div>
        ))}

        {!apps.length && (
          <div className="text-center py-12 px-4 rounded-2xl bg-slate-900/40 border border-slate-800">
            <Sparkles className="h-10 w-10 text-slate-500 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-white mb-1">No Applications Tracked Yet</h3>
            <p className="text-slate-400 text-sm max-w-md mx-auto mb-4">
              When you apply to job opportunities, mark them as "Applied" from the Job Matches feed to track your progress here.
            </p>
            <Link
              to="/jobs"
              className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl transition-all"
            >
              Browse Job Matches
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

