import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { History, RotateCw, Calendar } from "lucide-react";

type SearchRow = { id: number; query: string; jobs_found: number; created_at: string };

export default function SearchesPage() {
  const [rows, setRows] = useState<SearchRow[]>([]);
  const [rerunning, setRerunning] = useState<number | null>(null);

  useEffect(() => {
    api<SearchRow[]>("/searches").then(setRows).catch(() => {});
  }, []);

  const rerun = async (query: string, id: number) => {
    setRerunning(id);
    try {
      await api("/jobs/search", { method: "POST", body: JSON.stringify({ query }) });
      const updated = await api<SearchRow[]>("/searches");
      setRows(updated);
    } finally {
      setRerunning(null);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <History className="h-6 w-6 text-indigo-400" />
          <span>Job Search Log & History</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Historical log of automated and manual job searches. Rerun past searches anytime.
        </p>
      </div>

      <div className="space-y-3">
        {rows.map((r) => (
          <div
            key={r.id}
            className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:border-slate-700 transition-all"
          >
            <div>
              <div className="font-bold text-base text-white flex items-center gap-2">
                <span>{r.query}</span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 font-semibold">
                  {r.jobs_found} jobs collected
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
                <Calendar className="h-3.5 w-3.5 text-slate-500" />
                <span>Executed {new Date(r.created_at).toLocaleString()}</span>
              </div>
            </div>

            <button
              onClick={() => rerun(r.query, r.id)}
              disabled={rerunning === r.id}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 text-xs font-semibold transition-all disabled:opacity-50 shrink-0"
            >
              <RotateCw className={`h-3.5 w-3.5 ${rerunning === r.id ? "animate-spin text-indigo-400" : ""}`} />
              <span>{rerunning === r.id ? "Rerunning..." : "Rerun Search"}</span>
            </button>
          </div>
        ))}

        {!rows.length && (
          <div className="text-center py-12 px-4 rounded-2xl bg-slate-900/40 border border-slate-800">
            <History className="h-10 w-10 text-slate-500 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-white mb-1">No Search Log Found</h3>
            <p className="text-slate-400 text-sm max-w-md mx-auto">
              Run job searches to automatically populate your historical search queries here.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

