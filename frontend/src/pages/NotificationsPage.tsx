import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Bell, BellOff, Calendar } from "lucide-react";

type Notification = { id: number; title: string; body: string; read: boolean; created_at: string };

export default function NotificationsPage() {
  const [items, setItems] = useState<Notification[]>([]);

  useEffect(() => {
    api<Notification[]>("/notifications").then(setItems).catch(() => {});
  }, []);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <Bell className="h-6 w-6 text-indigo-400" />
          <span>Match & System Notifications</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Stay updated on newly discovered jobs and automated scheduled search matches.
        </p>
      </div>

      <div className="space-y-3">
        {items.map((n) => (
          <div
            key={n.id}
            className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-sm space-y-2 hover:border-slate-700 transition-all"
          >
            <div className="flex justify-between items-start gap-4">
              <h3 className="font-bold text-base text-white">{n.title}</h3>
              <div className="flex items-center gap-1.5 text-xs text-slate-500 shrink-0">
                <Calendar className="h-3.5 w-3.5" />
                <span>{new Date(n.created_at).toLocaleString()}</span>
              </div>
            </div>
            <p className="text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
              {n.body}
            </p>
          </div>
        ))}

        {!items.length && (
          <div className="text-center py-12 px-4 rounded-2xl bg-slate-900/40 border border-slate-800">
            <BellOff className="h-10 w-10 text-slate-500 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-white mb-1">No Notifications Yet</h3>
            <p className="text-slate-400 text-sm max-w-md mx-auto">
              You will receive notifications here when new relevant job matches are discovered by the scheduler.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

