import { createContext, useContext, useState, useEffect, type ReactNode, type Dispatch, type SetStateAction } from "react";
import { Navigate } from "react-router-dom";
import { authServiceAPI } from "../api/auth/authapi";

export const Roles = { 
  PUBLIC: "public", 
  USER: "user", 
  ADMIN: "admin" 
} as const;

export type Role = typeof Roles[keyof typeof Roles];

type RoleContextType = { 
  role: Role; 
  setRole: Dispatch<SetStateAction<Role>>; 
  loading: boolean;
};

const RoleContext = createContext<RoleContextType>({
  role: Roles.PUBLIC,
  setRole: () => {},
  loading: true,
});

export function RoleProvider({ children }: { children: ReactNode }) {
  const [role, setRole] = useState<Role>(Roles.PUBLIC);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchRole() {
      try {
        const userData = await authServiceAPI.privateMe();
        if (userData?.role && Object.values(Roles).includes(userData.role as Role)) {
          setRole(userData.role as Role);
        } else {
          setRole(Roles.PUBLIC);
        }
      } catch (err: any) {
        if (err.response?.status === 401) {
          setRole(Roles.PUBLIC);
        } else {
          console.error("Error fetching user role:", err);
          setRole(Roles.PUBLIC);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchRole();
  }, []);

  return (
    <RoleContext.Provider value={{ role, setRole, loading }}>
      {children}
    </RoleContext.Provider>
  );
}

export function useRole() {
  return useContext(RoleContext);
}

export function useRoleFlags() {
  const { role } = useRole();
  return {
    isPublic: role === Roles.PUBLIC,
    isUser: role === Roles.USER,
    isAdmin: role === Roles.ADMIN,
  };
}

export function RequiredRoleRouting({
  allowedRoles,
  children
}: {
  allowedRoles: Role[];
  children: ReactNode;
}) {
  const { role, loading } = useRole();

  if (loading) return <span className="loading loading-spinner loading-xl"></span>;

  return allowedRoles.includes(role) ? <>{children}</> : <Navigate to="/login" replace />;
}
