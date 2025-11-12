import { useState, useMemo } from "react";
import type { NotificationOut } from "../api/notification/notificationmodels";

interface AdminNotificationsTableProps {
  notifications: NotificationOut[];
  onViewNotification: (notificationId: string) => void;
}

export default function AdminNotificationsTable({ notifications, onViewNotification }: AdminNotificationsTableProps) {
  const [search, setSearch] = useState("");

  const filteredNotifications = useMemo(() => {
    if (!search) return notifications;
    const lower = search.toLowerCase();
    return notifications.filter(n =>
      n.id.toLowerCase().includes(lower) ||
      n.emitter.toLowerCase().includes(lower) ||
      n.reason.toLowerCase().includes(lower)
    );
  }, [search, notifications]);

  return (
    <div className="card bg-base-100 shadow-lg overflow-hidden">
      <div className="card-body p-4">
        <h2 className="text-lg font-semibold mb-3 text-center">Notifiche Utente</h2>

        <input
          type="text"
          placeholder="Cerca per ID, emittente o motivo..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="input input-bordered w-full mb-4"
        />

        <div className="overflow-x-auto max-h-[400px]">
          <table className="table table-zebra w-full min-w-[600px]">
            <thead>
              <tr className="text-sm text-base-content/70">
                <th>ID</th>
                <th>Data</th>
                <th>Emittente</th>
                <th>Motivo</th>
              </tr>
            </thead>
            <tbody>
              {!filteredNotifications.length ? (
                <tr><td colSpan={4} className="text-center text-sm text-base-content/60">Nessuna notifica trovata.</td></tr>
              ) : (
                filteredNotifications.map(n => (
                  <tr key={n.id} onClick={() => onViewNotification(n.id)} className="cursor-pointer hover:bg-base-200 transition">
                    <td className="font-mono text-xs truncate max-w-[100px]" title={n.id}>{n.id}</td>
                    <td>{new Date(n.created_at).toLocaleString()}</td>
                    <td>{n.emitter}</td>
                    <td>{n.reason}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
