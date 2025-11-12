import { useState, useMemo } from "react";
import type { UserOutAdmin } from "../api/auth/authmodels";

interface AdminUsersTableProps {
  users: UserOutAdmin[];
  onSelectUser: (user: UserOutAdmin) => void;
}

export default function AdminUsersTable({ users, onSelectUser }: AdminUsersTableProps) {
  const [search, setSearch] = useState("");

  const filteredUsers = useMemo(() => {
    if (!search) return users;
    const lower = search.toLowerCase();
    return users.filter(u =>
      u.id.toLowerCase().includes(lower) ||
      u.email.toLowerCase().includes(lower) ||
      u.name.toLowerCase().includes(lower) ||
      u.surname.toLowerCase().includes(lower) ||
      u.role.toLowerCase().includes(lower)
    );
  }, [search, users]);

  return (
    <div className="card bg-base-100 shadow-lg overflow-hidden">
      <div className="card-body p-4">
        <h2 className="text-lg font-semibold mb-3 text-center">Lista Utenti</h2>

        <input
          type="text"
          placeholder="Cerca per ID, nome, cognome, email o ruolo..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="input input-bordered w-full mb-4"
        />

        <div className="overflow-x-auto max-h-[400px]">
          <table className="table table-zebra w-full min-w-[600px]">
            <thead>
              <tr className="text-sm text-base-content/70">
                <th>ID</th>
                <th>Email</th>
                <th>Nome completo</th>
                <th>Ruolo</th>
                <th>Bannato</th>
              </tr>
            </thead>
            <tbody>
              {!filteredUsers.length ? (
                <tr><td colSpan={5} className="text-center text-sm text-base-content/60">Nessun utente trovato.</td></tr>
              ) : (
                filteredUsers.map(u => (
                  <tr key={u.id} onClick={() => onSelectUser(u)} className="cursor-pointer hover:bg-base-200 transition">
                    <td className="font-mono text-xs truncate max-w-[100px]" title={u.id}>{u.id}</td>
                    <td className="truncate max-w-[180px]" title={u.email}>{u.email}</td>
                    <td className="truncate max-w-[200px]" title={`${u.name} ${u.surname}`}>{u.name} {u.surname}</td>
                    <td>
                      <span className={`badge ${u.role === "admin" ? "badge-info" : "badge-ghost"}`}>{u.role}</span>
                    </td>
                    <td>
                      {u.is_banned ? <span className="badge badge-error">Sì</span> : <span className="badge badge-success">No</span>}
                    </td>
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
