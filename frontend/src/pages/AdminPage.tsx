import { useEffect, useState } from "react";
import { api } from "../lib/api";
import {
  ShieldAlert,
  Users,
  Briefcase,
  Layers,
  AlertTriangle,
  ToggleLeft,
  ToggleRight,
  Plus,
  Sliders,
  Terminal,
  Sparkles,
} from "lucide-react";

type Source = {
  id: number;
  name: string;
  source_type: string;
  enabled: boolean;
  config: Record<string, unknown>;
  last_error: string | null;
};

type Log = {
  level: string;
  message: string;
  created_at: string;
};

export default function AdminPage() {
  const [stats, setStats] = useState<Record<string, number> | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const [weights, setWeights] = useState<Record<string, number>>({});
  const [logs, setLogs] = useState<Log[]>([]);
  const [newSourceName, setNewSourceName] = useState("");
  const [newSourceType, setNewSourceType] = useState("rss");
  const [newFeedUrl, setNewFeedUrl] = useState("");
  const [addingSource, setAddingSource] = useState(false);

  const loadData = () => {
    api<Record<string, number>>("/admin/stats").then(setStats).catch(() => {});
    api<Source[]>("/admin/job-sources").then(setSources).catch(() => {});
    api<Record<string, number>>("/admin/weights").then(setWeights).catch(() => {});
    api<Log[]>("/admin/logs").then(setLogs).catch(() => {});
  };

  useEffect(() => {
    loadData();
  }, []);

  const toggleSource = async (id: number) => {
    await api(`/admin/job-sources/${id}/toggle`, { method: "PUT" });
    loadData();
  };

  const handleAddSource = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSourceName.trim()) return;
    setAddingSource(true);
    try {
      await api("/admin/job-sources", {
        method: "POST",
        body: JSON.stringify({
          name: newSourceName,
          source_type: newSourceType,
          config: newSourceType === "rss" ? { feed_url: newFeedUrl } : {},
          enabled: true,
        }),
      });
      setNewSourceName("");
      setNewFeedUrl("");
      loadData();
    } finally {
      setAddingSource(false);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <ShieldAlert className="h-6 w-6 text-amber-400" />
          <span>System Admin Console</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Monitor system metrics, manage active job sources, inspect matching weights, and view system error logs.
        </p>
      </div>

      {/* Metrics Grid */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3.5">
          {[
            { key: "users", label: "Registered Users", icon: Users, color: "text-indigo-400" },
            { key: "jobs_collected", label: "Jobs Collected", icon: Briefcase, color: "text-emerald-400" },
            { key: "jobs_matched", label: "Jobs Matched", icon: Layers, color: "text-blue-400" },
            { key: "active_sources", label: "Active Sources", icon: Sparkles, color: "text-amber-400" },
            { key: "search_errors", label: "Source Errors", icon: AlertTriangle, color: "text-rose-400" },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.key} className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 backdrop-blur-sm">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-slate-400">{item.label}</span>
                  <Icon className={`h-4 w-4 ${item.color}`} />
                </div>
                <div className={`text-2xl font-extrabold ${item.color}`}>{stats[item.key] || 0}</div>
              </div>
            );
          })}
        </div>
      )}

      {/* Job Sources Section */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-6">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Briefcase className="h-5 w-5 text-indigo-400" />
          <span>Configured Job Discovery Sources</span>
        </h2>

        {/* Existing Sources List */}
        <div className="space-y-3">
          {sources.map((s) => (
            <div
              key={s.id}
              className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-3"
            >
              <div>
                <div className="font-bold text-sm text-white flex items-center gap-2">
                  <span>{s.name}</span>
                  <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 uppercase font-semibold">
                    {s.source_type}
                  </span>
                </div>
                {s.last_error && (
                  <p className="text-xs text-rose-400 mt-1 max-w-lg truncate">
                    Last error: {s.last_error}
                  </p>
                )}
              </div>

              <button
                onClick={() => toggleSource(s.id)}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all border ${
                  s.enabled
                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/20"
                    : "bg-slate-800 text-slate-400 border-slate-700 hover:bg-slate-700"
                }`}
              >
                {s.enabled ? <ToggleRight className="h-4 w-4 text-emerald-400" /> : <ToggleLeft className="h-4 w-4 text-slate-500" />}
                <span>{s.enabled ? "Active" : "Disabled"}</span>
              </button>
            </div>
          ))}
        </div>

        {/* Add Source Form */}
        <form onSubmit={handleAddSource} className="pt-4 border-t border-slate-800 space-y-3">
          <div className="text-xs font-semibold text-slate-300">Add New Permitted Job Source</div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <input
              placeholder="Source Name (e.g. RemoteOK RSS)"
              value={newSourceName}
              onChange={(e) => setNewSourceName(e.target.value)}
              className="px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            />
            <select
              value={newSourceType}
              onChange={(e) => setNewSourceType(e.target.value)}
              className="px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="rss">RSS Feed</option>
              <option value="remotive">Remotive API</option>
              <option value="jobicy">Jobicy API</option>
              <option value="brightermonday">BrighterMonday Kenya</option>
              <option value="fuzu">Fuzu Kenya</option>
              <option value="myjobmag">MyJobMag Kenya</option>
              <option value="careerpoint">Career Point Kenya</option>
              <option value="jobwebkenya">JobWeb Kenya</option>
              <option value="remoteok">Remote OK API</option>
              <option value="remoteco">Remote.co</option>
              <option value="wellfound">Wellfound</option>
              <option value="himalayas">Himalayas API</option>
              <option value="telusdigital">TELUS Digital AI</option>
              <option value="rws">RWS AI</option>
              <option value="outlier">Outlier AI</option>
              <option value="mindrift">Mindrift AI</option>
              <option value="welocalize">Welocalize</option>
              <option value="cloudfactory">CloudFactory Workable</option>
              <option value="oneforma">OneForma</option>
              <option value="contra">Contra</option>
              <option value="lemon">Lemon.io</option>
              <option value="arc">Arc.dev</option>
              <option value="turing">Turing Greenhouse</option>
            </select>

            {newSourceType === "rss" ? (
              <input
                placeholder="Feed URL (https://.../feed.rss)"
                value={newFeedUrl}
                onChange={(e) => setNewFeedUrl(e.target.value)}
                className="px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            ) : (
              <div className="flex items-center text-xs text-slate-500 px-3">Public API Endpoint</div>
            )}
          </div>
          <button
            type="submit"
            disabled={addingSource || !newSourceName.trim()}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl transition-all disabled:opacity-50"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>Add Job Source</span>
          </button>
        </form>
      </div>

      {/* Match Engine Weight Allocation */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Sliders className="h-5 w-5 text-indigo-400" />
          <span>Explainable Match Score Weights</span>
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 text-xs">
          {Object.entries(weights).map(([k, v]) => (
            <div key={k} className="bg-slate-950 p-3 rounded-xl border border-slate-800">
              <div className="capitalize text-slate-400 font-medium mb-1">{k}</div>
              <div className="text-base font-extrabold text-indigo-400">{Math.round(v * 100)}%</div>
            </div>
          ))}
        </div>
      </div>

      {/* System Logs */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Terminal className="h-5 w-5 text-indigo-400" />
          <span>System Execution Logs</span>
        </h2>
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-xs text-slate-300 max-h-48 overflow-y-auto space-y-1">
          {logs.map((l, i) => (
            <div key={i} className="flex gap-2">
              <span className="text-slate-500">[{new Date(l.created_at).toLocaleTimeString()}]</span>
              <span className="text-amber-400 font-bold">[{l.level}]</span>
              <span>{l.message}</span>
            </div>
          ))}
          {!logs.length && <div className="text-slate-500 italic">No error logs recorded. All systems operating normally.</div>}
        </div>
      </div>
    </div>
  );
}

