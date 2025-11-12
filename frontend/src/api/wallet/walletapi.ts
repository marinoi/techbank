import axios, { type AxiosInstance } from "axios";
import type {
  WalletDetailsOut,
  WalletTransactionOut,
  WalletTransactionDetailsOut,
  DepositIn,
  PaymentRequestIn,
  WalletOut,
} from "./walletmodels";
import type { AuthServiceAPI } from "../auth/authapi";
import type { GenericResponse } from "../common/models";


class WalletServiceAPI {
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
      response => response,
      async error => {
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

  async privateGetWallet(): Promise<WalletDetailsOut> {
    const { data } = await this.api.get<WalletDetailsOut>("/private/wallet");
    return data;
  }

  async privateGetTransactions(): Promise<WalletTransactionOut[]> {
    const { data } = await this.api.get<WalletTransactionOut[]>("/private/transactions");
    return data;
  }

  async privateGetTransaction(transactionId: string): Promise<WalletTransactionDetailsOut> {
    const { data } = await this.api.get<WalletTransactionDetailsOut>(`/private/transactions/${transactionId}`);
    return data;
  }

  async privateDeposit(payload: DepositIn): Promise<GenericResponse> {
    const { data } = await this.api.post<GenericResponse>("/private/deposit", payload);
    return data;
  }

  async privatePayment(payload: PaymentRequestIn): Promise<GenericResponse> {
    const { data } = await this.api.post<GenericResponse>("/private/payment", payload);
    return data;
  }

  async adminGetAllWallets(): Promise<WalletOut[]> {
    const { data } = await this.api.get<WalletOut[]>("/admin/wallets");
    return data;
  }

  async adminGetWalletByUser(userId: string): Promise<WalletOut> {
    const { data } = await this.api.get<WalletOut>(`/admin/wallet/${userId}`);
    return data;
  }
  
  async adminGetWalletDetails(walletId: string): Promise<WalletDetailsOut> {
    const { data } = await this.api.get<WalletDetailsOut>(`/admin/wallets/${walletId}`);
    return data;
  }

  async adminGetWalletTransactions(walletId: string): Promise<WalletTransactionOut[]> {
    const { data } = await this.api.get<WalletTransactionOut[]>(`/admin/transactions/${walletId}`);
    return data;
  }

  async adminGetTransactionDetails(walletId: string, transactionId: string): Promise<WalletTransactionDetailsOut> {
    const { data } = await this.api.get<WalletTransactionDetailsOut>(`/admin/transactions/${walletId}/${transactionId}`);
    return data;
  }

  async adminBlockWallet(walletId: string): Promise<GenericResponse> {
    const { data } = await this.api.patch<GenericResponse>(`/admin/block/${walletId}`);
    return data;
  }

  async adminUnblockWallet(walletId: string): Promise<GenericResponse> {
    const { data } = await this.api.patch<GenericResponse>(`/admin/unblock/${walletId}`);
    return data;
  }
}

import { authServiceAPI } from "../auth/authapi";
export const walletServiceAPI = new WalletServiceAPI("/api/wallet/v1", authServiceAPI);
