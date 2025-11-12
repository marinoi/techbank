import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authServiceAPI } from "../api/auth/authapi";
import type { UserDataIn } from "../api/auth/authmodels";

export default function SigninForm() {
  const [name, setName] = useState("");
  const [surname, setSurname] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState(""); // YYYY-MM-DD
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const payload: UserDataIn = { name, surname, email, password, date_of_birth: dateOfBirth };

    try {
      const response = await authServiceAPI.publicSignup(payload);
      console.log("Registrazione avvenuta:", response);
      navigate("/login");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Errore durante la registrazione");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="w-full max-w-sm mx-4 md:mx-auto p-6 bg-base-200 rounded-lg shadow-md text-center" onSubmit={handleSubmit}>
      <h2 className="text-2xl font-bold mb-6">Registrati</h2>
      {error && <p className="text-red-500 mb-4">{error}</p>}

      <div className="form-control mb-4">
        <input id="name" type="text" placeholder="Nome" className="input input-bordered" value={name} onChange={e => setName(e.target.value)} required minLength={2} maxLength={32} />
      </div>

      <div className="form-control mb-4">
        <input id="surname" type="text" placeholder="Cognome" className="input input-bordered" value={surname} onChange={e => setSurname(e.target.value)} required minLength={2} maxLength={32} />
      </div>

      <div className="form-control mb-4">
        <input id="email" type="email" placeholder="Email" className="input input-bordered" value={email} onChange={e => setEmail(e.target.value)} required />
      </div>

      <div className="form-control mb-4">
        <input id="dateOfBirth" type="date" className="input input-bordered" value={dateOfBirth} onChange={e => setDateOfBirth(e.target.value)} required />
      </div>

      <div className="form-control mb-5">
        <input id="password" type="password" placeholder="Password" className="input input-bordered" value={password} onChange={e => setPassword(e.target.value)} required minLength={8} />
      </div>

      <button type="submit" className="btn btn-primary w-full" disabled={loading}>
        {loading ? "Registrando..." : "Registrati"}
      </button>
    </form>
  );
}
