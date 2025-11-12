import axios, { type AxiosInstance } from "axios";
import type {
  CardOut,
  CardDetailsOut,
  CardTransactionOut,
  CardTransactionDetailsOut,
  NewCardIn,
  CardRechargeIn,
  PaymentRequestIn,
} from "./cardmodels";
import type { AuthServiceAPI } from "../auth/authapi";
import type { GenericResponse } from "../common/models";


class CardServiceAPI {
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

  async privateGetCards(): Promise<CardOut[]> {
    const { data } = await this.api.get<CardOut[]>("/private/cards");
    return data;
  }

  async privateGetCard(cardId: string): Promise<CardDetailsOut> {
    const { data } = await this.api.get<CardDetailsOut>(`/private/cards/${cardId}`);
    return data;
  }

  async privateGetCardTransactions(cardId: string): Promise<CardTransactionOut[]> {
    const { data } = await this.api.get<CardTransactionOut[]>(`/private/transactions/${cardId}`);
    return data;
  }

  async privateGetTransactionDetails(
    cardId: string,
    transactionId: string
  ): Promise<CardTransactionDetailsOut> {
    const { data } = await this.api.get<CardTransactionDetailsOut>(
      `/private/transactions/${cardId}/${transactionId}`
    );
    return data;
  }

  async privateNewCard(payload: NewCardIn): Promise<GenericResponse> {
    const { data } = await this.api.post<GenericResponse>("/private/new-card", payload);
    return data;
  }

  async privateRechargeCard(
    cardId: string,
    payload: CardRechargeIn
  ): Promise<GenericResponse> {
    const { data } = await this.api.post<GenericResponse>(
      `/private/recharge/${cardId}`,
      payload
    );
    return data;
  }

  async privateDismissCard(cardId: string): Promise<GenericResponse> {
    const { data } = await this.api.patch<GenericResponse>(
      `/private/dismiss/${cardId}`
    );
    return data;
  }

  async privatePayment(
    cardId: string,
    payload: PaymentRequestIn
  ): Promise<GenericResponse> {
    const { data } = await this.api.post<GenericResponse>(
      `/private/payment/${cardId}`,
      payload
    );
    return data;
  }

  async adminGetCards(): Promise<CardOut[]> {
    const { data } = await this.api.get<CardOut[]>("/admin/cards");
    return data;
  }

  async adminGetCardsByUser(userId: string): Promise<CardOut[]> {
  const { data } = await this.api.get<CardOut[]>(`/admin/card/${userId}`);
  return data;
}

  async adminGetCardDetails(cardId: string): Promise<CardDetailsOut> {
    const { data } = await this.api.get<CardDetailsOut>(`/admin/cards/${cardId}`);
    return data;
  }

  async adminGetCardTransactions(cardId: string): Promise<CardTransactionOut[]> {
    const { data } = await this.api.get<CardTransactionOut[]>(`/admin/transactions/${cardId}`);
    return data;
  }

  async adminGetTransactionDetails(
    cardId: string,
    transactionId: string
  ): Promise<CardTransactionDetailsOut> {
    const { data } = await this.api.get<CardTransactionDetailsOut>(
      `/admin/transactions/${cardId}/${transactionId}`
    );
    return data;
  }

  async adminBlockCard(cardId: string): Promise<GenericResponse> {
    const { data } = await this.api.patch<GenericResponse>(`/admin/block/${cardId}`);
    return data;
  }

  async adminUnblockCard(cardId: string): Promise<GenericResponse> {
    const { data } = await this.api.patch<GenericResponse>(`/admin/unblock/${cardId}`);
    return data;
  }
}

import { authServiceAPI } from "../auth/authapi";
export const cardServiceAPI = new CardServiceAPI("/api/card/v1", authServiceAPI);
