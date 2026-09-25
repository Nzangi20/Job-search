import { FormEvent, useEffect, useState } from "react";
import { api } from "../lib/api";
import {
  UserCheck,
  Save,
  Sparkles,
  Tag,
  Briefcase,
  MapPin,
  DollarSign,
  CheckCircle2,
  ListPlus,
} from "lucide-react";

type Profile = {
  professional_level: string | null;
  professional_summary: string | null;
  preferred_roles: string[];
  preferred_locations: string[];
  employment_types: string[];
  minimum_salary: number | null;
  experience_level: string | null;
  work_authorization: string | null;
  keywords: string[];
  search_terms: string[];
  skills: string[];
};

function parseList(s: string) {
  return s
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean);
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    api<Profile>("/profile").then((p) => {
      setProfile({
        ...p,
        preferred_roles: p.preferred_roles || [],
        preferred_locations: p.preferred_locations || [],
        employment_types: p.employment_types || [],
        keywords: p.keywords || [],
        search_terms: p.search_terms || [],
        skills: p.skills || [],
      });
    });
  }, []);

  const save = async (e: FormEvent) => {
    e.preventDefault();
    if (!profile) return;
    setSaving(true);
    try {
      await api("/profile", { method: "PUT", body: JSON.stringify(profile) });
      setMessage("Candidate profile saved successfully.");
      setTimeout(() => setMessage(""), 4000);
    } finally {
      setSaving(false);
    }
  };

  if (!profile) {
    return (
      <div className="py-12 text-center text-slate-400">
        <Sparkles className="h-8 w-8 text-indigo-400 animate-spin mx-auto mb-2" />
        <p>Loading candidate profile...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <UserCheck className="h-6 w-6 text-indigo-400" />
            <span>Structured Candidate Profile</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Review and edit information extracted from your CV or define custom preferences.
          </p>
        </div>

        {message && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold rounded-xl">
            <CheckCircle2 className="h-4 w-4" />
            <span>{message}</span>
          </div>
        )}
      </div>

      <form onSubmit={save} className="space-y-6">
        {/* Professional Summary Section */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-indigo-400" />
            <span>Professional Summary & Level</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Seniority / Professional Level
              </label>
              <select
                value={profile.professional_level || profile.experience_level || ""}
                onChange={(e) => setProfile({ ...profile, professional_level: e.target.value, experience_level: e.target.value })}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="">Select Level...</option>
                <option value="Internship">Internship</option>
                <option value="Entry Level">Entry Level / Junior</option>
                <option value="Mid Level">Mid Level</option>
                <option value="Senior">Senior Level</option>
                <option value="Lead / Executive">Lead / Executive</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Work Authorization (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. Authorized for Kenya, Remote worldwide"
                value={profile.work_authorization || ""}
                onChange={(e) => setProfile({ ...profile, work_authorization: e.target.value })}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Professional Overview & Bio
            </label>
            <textarea
              rows={4}
              value={profile.professional_summary || ""}
              onChange={(e) => setProfile({ ...profile, professional_summary: e.target.value })}
              placeholder="Short professional summary..."
              className="w-full px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-indigo-500 leading-relaxed"
            />
          </div>
        </div>

        {/* Skills & Technologies */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Tag className="h-4 w-4 text-indigo-400" />
            <span>Technical Skills & Tools (Comma-separated)</span>
          </h2>

          <div>
            <input
              type="text"
              value={profile.skills.join(", ")}
              onChange={(e) => setProfile({ ...profile, skills: parseList(e.target.value) })}
              placeholder="Python, React, SQL, FastAPI, Machine Learning, Docker..."
              className="w-full px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            />
            <div className="flex flex-wrap gap-1.5 mt-3">
              {profile.skills.map((skill) => (
                <span key={skill} className="text-xs bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 px-2.5 py-1 rounded-lg">
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Preferences Section */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Briefcase className="h-4 w-4 text-indigo-400" />
            <span>Job Preferences & Criteria</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1">
                <Briefcase className="h-3 w-3 text-slate-400" />
                <span>Preferred Job Titles (comma-separated)</span>
              </label>
              <input
                type="text"
                value={profile.preferred_roles.join(", ")}
                onChange={(e) => setProfile({ ...profile, preferred_roles: parseList(e.target.value) })}
                placeholder="Python Developer, Data Analyst, AI Specialist..."
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1">
                <MapPin className="h-3 w-3 text-slate-400" />
                <span>Preferred Locations</span>
              </label>
              <input
                type="text"
                value={profile.preferred_locations.join(", ")}
                onChange={(e) => setProfile({ ...profile, preferred_locations: parseList(e.target.value) })}
                placeholder="Remote, Kenya, Worldwide..."
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Employment Types (comma-separated)
              </label>
              <input
                type="text"
                value={profile.employment_types.join(", ")}
                onChange={(e) => setProfile({ ...profile, employment_types: parseList(e.target.value) })}
                placeholder="full-time, contract, internship, freelance"
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1">
                <DollarSign className="h-3 w-3 text-slate-400" />
                <span>Minimum Salary Requirement ($ USD / yr)</span>
              </label>
              <input
                type="number"
                placeholder="e.g. 50000"
                value={profile.minimum_salary || ""}
                onChange={(e) => setProfile({ ...profile, minimum_salary: e.target.value ? Number(e.target.value) : null })}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1">
              <ListPlus className="h-3 w-3 text-slate-400" />
              <span>Automated Search Keywords & Terms</span>
            </label>
            <input
              type="text"
              value={profile.search_terms.join(", ")}
              onChange={(e) => setProfile({ ...profile, search_terms: parseList(e.target.value) })}
              placeholder="Python Backend, Junior Data Scientist, Remote AI..."
              className="w-full px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm rounded-xl transition-all shadow-lg shadow-indigo-600/30 disabled:opacity-50"
          >
            <Save className="h-4 w-4" />
            <span>{saving ? "Saving Changes..." : "Save Candidate Profile"}</span>
          </button>
        </div>
      </form>
    </div>
  );
}

