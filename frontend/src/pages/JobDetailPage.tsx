import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../lib/api";
import {
  ExternalLink,
  Sparkles,
  Building2,
  MapPin,
  HelpCircle,
  AlertCircle,
  Copy,
  Check,
  CheckCircle2,
  AlertTriangle,
  ArrowLeft,
  Briefcase,
} from "lucide-react";

type JobDetail = {
  id: number;
  title: string;
  company: string;
  description: string;
  location: string | null;
  remote: boolean;
  employment_type: string | null;
  salary_min: number | null;
  salary_max: number | null;
  currency: string | null;
  experience_required: string | null;
  education_required: string | null;
  source: string;
  source_url: string;
  posted_at: string | null;
  skills: string[];
  analysis: Record<string, unknown> | null;
};

type MatchDetail = {
  id: number;
  overall_score: number;
  component_scores: Record<string, number>;
  match_reasons: string[];
  gap_reasons: string[];
  job: {
    id: number;
  };
};

export default function JobDetailPage() {
  const { id } = useParams();
  const [job, setJob] = useState<JobDetail | null>(null);
  const [match, setMatch] = useState<MatchDetail | null>(null);
  const [coverLetter, setCoverLetter] = useState("");
  const [loadingLetter, setLoadingLetter] = useState(false);
  const [questionsInput, setQuestionsInput] = useState("");
  const [answers, setAnswers] = useState<{ question: string; suggested_answer: string }[]>([]);
  const [loadingAnswers, setLoadingAnswers] = useState(false);
  const [copied, setCopied] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<"ask_ai" | "cover_letter" | "answers" | "resume_tips">("ask_ai");

  const [customQuestion, setCustomQuestion] = useState("");
  const [loadingQuestion, setLoadingQuestion] = useState(false);
  const [qaHistory, setQaHistory] = useState<{ question: string; answer: string }[]>([]);

  useEffect(() => {
    if (id) {
      api<JobDetail>(`/jobs/${id}`).then(setJob).catch(() => {});
      api<MatchDetail[]>(`/matches`).then((matches) => {
        const found = matches.find((m) => m.job?.id === Number(id));
        if (found) setMatch(found);
      }).catch(() => {});
    }
  }, [id]);

  const handleAskQuestion = async (qToAsk?: string) => {
    const questionText = (qToAsk || customQuestion).trim();
    if (!id || !questionText || loadingQuestion) return;
    setLoadingQuestion(true);
    try {
      const res = await api<{ question: string; answer: string }>("/application-assistant/ask", {
        method: "POST",
        body: JSON.stringify({ job_id: Number(id), question: questionText }),
      });
      setQaHistory((prev) => [{ question: res.question, answer: res.answer }, ...prev]);
      setCustomQuestion("");
    } finally {
      setLoadingQuestion(false);
    }
  };

  const generateCoverLetter = async () => {
    if (!id) return;
    setLoadingLetter(true);
    try {
      const res = await api<{ cover_letter: string }>("/application-assistant/cover-letter", {
        method: "POST",
        body: JSON.stringify({ job_id: Number(id) }),
      });
      setCoverLetter(res.cover_letter);
    } finally {
      setLoadingLetter(false);
    }
  };

  const generateAnswers = async () => {
    if (!id || !questionsInput.trim()) return;
    setLoadingAnswers(true);
    const questions = questionsInput
      .split("\n")
      .map((q) => q.trim())
      .filter((q) => q.length > 0);

    try {
      const res = await api<{ answers: { question: string; suggested_answer: string }[] }>(
        "/application-assistant/answers",
        {
          method: "POST",
          body: JSON.stringify({ job_id: Number(id), questions }),
        }
      );
      setAnswers(res.answers || []);
    } finally {
      setLoadingAnswers(false);
    }
  };

  const copyToClipboard = (text: string, index?: number) => {
    navigator.clipboard.writeText(text);
    if (index !== undefined) {
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } else {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (!job) {
    return (
      <div className="py-12 text-center text-slate-400">
        <Sparkles className="h-8 w-8 text-indigo-400 animate-spin mx-auto mb-2" />
        <p>Loading job analysis details...</p>
      </div>
    );
  }

  const overallScore = match ? Math.round(match.overall_score) : 75;

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Back Button */}
      <Link
        to="/jobs"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        <span>Back to Discovered Jobs</span>
      </Link>

      {/* Main Job Overview Card */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 md:p-8 backdrop-blur-xl space-y-6">
        <div className="flex flex-col md:flex-row justify-between items-start gap-4">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                Source: {job.source}
              </span>
              {job.remote && (
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Remote Position
                </span>
              )}
            </div>

            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              {job.title}
            </h1>

            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-slate-400">
              <span className="flex items-center gap-1.5 text-slate-200 font-semibold">
                <Building2 className="h-4 w-4 text-indigo-400" />
                {job.company}
              </span>
              <span className="flex items-center gap-1.5">
                <MapPin className="h-4 w-4 text-slate-500" />
                {job.remote ? "Remote" : job.location || "On-site"}
              </span>
            </div>
          </div>

          <div className="flex flex-col items-end gap-3 w-full md:w-auto border-t md:border-t-0 pt-4 md:pt-0 border-slate-800">
            <div className="flex items-center gap-2 bg-slate-950 px-4 py-2 rounded-2xl border border-indigo-500/30">
              <Sparkles className="h-5 w-5 text-indigo-400" />
              <div>
                <div className="text-2xl font-extrabold text-emerald-400 leading-none">
                  {overallScore}%
                </div>
                <div className="text-[10px] text-slate-400 uppercase font-semibold">Compatibility</div>
              </div>
            </div>

            <a
              href={job.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full md:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm rounded-xl transition-all shadow-lg shadow-indigo-600/30"
            >
              <span>Open Original Application Page</span>
              <ExternalLink className="h-4 w-4" />
            </a>
          </div>
        </div>

        {/* Explainable Match Score Component Breakdown */}
        {match && match.component_scores && (
          <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4 md:p-5 space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Explainable Compatibility Breakdown
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
              {Object.entries(match.component_scores).map(([k, v]) => (
                <div key={k} className="bg-slate-900 p-2.5 rounded-lg border border-slate-800/60">
                  <div className="text-[11px] text-slate-400 capitalize truncate">{k}</div>
                  <div className="text-lg font-bold text-slate-100">{Math.round(v)}%</div>
                  <div className="w-full bg-slate-800 rounded-full h-1 mt-1">
                    <div
                      className="bg-indigo-500 h-1 rounded-full"
                      style={{ width: `${Math.min(100, v)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Match Highlights & Missing Gaps Grid */}
        {match && (
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-4 space-y-2">
              <h3 className="text-sm font-bold text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4" />
                <span>Why This Job Matches Your CV</span>
              </h3>
              <ul className="text-xs text-slate-300 space-y-1.5">
                {match.match_reasons.map((r, i) => (
                  <li key={i} className="flex items-start gap-1.5">
                    <span className="text-emerald-400 font-bold">•</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-amber-500/5 border border-amber-500/20 rounded-xl p-4 space-y-2">
              <h3 className="text-sm font-bold text-amber-400 flex items-center gap-1.5">
                <AlertTriangle className="h-4 w-4" />
                <span>Potential Qualification Gaps</span>
              </h3>
              <ul className="text-xs text-slate-300 space-y-1.5">
                {match.gap_reasons.length > 0 ? (
                  match.gap_reasons.map((g, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-amber-400 font-bold">•</span>
                      <span>{g}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-slate-400 italic">No major qualification gaps identified</li>
                )}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Description Section */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Briefcase className="h-5 w-5 text-indigo-400" />
          <span>Original Job Description</span>
        </h2>
        <div className="prose prose-invert max-w-none text-sm text-slate-300 leading-relaxed whitespace-pre-wrap bg-slate-950/60 border border-slate-800/80 rounded-xl p-5 max-h-96 overflow-y-auto">
          {job.description}
        </div>
      </div>

      {/* Application Assistant Box */}
      <div className="bg-slate-900/80 border border-indigo-500/30 rounded-2xl p-6 backdrop-blur-xl space-y-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-indigo-400" />
              <span>AI Application Assistant</span>
            </h2>
            <p className="text-xs text-slate-400">
              Generate customized materials tailored specifically to your CV and this job requirement.
            </p>
          </div>

          {/* Navigation Tabs */}
          <div className="flex flex-wrap items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
            <button
              onClick={() => setActiveTab("ask_ai")}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                activeTab === "ask_ai" ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30" : "text-slate-400 hover:text-white"
              }`}
            >
              Ask AI Assistant
            </button>
            <button
              onClick={() => setActiveTab("cover_letter")}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                activeTab === "cover_letter" ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30" : "text-slate-400 hover:text-white"
              }`}
            >
              Cover Letter
            </button>
            <button
              onClick={() => setActiveTab("answers")}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                activeTab === "answers" ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30" : "text-slate-400 hover:text-white"
              }`}
            >
              Application Form Q&A
            </button>
            <button
              onClick={() => setActiveTab("resume_tips")}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                activeTab === "resume_tips" ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30" : "text-slate-400 hover:text-white"
              }`}
            >
              CV Emphasis
            </button>
          </div>
        </div>

        {/* Tab 0: Ask AI Assistant (Groq Powered) */}
        {activeTab === "ask_ai" && (
          <div className="space-y-5">
            <div className="bg-slate-950/80 border border-slate-800 p-4 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-semibold text-indigo-300">
                  <Sparkles className="h-4 w-4 text-indigo-400" />
                  <span>Ask Groq AI about this position</span>
                </div>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Groq LLM Connected
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Ask any question about <strong>{job.title}</strong> at <strong>{job.company}</strong>. The AI assistant answers based on the job requirements and your uploaded CV.
              </p>

              {/* Preset Chips */}
              <div className="flex flex-wrap gap-2 pt-1">
                {[
                  "Why am I a fit for this role?",
                  "What core technical & soft skills should I highlight?",
                  "What interview questions are likely for this role?",
                  "What qualification gaps should I prepare for?",
                  "Draft answer for: Why do you want to join our company?",
                ].map((chip) => (
                  <button
                    key={chip}
                    onClick={() => handleAskQuestion(chip)}
                    disabled={loadingQuestion}
                    className="text-xs bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-indigo-300 px-3 py-1.5 rounded-lg border border-slate-700/80 transition-all text-left disabled:opacity-50"
                  >
                    💡 {chip}
                  </button>
                ))}
              </div>

              {/* Input Area */}
              <div className="flex gap-2 pt-2">
                <input
                  type="text"
                  placeholder="Type any custom question about this job..."
                  value={customQuestion}
                  onChange={(e) => setCustomQuestion(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleAskQuestion()}
                  className="flex-1 bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                />
                <button
                  onClick={() => handleAskQuestion()}
                  disabled={loadingQuestion || !customQuestion.trim()}
                  className="inline-flex items-center gap-1.5 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl transition-all disabled:opacity-50 shadow-md shadow-indigo-600/30"
                >
                  <Sparkles className={`h-3.5 w-3.5 ${loadingQuestion ? "animate-spin" : ""}`} />
                  <span>{loadingQuestion ? "Asking Groq..." : "Ask AI"}</span>
                </button>
              </div>
            </div>

            {/* Q&A History */}
            {qaHistory.length > 0 && (
              <div className="space-y-4 pt-2">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  AI Responses for {job.title}
                </h4>
                {qaHistory.map((item, idx) => (
                  <div key={idx} className="bg-slate-950 border border-indigo-500/20 rounded-xl p-4 md:p-5 space-y-3">
                    <div className="flex justify-between items-start gap-2 border-b border-slate-800/80 pb-2">
                      <div className="text-xs font-bold text-indigo-300 flex items-center gap-2">
                        <HelpCircle className="h-4 w-4 text-indigo-400" />
                        <span>Q: {item.question}</span>
                      </div>
                      <button
                        onClick={() => copyToClipboard(item.answer, idx)}
                        className="inline-flex items-center gap-1 text-[11px] text-slate-400 hover:text-white bg-slate-900 px-2 py-1 rounded-lg border border-slate-800 shrink-0"
                      >
                        {copiedIndex === idx ? (
                          <Check className="h-3 w-3 text-emerald-400" />
                        ) : (
                          <Copy className="h-3 w-3" />
                        )}
                        <span>{copiedIndex === idx ? "Copied" : "Copy"}</span>
                      </button>
                    </div>
                    <div className="text-xs text-slate-300 leading-relaxed whitespace-pre-wrap font-sans bg-slate-900/60 p-4 rounded-lg border border-slate-800/80">
                      {item.answer}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab 1: Cover Letter */}
        {activeTab === "cover_letter" && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <p className="text-xs text-slate-300">
                Draft a cover letter using your CV experience and the employer's key requirements.
              </p>
              <button
                onClick={generateCoverLetter}
                disabled={loadingLetter}
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl transition-all disabled:opacity-50"
              >
                <Sparkles className={`h-3.5 w-3.5 ${loadingLetter ? "animate-spin" : ""}`} />
                <span>{loadingLetter ? "Drafting Cover Letter..." : "Generate Cover Letter"}</span>
              </button>
            </div>

            {coverLetter && (
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-semibold text-indigo-300">Editable Cover Letter Draft</span>
                  <button
                    onClick={() => copyToClipboard(coverLetter)}
                    className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-white bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-700"
                  >
                    {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                    <span>{copied ? "Copied" : "Copy Draft"}</span>
                  </button>
                </div>
                <textarea
                  value={coverLetter}
                  onChange={(e) => setCoverLetter(e.target.value)}
                  className="w-full h-64 bg-slate-950 border border-slate-700/80 rounded-xl p-4 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 font-mono leading-relaxed"
                />
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Application Questions */}
        {activeTab === "answers" && (
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">
                Paste Application Questions (one per line)
              </label>
              <textarea
                placeholder="e.g. Why are you interested in this position? Describe a relevant Python project."
                value={questionsInput}
                onChange={(e) => setQuestionsInput(e.target.value)}
                className="w-full h-24 bg-slate-950 border border-slate-700/80 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
              <button
                onClick={generateAnswers}
                disabled={loadingAnswers || !questionsInput.trim()}
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl transition-all disabled:opacity-50"
              >
                <HelpCircle className={`h-3.5 w-3.5 ${loadingAnswers ? "animate-spin" : ""}`} />
                <span>{loadingAnswers ? "Generating Answers..." : "Generate Answers"}</span>
              </button>
            </div>

            {answers.length > 0 && (
              <div className="space-y-3 pt-2">
                {answers.map((item, idx) => (
                  <div key={idx} className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2">
                    <div className="text-xs font-bold text-indigo-300">Q: {item.question}</div>
                    <div className="text-xs text-slate-300 bg-slate-900 p-3 rounded-lg border border-slate-800 whitespace-pre-wrap">
                      {item.suggested_answer}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Resume Tips */}
        {activeTab === "resume_tips" && (
          <div className="space-y-3 text-xs text-slate-300">
            <p className="font-semibold text-indigo-300">CV Customization Recommendations:</p>
            <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2">
              <div className="flex items-center gap-2 text-emerald-400 font-semibold">
                <Check className="h-4 w-4" />
                <span>Emphasize Matching Skills:</span>
              </div>
              <p className="text-slate-400 pl-6">
                Move your experience with {job.skills?.slice(0, 4).join(", ") || "core technical skills"} to the top summary section of your CV.
              </p>
            </div>
            <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2">
              <div className="flex items-center gap-2 text-amber-400 font-semibold">
                <AlertTriangle className="h-4 w-4" />
                <span>Address Missing Skill Gaps:</span>
              </div>
              <p className="text-slate-400 pl-6">
                Highlight any related framework, project work, or certifications that demonstrate capacity in preferred skills.
              </p>
            </div>
          </div>
        )}

        {/* Essential Safety / User Action Disclaimer */}
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-3 flex items-start gap-2.5 text-xs text-amber-300/90">
          <AlertCircle className="h-4 w-4 shrink-0 text-amber-400 mt-0.5" />
          <span>
            <strong>User Control Reminder:</strong> All AI-generated cover letters and application answers must be reviewed and edited by you before submission. You retain complete control over every final application.
          </span>
        </div>
      </div>
    </div>
  );
}

