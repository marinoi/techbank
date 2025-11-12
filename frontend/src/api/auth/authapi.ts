import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from "axios";
import type {
  UserDataIn,
  LoginDataIn,
  UserOut,
  UserOutAdmin,
} from "./authmodels";
import type { GenericResponse } from "../common/models";


export class AuthServiceAPI {
  private api: AxiosInstance;
  private _user: UserOut | null = null;

  constructor(baseURL: string) {
    this.api = axios.create({
      baseURL,
      headers: { "Content-Type": "application/json" },
      withCredentials: true,
    });

    this.api.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
        const status = error.response?.status;
        const detail = error.response?.data?.detail;

        if (status === 401 && detail === "token-expired" && !originalRequest._retry) {
          try {
            originalRequest._retry = true;
            await this.publicRefreshToken(); 
            return this.api(originalRequest);
          } catch (refreshError) {
            console.log(refreshError);
          }
        }

        return Promise.reject(error);
      }
    ); 
  }   


  get user(): UserOut | null {
    return this._user;
  }

  get isLoggedIn(): boolean {
    return !!this._user;
  }

  async publicSignup(payload: UserDataIn): Promise<GenericResponse> {
    const { data } = await this.api.post<GenericResponse>("/signup", payload);
    return data;
  }

  async publicLogin(payload: LoginDataIn): Promise<UserOut> {
    const { data } = await this.api.post<UserOut>("/login", payload);
    this._user = data;
    return data;
  }

  async publicRefreshToken(): Promise<GenericResponse> {
    const { data } = await this.api.get<GenericResponse>("/refresh-token");
    return data;
  }

  async privateMe(): Promise<UserOut> {
    const { data } = await this.api.get<UserOut>("/private/me");
    this._user = data;
    return data;
  }

  async privateLogout(): Promise<GenericResponse> {
    const { data } = await this.api.get<GenericResponse>("/private/logout");
    this._user = null;
    return data;
  }

  async adminGetUsers(): Promise<UserOutAdmin[]> {
    const { data } = await this.api.get<UserOutAdmin[]>("/admin/users");
    return data;
  }

  async adminGetUser(userId: string): Promise<UserOutAdmin> {
    const { data } = await this.api.get<UserOutAdmin>(`/admin/users/${userId}`);
    return data;
  }

  async adminCreateUser(payload: UserDataIn): Promise<GenericResponse> {
    const { data } = await this.api.post<GenericResponse>("/admin/user/new", payload);
    return data;
  }

  async adminUpdateUser(userId: string, payload: UserDataIn): Promise<GenericResponse> {
    const { data } = await this.api.put<GenericResponse>(`/admin/users/update/${userId}`, payload);
    return data;
  }

  async adminBanUser(userId: string): Promise<GenericResponse> {
    const { data } = await this.api.patch<GenericResponse>(`/admin/users/ban/${userId}`);
    return data;
  }

  async adminDeleteUser(userId: string): Promise<GenericResponse> {
    const { data } = await this.api.delete<GenericResponse>(`/admin/users/delete/${userId}`);
    return data;
  }
}


export const authServiceAPI = new AuthServiceAPI("/api/auth/v1");
