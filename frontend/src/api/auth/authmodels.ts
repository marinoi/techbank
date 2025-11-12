export type Role = "user" | "admin";


export interface UserDataIn {
  email: string;
  name: string;
  surname: string;
  date_of_birth: string; 
  password?: string;
  role?: Role; 
}

export interface LoginDataIn {
  email: string;
  password: string;
}


export interface UserOut {
  name: string;
  surname: string;
  email: string;
  role: Role;
}

export interface UserOutAdmin extends UserOut {
  id: string;
  created_at: string;      
  date_of_birth: string;  
  is_banned: boolean;
  last_login: string | null;
}

export interface HealthCheckResponse {
  "health-check": string;
}
