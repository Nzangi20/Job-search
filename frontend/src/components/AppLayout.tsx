import { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  LayoutDashboard,
  FileText,
  Briefcase,
  Bookmark,
  CheckCircle2,
  History,
  Bell,
  Sliders,
  ShieldAlert,
  LogOut,
  Sparkles,
  Menu,
  X,
  User as UserIcon,
} from "lucide-react";

const links = [
  { label: "Dashboard", to: "/dashboard", icon: LayoutDashboard },
  { label: "My CV", to: "/resume", icon: FileText },
  { label: "Job Matches", to: "/jobs", icon: Briefcase },
  { label: "Saved Jobs", to: "/saved", icon: Bookmark },
  { label: "Applications", to: "/applications", icon: CheckCircle2 },
  { label: "Search History", to: "/searches", icon: History },
  { label: "Notifications", to: "/notifications", icon: Bell },
  { label: "Settings", to: "/settings", icon: Sliders },
];

export default function AppLayout() {
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen flex bg-slate-950 text-slate-100 font-sans antialiased">
      {/* Sidebar Desktop */}
      <aside className="w-64 border-r border-slate-800/80 bg-slate-900/95 flex flex-col hidden md:flex sticky top-0 h-screen z-30 shadow-xl">
        <div className="p-5 border-b border-slate-800/80 flex items-center justify-between">
          <Link to="/dashboard" className="flex items-center gap-2.5 font-bold text-lg text-white">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent font-extrabold tracking-tight">
              AI Job Hunter
            </span>
          </Link>
        </div>

        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {links.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30 font-semibold"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                  }`
                }
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}

          {user?.role === "admin" && (
            <div className="pt-4 mt-4 border-t border-slate-800/60">
              <div className="px-3.5 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                System Admin
              </div>
              <NavLink
                to="/admin"
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                      : "text-amber-400/80 hover:bg-amber-500/10 hover:text-amber-300"
                  }`
                }
              >
                <ShieldAlert className="h-4 w-4 shrink-0" />
                <span>Admin Console</span>
              </NavLink>
            </div>
          )}
        </nav>

        {/* User Card at bottom of sidebar */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-900/40">
          <Link
            to="/profile"
            className="flex items-center gap-3 p-2 rounded-xl hover:bg-slate-800/60 transition-colors group mb-2"
          >
            <div className="h-9 w-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 font-semibold group-hover:border-indigo-500 transition-colors">
              <UserIcon className="h-4 w-4 text-indigo-400" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-slate-200 truncate group-hover:text-indigo-300">
                {user?.full_name || user?.email?.split("@")[0]}
              </div>
              <div className="text-xs text-slate-400 truncate">{user?.email}</div>
            </div>
          </Link>
          <button
            onClick={logout}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 text-xs font-medium text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 border border-slate-800 hover:border-rose-500/30 rounded-lg transition-all"
          >
            <LogOut className="h-3.5 w-3.5" />
            <span>Sign out</span>
          </button>
        </div>
      </aside>

      {/* Mobile Drawer Overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-950/80 backdrop-blur-sm md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Mobile Drawer */}
      <div
        className={`fixed top-0 left-0 bottom-0 w-72 z-50 bg-slate-900 border-r border-slate-800 p-4 flex flex-col transform transition-transform duration-300 md:hidden ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
          <div className="flex items-center gap-2 font-bold text-white">
            <Sparkles className="h-5 w-5 text-indigo-400" />
            <span>AI Job Hunter</span>
          </div>
          <button onClick={() => setMobileOpen(false)} className="p-1 text-slate-400 hover:text-white">
            <X className="h-5 w-5" />
          </button>
        </div>
        <nav className="flex-1 space-y-1">
          {links.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium ${
                    isActive ? "bg-indigo-600 text-white" : "text-slate-300 hover:bg-slate-800"
                  }`
                }
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
          {user?.role === "admin" && (
            <NavLink
              to="/admin"
              onClick={() => setMobileOpen(false)}
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-amber-300 hover:bg-amber-500/10"
            >
              <ShieldAlert className="h-4 w-4" />
              <span>Admin Console</span>
            </NavLink>
          )}
        </nav>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-16 border-b border-slate-800/80 bg-slate-900/90 px-4 md:px-8 flex items-center justify-between sticky top-0 z-20 shadow-md">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileOpen(true)}
              className="md:hidden p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg"
            >
              <Menu className="h-5 w-5" />
            </button>
            <div className="hidden sm:flex items-center gap-2 text-xs font-medium text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-full">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>AI Job Search Engine Active</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/profile"
              className="flex items-center gap-2 text-xs font-medium text-slate-300 hover:text-indigo-400 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg transition-all"
            >
              <UserIcon className="h-3.5 w-3.5 text-indigo-400" />
              <span className="hidden sm:inline">Candidate Profile</span>
            </Link>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-4 md:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

