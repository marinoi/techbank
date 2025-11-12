import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useRole, Roles, Role } from "../contexts/RoleContext";
import { authServiceAPI } from "../api/auth/authapi";

export default function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const { role, setRole } = useRole();
  const navigate = useNavigate();

  useEffect(() => {
    if (role === Roles.USER) navigate("/wallet");
    else if (role === Roles.ADMIN) navigate("/dashboard");
  }, [role, navigate]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setErrorMessage("");
    try {
      const user = await authServiceAPI.publicLogin({ email, password });
      setRole(user.role as Role);
    } catch (err: any) {
      console.error("Errore login:", err);
      setErrorMessage(err.response?.status === 401 ? "Email o password non corretti" : "Errore durante il login. Riprova più tardi.");
    }
  }

  return (
      <form className="w-full max-w-sm mx-4 md:mx-auto p-6 bg-base-200 rounded-lg shadow-md text-center" onSubmit={handleSubmit}>
        <h2 className="text-2xl font-bold mb-6">Accedi</h2>
        {errorMessage && <div className="mb-4 text-red-600 font-semibold">{errorMessage}</div>}
        <div className="form-control mb-4">
          <input id="email" type="email" placeholder="Inserisci la tua email" className={`input input-bordered w-full ${errorMessage ? "input-error" : ""}`} value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        <div className="form-control mb-5">
          <input type="password" placeholder="Inserisci la tua password" className={`input input-bordered w-full ${errorMessage ? "input-error" : ""}`} value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="current-password" />
        </div>
        <div className="mb-4">
          <button type="button" onClick={() => alert("Funzione non implementata")} className="link link-hover text-sm">Password dimenticata?</button>
        </div>
        <button type="submit" className="btn btn-primary w-full">Accedi</button>
      </form>
  );
}
