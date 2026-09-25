import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const nav = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await register(email, password, fullName || undefined);
      nav("/resume");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <form onSubmit={onSubmit} className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8">
        <h1 className="text-2xl font-bold mb-6">Create account</h1>
        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}
        <label className="block text-sm mb-4">
          Full name
          <input
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="mt-1 w-full rounded-lg bg-slate-950 border border-slate-700 px-3 py-2"
          />
        </label>
        <label className="block text-sm mb-4">
          Email
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-lg bg-slate-950 border border-slate-700 px-3 py-2"
          />
        </label>
        <label className="block text-sm mb-6">
          Password (min 8 characters)
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-lg bg-slate-950 border border-slate-700 px-3 py-2"
          />
        </label>
        <button type="submit" className="w-full bg-brand-600 hover:bg-brand-700 py-2 rounded-lg font-medium">
          Register
        </button>
        <p className="text-sm text-slate-400 mt-4 text-center">
          Already have an account? <Link to="/login" className="text-brand-500">Log in</Link>
        </p>
      </form>
    </div>
  );
}
