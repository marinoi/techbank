import axios, { type AxiosInstance } from "axios";
import type {
  NotificationOut,
  NotificationDetailsOut,
} from "./notificationmodels";
import type { AuthServiceAPI } from "../auth/authapi";

class NotificationServiceAPI {
  private api: AxiosInstance;
  private authService: AuthServiceAPI;

  constructor(baseURL: string, authService: AuthServiceAPI) {
    this.authService = authService;
    this.api = axios.create({
      baseURL,
      headers: { "Content-Type": "application/json" },
      withCredentials: true,
    });

    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        if (
          error.response?.status === 401 &&
          !originalRequest._retry &&
          this.authService.isLoggedIn
        ) {
          originalRequest._retry = true;
          await this.authService.publicRefreshToken();
          return this.api(originalRequest);
        }
        return Promise.reject(error);
      }
    );
  }

  async privateGetNotifications(): Promise<NotificationOut[]> {
    const { data } = await this.api.get<NotificationOut[]>("/private/notifications");
    return data;
  }

  async privateGetNotification(notificationId: string): Promise<NotificationDetailsOut> {
    const { data } = await this.api.get<NotificationDetailsOut>(
      `/private/notifications/${notificationId}`
    );
    return data;
  }

  async adminGetUserNotifications(userId: string): Promise<NotificationOut[]> {
    const { data } = await this.api.get<NotificationOut[]>(`/admin/notifications/${userId}`);
    return data;
  }

  async adminGetUserNotificationDetails(
    userId: string,
    notificationId: string
  ): Promise<NotificationDetailsOut> {
    const { data } = await this.api.get<NotificationDetailsOut>(
      `/admin/notifications/${userId}/${notificationId}`
    );
    return data;
  }
}

import { authServiceAPI } from "../auth/authapi";
export const notificationServiceAPI = new NotificationServiceAPI("/api/notification/v1", authServiceAPI);
