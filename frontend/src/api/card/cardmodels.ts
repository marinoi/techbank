import { UUID } from "../common/types";

export enum CardTransactionDirection {
  TRANSFER_IN = "transfer-in",
  TRANSFER_OUT = "transfer-out",
}

export enum CardTransactionType {
  CARD_RECHARGE = "card-recharge",
  CARD_REFUND = "card-refund",
  CARD_TO_WALLET = "card-to-wallet",
  WALLET_TO_CARD = "wallet-to-card",
  CARD_TO_CARD = "card-to-card",
}

export enum CardUsagePolicy {
  STANDARD = "card-standard-policy",
  AMOUNT_LIMITED = "card-amount-limited-policy",
}


export interface CardOut {
  id: UUID;
  user_id: UUID;
  amount: string; 
  is_active: boolean;
}

export interface CardDetailsOut extends CardOut {
  policy: CardUsagePolicy[];
  amount_limit?: string;
  created_at: string;
  updated_at: string; 
}

export interface NewCardIn {
  amount?: string; 
  policy?: CardUsagePolicy[]; 
  amount_limit?: string | null;
}

export interface CardRechargeIn {
  amount: string;
}

export interface CardTransactionOut {
  id: UUID;
  created_at: string;
  amount: string;
  direction: CardTransactionDirection;
}

export interface CardTransactionDetailsOut extends CardTransactionOut {
  card_id: UUID;
  counterparty_instrument_id: UUID;
  counterparty_name: string;
  counterparty_surname: string;
  type: CardTransactionType;
  description?: string | null;
}

export interface PaymentRequestIn {
  amount: string;
  counterparty_instrument_id: UUID;
  transaction_type: CardTransactionType;
  description: string;
}

