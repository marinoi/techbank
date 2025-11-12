import { NotificationDetailsOut } from "../api/notification/notificationmodels";

interface NotificationModalProps {
  notification: NotificationDetailsOut | null;
  onClose: () => void;
}

export default function NotificationModal({ notification, onClose }: NotificationModalProps) {
  if (!notification) return null;

  return (
    <div className="modal modal-open">
      <div className="modal-box relative max-w-lg">
        <h3 className="text-lg font-bold mb-4 text-center">Dettaglio Notifica</h3>

        <button
          type="button"
          className="btn btn-sm btn-circle absolute right-2 top-2"
          onClick={onClose}
        >
          ✕
        </button>

        <div className="space-y-2 text-sm">
          <p><strong>ID:</strong> {notification.id}</p>
          <p><strong>Data:</strong> {new Date(notification.created_at).toLocaleString()}</p>
          <p><strong>Emittente:</strong> {notification.emitter}</p>
          <p><strong>Motivo:</strong> {notification.reason}</p>
          <p><strong>Messaggio:</strong> {notification.message || "-"}</p>
          {notification.source_event_id && (
            <p><strong>Evento Collegato:</strong> {notification.source_event_id}</p>
          )}
        </div>
      </div>
    </div>
  );
}
