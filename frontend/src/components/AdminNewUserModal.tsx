import { useState } from "react";
import type { UserDataIn } from "../api/auth/authmodels";

interface AdminNewUserModalProps {
  onClose: () => void;
  onCreate: (data: UserDataIn) => void | Promise<void>;
}

export default function AdminNewUserModal({ onClose, onCreate }: AdminNewUserModalProps) {
  const [formData, setFormData] = useState<UserDataIn>({ email: "", name: "", surname: "", date_of_birth: "", password: "", role: "user" });

  const handleChange = (key: keyof UserDataIn, value: string) => setFormData(prev => ({ ...prev, [key]: value }));

  const handleSubmit = async (e: React.FormEvent) => { e.preventDefault(); await onCreate(formData); setFormData({ email: "", name: "", surname: "", date_of_birth: "", password: "", role: "user" }); onClose(); };

  return (
    <div className="modal modal-open flex items-center justify-center">
      <div className="modal-box bg-base-100 shadow-md p-6 relative w-full max-w-md">
        <button type="button" className="btn btn-sm btn-circle absolute right-3 top-3" onClick={onClose}>✕</button>
        <h3 className="text-2xl font-bold text-center mb-6">Nuovo Utente</h3>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input type="text" placeholder="Nome" className="input input-bordered w-full" value={formData.name} onChange={e => handleChange("name", e.target.value)} required />
          <input type="text" placeholder="Cognome" className="input input-bordered w-full" value={formData.surname} onChange={e => handleChange("surname", e.target.value)} required />
          <input type="email" placeholder="Email" className="input input-bordered w-full" value={formData.email} onChange={e => handleChange("email", e.target.value)} required />
          <input type="date" className="input input-bordered w-full" value={formData.date_of_birth} onChange={e => handleChange("date_of_birth", e.target.value)} required />
          <input type="password" placeholder="Password" className="input input-bordered w-full" value={formData.password} onChange={e => handleChange("password", e.target.value)} required />
          <select className="select select-bordered w-full" value={formData.role} onChange={e => handleChange("role", e.target.value as "user" | "admin")}>
            <option value="user">Utente</option>
            <option value="admin">Admin</option>
          </select>
          <button type="submit" className="btn btn-primary w-full mt-2">Crea Utente</button>
        </form>
      </div>
    </div>
  );
}
