import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import {
  Search,
  Filter,
  Zap,
  Bookmark,
  EyeOff,
  CheckCircle2,
  ExternalLink,
  MapPin,
  Building2,
  Check,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Sparkles,
  FileText,
  ChevronRight,
} from "lucide-react";

type Match = {
  id: number;
  overall_score: number;
  component_scores: Record<string, number>;
  match_reasons: string[];
  gap_reasons: string[];
  status: string;
  resume_id: number | null;
  resume_filename: string | null;
  job: {
    id: number;
    title: string;
    company: string;
    location: string | null;
    remote: boolean;
    employment_type: string | null;
    salary_min: number | null;
    salary_max: number | null;
    currency: string | null;
    source: string;
    source_url: string;
    skills: string[];
  };
};

type ResumeGroup = {
  resume_id: number | null;
  resume_filename: string;
  is_active: boolean;
  matches: Match[];
  match_count: number;
};

export default function JobsPage() {
  const [resumeGroups, setResumeGroups] = useState<ResumeGroup[]>([]);
  const [flatMatches, setFlatMatches] = useState<Match[]>([]);
  const [viewMode, setViewMode] = useState<"by-resume" | "all">("by-resume");
  const [minMatch, setMinMatch] = useState("");
  const [employmentType, setEmploymentType] = useState("");
  const [locationFilter, setLocationFilter] = useState("");
  const [searching, setSearching] = useState(false);
  const [query, setQuery] = useState("");
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [collapsedResumes, setCollapsedResumes] = useState<Set<string>>(new Set());
  const [searchResult, setSearchResult] = useState<string | null>(null);

  const loadByResume = () => {
    api<ResumeGroup[]>("/matches/by-resume")
      .then(setResumeGroups)
      .catch(() => {});
  };

  const loadFlat = () => {
    const params = new URLSearchParams();
    if (minMatch) params.set("min_match", minMatch);
    if (employmentType) params.set("employment_type", employmentType);
    if (locationFilter) params.set("location", locationFilter);
    api<Match[]>(`/matches?${params}`)
      .then(setFlatMatches)
      .catch(() => {});
  };

  useEffect(() => {
    loadByResume();
    loadFlat();
  }, []);

  useEffect(() => {
    loadFlat();
  }, [minMatch, employmentType, locationFilter]);

  const runSearch = async () => {
    setSearching(true);
    setSearchResult(null);
    try {
      const result = await api<{ jobs_collected: number; message: string; resumes_matched: number }>(
        "/jobs/search",
        { method: "POST", body: JSON.stringify({ query: query || undefined }) }
      );
      setSearchResult(
        `✅ Discovered ${result.jobs_collected} new jobs — matched against ${result.resumes_matched} CV(s)`
      );
      loadByResume();
      loadFlat();
    } catch (e: any) {
      setSearchResult(`❌ Search failed: ${e.message}`);
    } finally {
      setSearching(false);
    }
  };

  const handleAction = async (jobId: number, action: "save" | "ignore" | "applied") => {
    await api(`/jobs/${jobId}/${action}`, { method: "POST" });
    loadByResume();
    loadFlat();
  };

  const toggleResumeCollapse = (filename: string) => {
    setCollapsedResumes((prev) => {
      const next = new Set(prev);
      if (next.has(filename)) next.delete(filename);
      else next.add(filename);
      return next;
    });
  };

  const renderMatch = (m: Match) => {
    const score = Math.round(m.overall_score);
    let scoreBadgeColor = "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
    if (score < 80) scoreBadgeColor = "text-indigo-400 bg-indigo-500/10 border-indigo-500/30";
    if (score < 70) scoreBadgeColor = "text-amber-400 bg-amber-500/10 border-amber-500/30";

    const isExpanded = expandedId === m.id;

    return (
      <article
        key={m.id}
        className="bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 md:p-6 transition-colors shadow-md"
      >
        <div className="flex flex-col md:flex-row justify-between items-start gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2.5 mb-1.5 flex-wrap">
              <Link
                to={`/jobs/${m.job.id}`}
                className="text-xl font-bold text-white hover:text-indigo-400 transition-colors"
              >
                {m.job.title}
              </Link>
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                {m.job.source}
              </span>
              {m.status && m.status !== "new" && (
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase tracking-wider">
                  {m.status}
                </span>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400 mb-3">
              <span className="flex items-center gap-1 font-medium text-slate-300">
                <Building2 className="h-3.5 w-3.5 text-slate-400" />
                {m.job.company}
              </span>
              <span className="flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5 text-slate-400" />
                {m.job.remote ? "Remote" : m.job.location || "On-site"}
              </span>
              {m.job.employment_type && (
                <span className="capitalize text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded">
                  {m.job.employment_type}
                </span>
              )}
            </div>

            {/* Skill Chips */}
            {m.job.skills && m.job.skills.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-4">
                {m.job.skills.slice(0, 8).map((s) => (
                  <span
                    key={s}
                    className="text-xs bg-slate-800/80 text-slate-300 border border-slate-700/60 px-2.5 py-0.5 rounded-lg"
                  >
                    {s}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Match Score Badge */}
          <div className="shrink-0 flex items-center gap-3">
            <div className={`px-4 py-2 rounded-2xl border font-extrabold text-2xl ${scoreBadgeColor}`}>
              {score}%
            </div>
          </div>
        </div>

        {/* Highlights & Gaps Section */}
        <div className="grid md:grid-cols-2 gap-3 mt-2 text-xs">
          {/* Positives */}
          <div className="bg-emerald-500/5 border border-emerald-500/15 rounded-xl p-3 space-y-1">
            <div className="font-semibold text-emerald-400 flex items-center gap-1.5 mb-1.5">
              <Check className="h-3.5 w-3.5" />
              <span>Why This Job Matches</span>
            </div>
            {(m.match_reasons || []).slice(0, 3).map((r, i) => (
              <div key={i} className="text-slate-300 flex items-start gap-1.5">
                <span className="text-emerald-400 font-bold">•</span>
                <span>{r}</span>
              </div>
            ))}
          </div>

          {/* Gaps */}
          <div className="bg-amber-500/5 border border-amber-500/15 rounded-xl p-3 space-y-1">
            <div className="font-semibold text-amber-400 flex items-center gap-1.5 mb-1.5">
              <AlertTriangle className="h-3.5 w-3.5" />
              <span>Potential Gaps</span>
            </div>
            {(m.gap_reasons || []).length > 0 ? (
              (m.gap_reasons || []).slice(0, 3).map((g, i) => (
                <div key={i} className="text-slate-300 flex items-start gap-1.5">
                  <span className="text-amber-400 font-bold">•</span>
                  <span>{g}</span>
                </div>
              ))
            ) : (
              <div className="text-slate-400 italic">No major qualification gaps identified</div>
            )}
          </div>
        </div>

        {/* Component Score Breakdown Accordion */}
        {isExpanded && m.component_scores && (
          <div className="mt-4 pt-4 border-t border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
            {Object.entries(m.component_scores).map(([k, v]) => (
              <div key={k} className="space-y-1">
                <div className="flex justify-between text-xs capitalize text-slate-400">
                  <span>{k}</span>
                  <span className="font-semibold text-slate-200">{Math.round(v)}%</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1.5">
                  <div
                    className="bg-indigo-500 h-1.5 rounded-full"
                    style={{ width: `${Math.min(100, v)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Action Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 mt-4 pt-3 border-t border-slate-800/60 text-xs">
          <button
            onClick={() => setExpandedId(isExpanded ? null : m.id)}
            className="flex items-center gap-1 text-slate-400 hover:text-slate-200"
          >
            {isExpanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
            <span>{isExpanded ? "Hide Breakdown" : "View Score Breakdown"}</span>
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={() => handleAction(m.job.id, "save")}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-700 hover:border-amber-500/50 text-slate-300 hover:text-amber-300 bg-slate-900 transition-all"
            >
              <Bookmark className="h-3.5 w-3.5" />
              <span>Save</span>
            </button>
            <button
              onClick={() => handleAction(m.job.id, "applied")}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-700 hover:border-emerald-500/50 text-slate-300 hover:text-emerald-300 bg-slate-900 transition-all"
            >
              <CheckCircle2 className="h-3.5 w-3.5" />
              <span>Mark Applied</span>
            </button>
            <button
              onClick={() => handleAction(m.job.id, "ignore")}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-700 hover:border-slate-600 text-slate-400 hover:text-slate-300 bg-slate-900 transition-all"
            >
              <EyeOff className="h-3.5 w-3.5" />
              <span>Ignore</span>
            </button>
            <a
              href={m.job.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium transition-all"
            >
              <span>Original Post</span>
              <ExternalLink className="h-3.5 w-3.5" />
            </a>
          </div>
        </div>
      </article>
    );
  };

  const totalMatches = viewMode === "by-resume"
    ? resumeGroups.reduce((sum, g) => sum + g.match_count, 0)
    : flatMatches.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-indigo-400" />
            <span>Discovered Job Opportunities</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            AI-analyzed jobs matched against each of your uploaded CVs. Found{" "}
            <span className="text-white font-semibold">{totalMatches}</span> matches.
          </p>
        </div>

        <button
          onClick={runSearch}
          disabled={searching}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl transition-all shadow-lg shadow-indigo-600/30 disabled:opacity-50 shrink-0"
        >
          <Zap className={`h-4 w-4 ${searching ? "animate-spin" : ""}`} />
          <span>{searching ? "Discovering Jobs..." : "Run Job Discovery"}</span>
        </button>
      </div>

      {/* Search Result Feedback */}
      {searchResult && (
        <div
          className={`px-4 py-3 rounded-xl text-sm font-medium border ${
            searchResult.startsWith("✅")
              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
              : "bg-red-500/10 border-red-500/30 text-red-300"
          }`}
        >
          {searchResult}
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 backdrop-blur-md space-y-3">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
            <Filter className="h-3.5 w-3.5 text-indigo-400" />
            <span>Filter & View</span>
          </div>
          {/* View Toggle */}
          <div className="flex items-center gap-1 bg-slate-950 rounded-lg border border-slate-700/80 p-0.5">
            <button
              onClick={() => setViewMode("by-resume")}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                viewMode === "by-resume"
                  ? "bg-indigo-600 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <FileText className="h-3 w-3 inline mr-1" />
              By CV
            </button>
            <button
              onClick={() => setViewMode("all")}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                viewMode === "all"
                  ? "bg-indigo-600 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              All Jobs
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            <input
              placeholder="Search keyword (e.g. Python, Remote)..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && runSearch()}
              className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>

          <select
            value={minMatch}
            onChange={(e) => setMinMatch(e.target.value)}
            className="w-full px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="90">90% – 100% (Highest Compatibility)</option>
            <option value="80">80%+ Match</option>
            <option value="70">70%+ Match</option>
            <option value="">All Matches</option>
          </select>

          <select
            value={employmentType}
            onChange={(e) => setEmploymentType(e.target.value)}
            className="w-full px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Employment Types</option>
            <option value="full-time">Full-time</option>
            <option value="contract">Contract</option>
            <option value="internship">Internship</option>
            <option value="freelance">Freelance</option>
            <option value="part-time">Part-time</option>
          </select>

          <select
            value={locationFilter}
            onChange={(e) => setLocationFilter(e.target.value)}
            className="w-full px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Locations</option>
            <option value="remote">Remote Only</option>
            <option value="kenya">Kenya</option>
            <option value="worldwide">Worldwide</option>
          </select>
        </div>
      </div>

      {/* ===== BY-RESUME VIEW ===== */}
      {viewMode === "by-resume" && (
        <div className="space-y-6">
          {resumeGroups.length > 0 ? (
            resumeGroups.map((group) => {
              const isCollapsed = collapsedResumes.has(group.resume_filename);
              return (
                <div
                  key={group.resume_filename}
                  className="border border-slate-800 rounded-2xl overflow-hidden bg-slate-950/50"
                >
                  {/* Resume Group Header */}
                  <button
                    onClick={() => toggleResumeCollapse(group.resume_filename)}
                    className="w-full flex items-center justify-between p-4 md:p-5 bg-gradient-to-r from-slate-900/90 to-slate-900/60 hover:from-slate-800/90 hover:to-slate-800/60 transition-all"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 rounded-xl bg-indigo-500/15 border border-indigo-500/30">
                        <FileText className="h-5 w-5 text-indigo-400" />
                      </div>
                      <div className="text-left">
                        <h2 className="text-lg font-bold text-white flex items-center gap-2">
                          {group.resume_filename}
                          {group.is_active && (
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase tracking-wider">
                              Active CV
                            </span>
                          )}
                        </h2>
                        <p className="text-sm text-slate-400">
                          {group.match_count} job{group.match_count !== 1 ? "s" : ""} matched for this CV
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-2xl font-extrabold text-indigo-400">
                        {group.match_count}
                      </span>
                      <ChevronRight
                        className={`h-5 w-5 text-slate-500 transition-transform ${
                          isCollapsed ? "" : "rotate-90"
                        }`}
                      />
                    </div>
                  </button>

                  {/* Matches List */}
                  {!isCollapsed && (
                    <div className="p-4 md:p-5 space-y-4 border-t border-slate-800/60">
                      {group.matches.map((m) => renderMatch(m))}
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            <div className="text-center py-12 px-4 rounded-2xl bg-slate-900/40 border border-slate-800">
              <FileText className="h-10 w-10 text-slate-500 mx-auto mb-3" />
              <h3 className="text-lg font-bold text-white mb-1">No CV-Based Matches Yet</h3>
              <p className="text-slate-400 text-sm max-w-md mx-auto mb-4">
                Upload a CV in the Resume section, then run Job Discovery to find tailored opportunities
                for each of your uploaded CVs.
              </p>
              <div className="flex items-center justify-center gap-3">
                <Link
                  to="/resume"
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white font-medium text-sm rounded-xl transition-all border border-slate-700"
                >
                  Upload CV
                </Link>
                <button
                  onClick={runSearch}
                  disabled={searching}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl transition-all"
                >
                  Run Job Discovery
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ===== FLAT VIEW ===== */}
      {viewMode === "all" && (
        <div className="space-y-4">
          {flatMatches.map((m) => renderMatch(m))}

          {!flatMatches.length && (
            <div className="text-center py-12 px-4 rounded-2xl bg-slate-900/40 border border-slate-800">
              <Search className="h-10 w-10 text-slate-500 mx-auto mb-3" />
              <h3 className="text-lg font-bold text-white mb-1">No Matches Found</h3>
              <p className="text-slate-400 text-sm max-w-md mx-auto mb-4">
                Try adjusting your search criteria or trigger a new automated search to collect fresh
                opportunities.
              </p>
              <button
                onClick={runSearch}
                disabled={searching}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl transition-all"
              >
                Run Job Discovery Now
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
