import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await login(email, password);
      nav("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <form onSubmit={onSubmit} className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8">
        <h1 className="text-2xl font-bold mb-6">Log in</h1>
        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}
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
          Password
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-lg bg-slate-950 border border-slate-700 px-3 py-2"
          />
        </label>
        <button type="submit" className="w-full bg-brand-600 hover:bg-brand-700 py-2 rounded-lg font-medium">
          Log in
        </button>
        <p className="text-sm text-slate-400 mt-4 text-center">
          No account? <Link to="/register" className="text-brand-500">Register</Link>
        </p>
      </form>
    </div>
  );
}
