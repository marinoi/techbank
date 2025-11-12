import { useEffect, useState } from "react";
import { notificationServiceAPI } from "../api/notification/notificationapi";
import type { NotificationOut, NotificationDetailsOut } from "../api/notification/notificationmodels";

export default function NotificationPage() {
  const [notifications, setNotifications] = useState<NotificationOut[]>([]);
  const [selectedNotification, setSelectedNotification] = useState<NotificationDetailsOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await notificationServiceAPI.privateGetNotifications();
        setNotifications(data);
      } catch {
        setError("Impossibile caricare le notifiche.");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const viewNotification = async (id: string) => {
    try {
      const details = await notificationServiceAPI.privateGetNotification(id);
      setSelectedNotification(details);
    } catch {
      alert("Impossibile caricare i dettagli della notifica.");
    }
  };

  if (loading) return <div className="text-center mt-10 loading loading-lg"></div>;
  if (error) return <p className="text-error text-center mt-10">{error}</p>;

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      <div className="card bg-base-200 shadow-md p-4">
        <h2 className="text-xl font-semibold mb-4">Notifiche</h2>
        {!notifications.length ? (
          <p className="text-gray-500">Nessuna notifica disponibile.</p>
        ) : (
          <div className="space-y-2">
            <div className="overflow-x-auto hidden sm:block">
              <table className="table w-full table-zebra">
                <thead>
                  <tr><th>ID</th><th>Emittente</th><th>Motivo</th><th>Data</th></tr>
                </thead>
                <tbody>
                  {notifications.map(n => (
                    <tr key={n.id} className="cursor-pointer" onClick={() => viewNotification(n.id)}>
                      <td className="font-mono truncate max-w-[150px]">{n.id}</td>
                      <td>{n.emitter}</td>
                      <td>{n.reason}</td>
                      <td>{new Date(n.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="sm:hidden flex flex-col gap-2">
              {notifications.map(n => (
                <div key={n.id} className="p-3 rounded-lg bg-base-100 shadow cursor-pointer flex flex-col gap-1" onClick={() => viewNotification(n.id)}>
                  <p className="font-mono text-sm break-all"><strong>ID:</strong> {n.id}</p>
                  <p><strong>Emittente:</strong> {n.emitter}</p>
                  <p><strong>Motivo:</strong> {n.reason}</p>
                  <p className="text-xs text-gray-500">{new Date(n.created_at).toLocaleString()}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {selectedNotification && (
        <div className="modal modal-open">
          <div className="modal-box relative">
            <h3 className="text-lg font-bold">Dettagli Notifica</h3>
            <button className="btn btn-sm btn-circle absolute right-2 top-2" onClick={() => setSelectedNotification(null)}>✕</button>
            <div className="mt-4 space-y-2 text-sm">
              <p><strong>ID:</strong> {selectedNotification.id}</p>
              <p><strong>Utente:</strong> {selectedNotification.user_id}</p>
              <p><strong>Emittente:</strong> {selectedNotification.emitter}</p>
              <p><strong>Motivo:</strong> {selectedNotification.reason}</p>
              <p><strong>Messaggio:</strong> {selectedNotification.message}</p>
              {selectedNotification.source_event_id && <p><strong>Evento sorgente:</strong> {selectedNotification.source_event_id}</p>}
              <p><strong>Data:</strong> {new Date(selectedNotification.created_at).toLocaleString()}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
