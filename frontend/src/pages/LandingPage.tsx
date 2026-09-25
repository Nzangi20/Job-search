import { Link } from "react-router-dom";
import {
  Sparkles,
  Search,
  FileCheck,
  Zap,
  Target,
  BellRing,
  ShieldCheck,
  ArrowRight,
  CheckCircle2,
  Lock,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased overflow-x-hidden selection:bg-indigo-500 selection:text-white">
      {/* Background Gradient Glows */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[400px] bg-indigo-600/15 blur-[120px] rounded-full pointer-events-none" />
      <div className="fixed top-96 left-1/4 w-[600px] h-[300px] bg-emerald-600/10 blur-[100px] rounded-full pointer-events-none" />

      {/* Header */}
      <header className="relative z-10 max-w-7xl mx-auto px-6 py-6 flex justify-between items-center border-b border-slate-800/60">
        <Link to="/" className="flex items-center gap-2.5 font-bold text-xl text-white">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-emerald-400 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <span className="bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent font-extrabold tracking-tight">
            AI Job Hunter
          </span>
        </Link>
        <div className="flex items-center gap-3">
          <Link
            to="/login"
            className="px-4 py-2 text-sm font-semibold text-slate-300 hover:text-white transition-colors"
          >
            Log in
          </Link>
          <Link
            to="/register"
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm rounded-xl transition-all shadow-lg shadow-indigo-600/30"
          >
            Get Started Free
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 max-w-5xl mx-auto px-6 pt-20 pb-24 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold mb-6 animate-pulse">
          <Sparkles className="h-4 w-4 text-indigo-400" />
          <span>Automated Job Discovery & Explainable Match Engine</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-[1.1] mb-6">
          Stop Searching for Jobs.
          <br />
          <span className="bg-gradient-to-r from-indigo-400 via-purple-300 to-emerald-400 bg-clip-text text-transparent">
            Let AI Find the Right Opportunities for You.
          </span>
        </h1>

        <p className="text-lg md:text-xl text-slate-400 max-w-3xl mx-auto mb-10 leading-relaxed">
          Upload your CV once. Define your preferences. AI Job Hunter continuously searches legitimate job sources, analyzes requirements, and presents explainable match scores — keeping final application decisions entirely in your hands.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Link
            to="/register"
            className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-bold text-base rounded-2xl transition-all shadow-xl shadow-indigo-600/30 hover:scale-[1.02]"
          >
            <span>Create Candidate Account</span>
            <ArrowRight className="h-5 w-5" />
          </Link>
          <Link
            to="/login"
            className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-slate-900 hover:bg-slate-800 text-slate-200 font-semibold text-base rounded-2xl border border-slate-800 transition-all"
          >
            <span>Sign In to Dashboard</span>
          </Link>
        </div>
      </section>

      {/* Workflow Steps Grid */}
      <section className="relative z-10 max-w-6xl mx-auto px-6 py-16 border-t border-slate-800/80">
        <div className="text-center mb-14">
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-2">How AI Job Hunter Works</h2>
          <p className="text-slate-400 text-sm">Four seamless steps from upload to application readiness</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { step: "01", title: "Upload CV", desc: "Upload PDF, DOCX, or TXT. Structured info is automatically extracted.", icon: FileCheck },
            { step: "02", title: "Set Preferences", desc: "Specify target roles, locations, employment type, and minimum salary.", icon: Target },
            { step: "03", title: "AI Search Engine", desc: "System continuously discovers legitimate jobs across configured sources.", icon: Search },
            { step: "04", title: "Review & Apply", desc: "Get explainable match scores (✓ highlights & ⚠ gaps) and open original post.", icon: Zap },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.step}
                className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl relative group hover:border-indigo-500/50 transition-all"
              >
                <div className="text-indigo-500/30 text-4xl font-extrabold mb-4">{item.step}</div>
                <div className="p-3 bg-indigo-500/10 w-fit rounded-xl mb-4 text-indigo-400 border border-indigo-500/20">
                  <Icon className="h-6 w-6" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Core Platform Features */}
      <section className="relative z-10 max-w-6xl mx-auto px-6 py-16 border-t border-slate-800/80">
        <div className="text-center mb-14">
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-2">Built for Intelligent Job Discovery</h2>
          <p className="text-slate-400 text-sm">Designed for candidate empowerment and privacy</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl">
            <CheckCircle2 className="h-8 w-8 text-emerald-400 mb-4" />
            <h3 className="text-lg font-bold text-white mb-2">Explainable Compatibility Scores</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Match percentages are weighted across Skills (35%), Experience (20%), Role (20%), Location (10%), Education (5%), Tech (5%), and Preferences (5%).
            </p>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl">
            <BellRing className="h-8 w-8 text-indigo-400 mb-4" />
            <h3 className="text-lg font-bold text-white mb-2">Automated Discovery & Alerts</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Background schedulers scan permitted RSS feeds and public APIs, instantly notifying you of newly posted opportunities.
            </p>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl">
            <Lock className="h-8 w-8 text-amber-400 mb-4" />
            <h3 className="text-lg font-bold text-white mb-2">Strict Candidate Control</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              No automatic job submissions. Application assistant tools generate cover letters and answer drafts, but final submission is 100% in your control.
            </p>
          </div>
        </div>
      </section>

      {/* Safety & Disclaimer Footer Notice */}
      <footer className="relative z-10 max-w-6xl mx-auto px-6 py-12 border-t border-slate-800/80 text-center text-xs text-slate-500 space-y-3">
        <div className="flex justify-center items-center gap-2 text-slate-400 font-semibold">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <span>AI Job Hunter SaaS Platform — Privacy & Verification Guarantee</span>
        </div>
        <p className="max-w-2xl mx-auto">
          We do not guarantee employment or fabricate application links. Original job URLs are preserved directly from official job sources.
        </p>
        <p className="text-slate-600">© 2026 AI Job Hunter. All rights reserved.</p>
      </footer>
    </div>
  );
}

