import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import {
  FileText,
  Upload,
  CheckCircle2,
  Trash2,
  Sparkles,
  AlertCircle,
  FileCheck,
  Briefcase,
  UserCheck,
  Loader2,
  Check,
} from "lucide-react";

type ResumeAnalysis = {
  professional_summary?: string;
  seniority_level?: string;
  skills?: string[];
  tools?: string[];
  programming_languages?: string[];
  potential_job_titles?: string[];
};

type Resume = {
  id: number;
  filename: string;
  has_analysis: boolean;
  is_active: boolean;
  created_at: string;
  analysis?: ResumeAnalysis | null;
  extracted_text?: string | null;
};

export default function ResumePage() {
  const navigate = useNavigate();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [activeResume, setActiveResume] = useState<Resume | null>(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [activating, setActivating] = useState<number | null>(null);
  const [searching, setSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [dragActive, setDragActive] = useState(false);

  const loadResumes = async () => {
    try {
      const data = await api<Resume[]>("/resume");
      setResumes(data);
      const active = data.find((r) => r.is_active) || data[0] || null;
      setActiveResume(active);
      if (active?.analysis?.potential_job_titles?.length) {
        setSearchQuery(active.analysis.potential_job_titles[0]);
      }
    } catch {
      // Ignore
    }
  };

  useEffect(() => {
    loadResumes();
  }, []);

  const onUpload = async (file: File) => {
    if (file.size > 10 * 1024 * 1024) {
      setError("File exceeds maximum allowed size of 10MB");
      return;
    }

    setUploading(true);
    setError("");
    setSuccessMsg("");
    const fd = new FormData();
    fd.append("file", file);
    try {
      const uploaded = await api<Resume>("/resume/upload", { method: "POST", body: fd });
      await loadResumes();
      setActiveResume(uploaded);
      setSuccessMsg(`"${uploaded.filename}" uploaded and set as your active CV! Job matches tailored strictly to this CV.`);
      setTimeout(() => setSuccessMsg(""), 5000);
      if (uploaded.analysis?.potential_job_titles?.length) {
        setSearchQuery(uploaded.analysis.potential_job_titles[0]);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleActivate = async (resumeId: number, filename: string) => {
    setActivating(resumeId);
    setError("");
    setSuccessMsg("");
    try {
      const activated = await api<Resume>(`/resume/${resumeId}/activate`, { method: "POST" });
      await loadResumes();
      setActiveResume(activated);
      setSuccessMsg(`"${filename}" is now active! All job recommendations & matches are now tailored exclusively to this CV.`);
      setTimeout(() => setSuccessMsg(""), 5000);
      if (activated.analysis?.potential_job_titles?.length) {
        setSearchQuery(activated.analysis.potential_job_titles[0]);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "CV activation failed");
    } finally {
      setActivating(null);
    }
  };

  const handleAnalyze = async (resumeId: number) => {
    setAnalyzing(true);
    setError("");
    try {
      const updated = await api<Resume>(`/resume/${resumeId}/analyze`, { method: "POST" });
      setActiveResume(updated);
      setResumes((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
      if (updated.analysis?.potential_job_titles?.length) {
        setSearchQuery(updated.analysis.potential_job_titles[0]);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDelete = async () => {
    if (confirm("Are you sure you want to delete your stored CV history?")) {
      await api("/resume", { method: "DELETE" });
      setActiveResume(null);
      loadResumes();
    }
  };

  const runPersonalJobSearch = async () => {
    setSearching(true);
    try {
      await api("/jobs/search", {
        method: "POST",
        body: JSON.stringify({ query: searchQuery || undefined }),
      });
      navigate("/jobs");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Search failed");
    } finally {
      setSearching(false);
    }
  };

  const analysis = activeResume?.analysis;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <FileText className="h-6 w-6 text-indigo-400" />
          <span>Upload & Target CV Management</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Upload CVs, choose your active target CV, and ensure job recommendations are tailored strictly for that specific CV.
        </p>
      </div>

      {/* Upload Dropzone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragActive(false);
          if (e.dataTransfer.files?.[0]) onUpload(e.dataTransfer.files[0]);
        }}
        className={`border-2 border-dashed rounded-2xl p-8 md:p-10 text-center transition-all bg-slate-900/60 backdrop-blur-sm ${
          dragActive
            ? "border-indigo-500 bg-indigo-500/10"
            : "border-slate-800 hover:border-indigo-500/50"
        }`}
      >
        <div className="h-14 w-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mx-auto mb-4">
          <Upload className={`h-7 w-7 ${uploading ? "animate-bounce" : ""}`} />
        </div>

        <h3 className="text-lg font-bold text-white mb-1">
          {uploading ? "Uploading CV & Preparing AI..." : "Drop your CV file here"}
        </h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto mb-6">
          Supported formats: <span className="text-slate-200 font-semibold">PDF, DOCX, TXT</span> (Max file size: 10MB)
        </p>

        <label className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm rounded-xl transition-all shadow-lg shadow-indigo-600/30 cursor-pointer">
          <Sparkles className="h-4 w-4" />
          <span>{uploading ? "Uploading CV..." : "Select File & Upload"}</span>
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            className="hidden"
            disabled={uploading}
            onChange={(e) => e.target.files?.[0] && onUpload(e.target.files[0])}
          />
        </label>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-semibold flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Uploaded Resumes Selector */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <FileCheck className="h-4 w-4 text-indigo-400" />
            <span>Uploaded CVs & Target CV Selection</span>
          </h2>
          {resumes.length > 0 && (
            <button
              onClick={handleDelete}
              className="inline-flex items-center gap-1 text-xs text-rose-400 hover:text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 px-3 py-1.5 rounded-lg border border-rose-500/20 transition-all"
            >
              <Trash2 className="h-3 w-3" />
              <span>Delete History</span>
            </button>
          )}
        </div>

        <div className="space-y-3">
          {resumes.map((r) => (
            <div
              key={r.id}
              onClick={() => setActiveResume(r)}
              className={`cursor-pointer bg-slate-950 border rounded-xl p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-3 transition-all ${
                r.is_active
                  ? "border-emerald-500/80 ring-1 ring-emerald-500/40 bg-emerald-950/10"
                  : activeResume?.id === r.id
                  ? "border-indigo-500/80"
                  : "border-slate-800 hover:border-slate-700"
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${r.is_active ? "bg-emerald-500/20 text-emerald-400" : "bg-indigo-500/10 text-indigo-400"}`}>
                  <FileText className="h-5 w-5" />
                </div>
                <div>
                  <div className="font-semibold text-sm text-white flex items-center gap-2">
                    <span>{r.filename}</span>
                    {r.is_active ? (
                      <span className="text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 px-2.5 py-0.5 rounded-full uppercase font-extrabold flex items-center gap-1">
                        <Check className="h-3 w-3 text-emerald-400" />
                        <span>Active Target CV</span>
                      </span>
                    ) : (
                      <span className="text-[10px] bg-slate-800 text-slate-400 border border-slate-700 px-2 py-0.2 rounded-full uppercase font-medium">
                        Inactive
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-slate-500">
                    Uploaded {new Date(r.created_at).toLocaleString()}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                {!r.is_active && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleActivate(r.id, r.filename);
                    }}
                    disabled={activating === r.id}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-300 bg-emerald-500/15 hover:bg-emerald-500/25 px-3 py-1.5 rounded-xl border border-emerald-500/40 transition-all disabled:opacity-50"
                  >
                    {activating === r.id ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                    )}
                    <span>{activating === r.id ? "Tailoring Search..." : "Set as Active CV"}</span>
                  </button>
                )}

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleAnalyze(r.id);
                  }}
                  disabled={analyzing}
                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-300 bg-indigo-500/10 hover:bg-indigo-500/20 px-3 py-1.5 rounded-xl border border-indigo-500/30 transition-all disabled:opacity-50"
                >
                  {analyzing ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
                  )}
                  <span>{analyzing ? "Analyzing..." : "Re-Analyze"}</span>
                </button>
              </div>
            </div>
          ))}

          {!resumes.length && (
            <p className="text-xs text-slate-500 text-center py-6">
              No CV uploaded yet. Upload your CV above to get started.
            </p>
          )}
        </div>
      </div>

      {/* AI Extraction Display Card */}
      {activeResume && (
        <div className="bg-slate-900/70 border border-indigo-500/30 rounded-2xl p-6 backdrop-blur-sm space-y-6 shadow-xl shadow-indigo-950/40">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
            <div>
              <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20 mb-1">
                <CheckCircle2 className="h-3.5 w-3.5" />
                <span>Active Target CV: {activeResume.filename}</span>
              </div>
              <h2 className="text-lg font-bold text-white tracking-tight">
                Candidate AI Profile (Active CV)
              </h2>
            </div>

            <button
              onClick={runPersonalJobSearch}
              disabled={searching}
              className="inline-flex items-center gap-1.5 text-xs font-bold px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/30 transition-all shrink-0 disabled:opacity-50"
            >
              {searching ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Sparkles className="h-3.5 w-3.5" />}
              <span>{searching ? "Searching Tailored Jobs..." : "Search Jobs for This CV"}</span>
            </button>
          </div>

          {analysis ? (
            <div className="space-y-5">
              {/* Seniority & Overview */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2 bg-slate-950/80 border border-slate-800 rounded-xl p-4">
                  <div className="text-xs font-semibold text-slate-400 mb-1 flex items-center gap-1.5">
                    <UserCheck className="h-3.5 w-3.5 text-indigo-400" />
                    <span>Professional Summary</span>
                  </div>
                  <p className="text-xs text-slate-200 leading-relaxed">
                    {analysis.professional_summary || "No summary provided in CV."}
                  </p>
                </div>

                <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 flex flex-col justify-center">
                  <div className="text-xs font-semibold text-slate-400 mb-1 flex items-center gap-1.5">
                    <Briefcase className="h-3.5 w-3.5 text-indigo-400" />
                    <span>Seniority Level</span>
                  </div>
                  <div className="text-lg font-bold text-indigo-300">
                    {analysis.seniority_level || "Mid Level"}
                  </div>
                </div>
              </div>

              {/* Skills Chips */}
              <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 space-y-2">
                <div className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
                  <Briefcase className="h-3.5 w-3.5 text-indigo-400" />
                  <span>Detected Technical Skills & Tools</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {(analysis.skills || []).concat(analysis.tools || []).map((skill) => (
                    <span
                      key={skill}
                      className="text-xs bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 px-2.5 py-1 rounded-lg"
                    >
                      {skill}
                    </span>
                  ))}
                  {!analysis.skills?.length && !analysis.tools?.length && (
                    <span className="text-xs text-slate-500 italic">No skills detected</span>
                  )}
                </div>
              </div>

              {/* Potential Job Titles */}
              {analysis.potential_job_titles && analysis.potential_job_titles.length > 0 && (
                <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 space-y-2">
                  <div className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
                    <Briefcase className="h-3.5 w-3.5 text-indigo-400" />
                    <span>Recommended Target Roles</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {analysis.potential_job_titles.map((title) => (
                      <span
                        key={title}
                        className="text-xs bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 px-3 py-1 rounded-xl font-medium"
                      >
                        {title}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-6">
              <p className="text-xs text-slate-400 mb-3">
                No AI analysis generated for this CV yet.
              </p>
              <button
                onClick={() => handleAnalyze(activeResume.id)}
                disabled={analyzing}
                className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-50"
              >
                <Sparkles className="h-4 w-4" />
                <span>Run AI CV Analysis</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
