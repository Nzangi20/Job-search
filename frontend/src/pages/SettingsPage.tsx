import { FormEvent, useEffect, useState } from "react";
import { api } from "../lib/api";
import { Sliders, Mail, Send, Trash2, CheckCircle2, Save, ShieldCheck, Key, Bot, Eye, EyeOff } from "lucide-react";

type AISettings = {
  ai_provider: string;
  ai_base_url: string;
  ai_model: string;
  ai_api_key_configured: boolean;
  ai_api_key_masked: string | null;
};

export default function SettingsPage() {
  const [emailEnabled, setEmailEnabled] = useState(true);
  const [telegramEnabled, setTelegramEnabled] = useState(false);
  const [telegramChatId, setTelegramChatId] = useState("");

  const [aiSettings, setAiSettings] = useState<AISettings | null>(null);
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [aiModel, setAiModel] = useState("gpt-4o-mini");
  const [aiProvider, setAiProvider] = useState("openai");
  const [showKey, setShowKey] = useState(false);
  const [savingAi, setSavingAi] = useState(false);

  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");

  const loadSettings = async () => {
    try {
      const data = await api<AISettings>("/settings/ai");
      setAiSettings(data);
      setAiModel(data.ai_model || "gpt-4o-mini");
      setAiProvider(data.ai_provider || "openai");
    } catch {
      // Ignore
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const saveNotifications = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api("/notifications/settings", {
        method: "PUT",
        body: JSON.stringify({
          email_enabled: emailEnabled,
          telegram_enabled: telegramEnabled,
          telegram_chat_id: telegramChatId || undefined,
        }),
      });
      setMsg("Notification settings saved.");
      setTimeout(() => setMsg(""), 4000);
    } finally {
      setSaving(false);
    }
  };

  const saveAiConfig = async (e: FormEvent) => {
    e.preventDefault();
    setSavingAi(true);
    try {
      const data = await api<AISettings>("/settings/ai", {
        method: "PUT",
        body: JSON.stringify({
          ai_provider: aiProvider,
          ai_model: aiModel,
          ai_api_key: apiKeyInput ? apiKeyInput.trim() : undefined,
        }),
      });
      setAiSettings(data);
      setApiKeyInput("");
      setMsg("AI API Key & Settings saved successfully.");
      setTimeout(() => setMsg(""), 4000);
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Failed to save AI configuration");
    } finally {
      setSavingAi(false);
    }
  };

  const deleteCv = async () => {
    if (!confirm("Are you sure you want to delete your stored CV data?")) return;
    await api("/resume", { method: "DELETE" });
    setMsg("CV data deleted.");
    setTimeout(() => setMsg(""), 4000);
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Sliders className="h-6 w-6 text-indigo-400" />
            <span>Account & System Settings</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Configure AI API key, job discovery preferences, notification delivery, and privacy.
          </p>
        </div>

        {msg && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold rounded-xl">
            <CheckCircle2 className="h-4 w-4" />
            <span>{msg}</span>
          </div>
        )}
      </div>

      {/* AI & API Key Settings */}
      <div className="bg-slate-900/60 border border-indigo-500/30 rounded-2xl p-6 backdrop-blur-sm space-y-4 shadow-xl shadow-indigo-950/30">
        <div className="flex justify-between items-center border-b border-slate-800 pb-3">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Bot className="h-5 w-5 text-indigo-400" />
            <span>AI Provider & API Key Configuration</span>
          </h2>
          {aiSettings?.ai_api_key_configured ? (
            <span className="text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2.5 py-1 rounded-full font-semibold flex items-center gap-1">
              <span>🟢 Active API Key:</span>
              <span className="font-mono">{aiSettings.ai_api_key_masked}</span>
            </span>
          ) : (
            <span className="text-xs bg-amber-500/20 text-amber-300 border border-amber-500/30 px-2.5 py-1 rounded-full font-semibold">
              🟡 Using Heuristic Fallback (No Key)
            </span>
          )}
        </div>

        <form onSubmit={saveAiConfig} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                AI Provider
              </label>
              <select
                value={aiProvider}
                onChange={(e) => setAiProvider(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="openai">OpenAI (ChatGPT)</option>
                <option value="groq">Groq AI</option>
                <option value="custom">OpenAI-Compatible API</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                AI Model Name
              </label>
              <input
                type="text"
                placeholder="gpt-4o-mini"
                value={aiModel}
                onChange={(e) => setAiModel(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Key className="h-3.5 w-3.5 text-indigo-400" />
                <span>OpenAI / Provider API Key</span>
              </span>
              {aiSettings?.ai_api_key_configured && (
                <span className="text-[11px] text-slate-400">
                  Current Key: <code className="text-indigo-300">{aiSettings.ai_api_key_masked}</code>
                </span>
              )}
            </label>
            <div className="relative">
              <input
                type={showKey ? "text" : "password"}
                placeholder={aiSettings?.ai_api_key_configured ? "Enter new API key to replace current key..." : "Paste your API key here (sk-proj-...)"}
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                className="w-full pl-3.5 pr-10 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
              >
                {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            <p className="text-[11px] text-slate-500 mt-1">
              Your API key is used exclusively for CV parsing, cover letter generation, and explainable job match analysis.
            </p>
          </div>

          <div className="flex justify-end pt-1">
            <button
              type="submit"
              disabled={savingAi}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl transition-all shadow-lg shadow-indigo-600/30 disabled:opacity-50"
            >
              <Save className="h-4 w-4" />
              <span>{savingAi ? "Saving API Key..." : "Save AI API Key"}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Notification Channels */}
      <form onSubmit={saveNotifications} className="space-y-6">
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Mail className="h-4 w-4 text-indigo-400" />
            <span>Notification Delivery Preferences</span>
          </h2>

          <div className="space-y-3">
            <label className="flex items-center justify-between p-3.5 bg-slate-950 border border-slate-800 rounded-xl cursor-pointer hover:border-slate-700 transition-all">
              <div className="flex items-center gap-3">
                <Mail className="h-4 w-4 text-indigo-400" />
                <div>
                  <div className="text-sm font-semibold text-slate-200">Email Alerts</div>
                  <div className="text-xs text-slate-500">Receive summaries when newly matched jobs are found</div>
                </div>
              </div>
              <input
                type="checkbox"
                checked={emailEnabled}
                onChange={(e) => setEmailEnabled(e.target.checked)}
                className="h-4 w-4 rounded border-slate-700 text-indigo-600 focus:ring-indigo-500"
              />
            </label>

            <div className="p-3.5 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Send className="h-4 w-4 text-indigo-400" />
                  <div>
                    <div className="text-sm font-semibold text-slate-200">Telegram Instant Alerts (Optional)</div>
                    <div className="text-xs text-slate-500">Connect Telegram bot to get instant notifications</div>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={telegramEnabled}
                  onChange={(e) => setTelegramEnabled(e.target.checked)}
                  className="h-4 w-4 rounded border-slate-700 text-indigo-600 focus:ring-indigo-500"
                />
              </div>

              {telegramEnabled && (
                <div className="pt-2">
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Telegram Chat ID
                  </label>
                  <input
                    type="text"
                    placeholder="Enter Telegram Chat ID..."
                    value={telegramChatId}
                    onChange={(e) => setTelegramChatId(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700/80 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={saving}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs rounded-xl border border-slate-700 transition-all disabled:opacity-50"
            >
              <Save className="h-4 w-4" />
              <span>{saving ? "Saving..." : "Save Notification Settings"}</span>
            </button>
          </div>
        </div>

        {/* Privacy & Account Management */}
        <div className="bg-slate-900/60 border border-rose-500/20 rounded-2xl p-6 backdrop-blur-sm space-y-4">
          <h2 className="text-base font-bold text-rose-400 flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-rose-400" />
            <span>Data Privacy & Deletion</span>
          </h2>

          <p className="text-xs text-slate-400 leading-relaxed">
            Delete stored CV files, extracted text, and personal profile information from the database anytime.
          </p>

          <button
            type="button"
            onClick={deleteCv}
            className="inline-flex items-center gap-2 px-4 py-2 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-xl text-xs font-semibold transition-all"
          >
            <Trash2 className="h-4 w-4" />
            <span>Delete Stored CV & Profile Data</span>
          </button>
        </div>
      </form>
    </div>
  );
}
