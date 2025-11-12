import { Link, useNavigate } from "react-router-dom";
import companyName from "../constants/companyName";
import { Roles, useRole, useRoleFlags } from "../contexts/RoleContext"
import { authServiceAPI } from "../api/auth/authapi";


export default function NavBar() {
  const { setRole } = useRole();
  const { isPublic, isUser, isAdmin } = useRoleFlags();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await authServiceAPI.privateLogout();
      setRole(Roles.PUBLIC);
      navigate("/login");
    } catch (err) {
      console.error("LogoutError:", err);
    }
  };

  return (
    <nav className="navbar bg-base-300 shadow-sm">
      <div className="flex-1 md:ml-20">

        {isUser && <Link to="/wallet"><button className="btn btn-ghost text-2xl md:text-3xl">{companyName}</button></Link>}

        {isPublic && <Link to="/"><button className="btn btn-ghost text-2xl md:text-3xl">{companyName}</button></Link>}
        {isAdmin && <Link to="/dashboard"><button className="btn btn-ghost text-2xl md:text-3xl">{companyName}</button></Link>}

      </div>

      <div className="flex-1 flex justify-end items-center md:mr-20 gap-2">
        {isPublic && (
          <>
            <Link to="/login"><button className="btn btn-primary btn-sm md:btn-md">Accedi</button></Link>
            <Link to="/signin"><button className="btn btn-outline btn-sm md:btn-md">Registrati</button></Link>
          </>
        )}

        {isUser && (
          <>
            <Link to="/notification"><button className="btn btn-secondary btn-sm md:btn-md">Notifiche</button></Link>
          </>
        )}

        
        {isAdmin && (
          <>
            <Link to="/stress-test"><button className="btn btn-info btn-sm md:btn-md">API Test</button></Link>
          </>
        )}

        {(isUser || isAdmin) && (
          <>
            <button onClick={handleLogout} className="btn btn-outline btn-sm md:btn-md">Esci</button>
          </>
        )}
      </div>
    </nav>
  );
}
