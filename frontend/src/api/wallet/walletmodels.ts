import type { UUID } from "../common/types";


export enum WalletTransactionDirection {
  TRANSFER_IN = "transfer-in",
  TRANSFER_OUT = "transfer-out",
}

export enum WalletTransactionType {
  DEPOSIT = "deposit",
  CARD_RECHARGE = "card-recharge",
  CARD_REFUND = "card-refund",
  CARD_TO_WALLET = "card-to-wallet",
  WALLET_TO_CARD = "wallet-to-card",
  WALLET_TO_WALLET = "wallet-to-wallet",
}

export interface WalletOut {
  id: UUID;
  user_id: UUID;
  amount: number;
}

export interface WalletDetailsOut extends WalletOut {
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WalletTransactionOut {
  id: UUID;
  counterparty_instrument_id: UUID;
  amount: number;
  direction: WalletTransactionDirection;
  created_at: string;
}

export interface WalletTransactionDetailsOut extends WalletTransactionOut {
  wallet_id: UUID;
  counterparty_name: string;
  counterparty_surname: string;
  type: WalletTransactionType;
  description?: string;
}

export interface DepositIn {
  amount: string;
}

export interface PaymentRequestIn {
  amount: string;
  counterparty_instrument_id: UUID;
  transaction_type: WalletTransactionType;
  description: string;
}
