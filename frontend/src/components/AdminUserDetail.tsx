import { useState } from "react";
import type { UserOutAdmin, UserDataIn } from "../api/auth/authmodels";

interface AdminUserDetailProps {
  user: UserOutAdmin;
  onBan: () => void;
  onDelete: () => void;
  onUpdate: (payload: UserDataIn) => void;
}

export default function AdminUserDetail({ user, onBan, onDelete, onUpdate }: AdminUserDetailProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState<UserDataIn>({
    name: user.name,
    surname: user.surname,
    email: user.email,
    date_of_birth: user.date_of_birth,
  });

  const handleChange = (key: keyof UserDataIn, value: string) => setFormData(prev => ({ ...prev, [key]: value }));

  const handleSave = () => {
    onUpdate(formData);
    setIsEditing(false);
  };

  return (
    <div className="card bg-base-100 shadow-lg border border-base-300 max-w-5xl mx-auto my-6 rounded-lg">
      <div className="card-body p-6">
        <h2 className="text-2xl font-semibold text-center mb-6">Dettaglio Utente</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-base">
          <div className="space-y-3">
            <div>
              <label className="font-semibold block mb-1">Nome</label>
              {isEditing ? (
                <input type="text" className="input input-bordered w-full" value={formData.name} onChange={e => handleChange("name", e.target.value)} />
              ) : <p>{user.name}</p>}
            </div>

            <div>
              <label className="font-semibold block mb-1">Cognome</label>
              {isEditing ? (
                <input type="text" className="input input-bordered w-full" value={formData.surname} onChange={e => handleChange("surname", e.target.value)} />
              ) : <p>{user.surname}</p>}
            </div>

            <div>
              <label className="font-semibold block mb-1">Email</label>
              {isEditing ? (
                <input type="email" className="input input-bordered w-full" value={formData.email} onChange={e => handleChange("email", e.target.value)} />
              ) : <p>{user.email}</p>}
            </div>

            <div>
              <label className="font-semibold block mb-1">Data di nascita</label>
              {isEditing ? (
                <input type="date" className="input input-bordered w-full" value={formData.date_of_birth} onChange={e => handleChange("date_of_birth", e.target.value)} />
              ) : <p>{user.date_of_birth}</p>}
            </div>
          </div>

          <div className="space-y-2">
            <p><strong>ID Utente:</strong> {user.id}</p>
            <p><strong>Ruolo:</strong> {user.role}</p>
            <p>
              <strong>Stato BAN:</strong>{" "}
              <span className={`badge ${user.is_banned ? "badge-error" : "badge-success"}`}>
                {user.is_banned ? "BANNED" : "ACTIVE"}
              </span>
            </p>
            <p><strong>Creato il:</strong> {new Date(user.created_at).toLocaleDateString()}</p>
            <p><strong>Ultimo login:</strong> {user.last_login ? new Date(user.last_login).toLocaleString() : "-"}</p>
          </div>
        </div>

        <div className="mt-6 flex flex-col sm:flex-row gap-4">
          <button onClick={onBan} className="btn btn-warning w-full sm:w-auto">Ban</button>
          <button onClick={onDelete} className="btn btn-error w-full sm:w-auto">Elimina</button>
          {isEditing ? (
            <button onClick={handleSave} className="btn btn-success w-full sm:w-auto">Salva</button>
          ) : (
            <button onClick={() => setIsEditing(true)} className="btn btn-info w-full sm:w-auto">Modifica</button>
          )}
        </div>
      </div>
    </div>
  );
}
