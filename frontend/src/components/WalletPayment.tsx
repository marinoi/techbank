import { useState } from "react";
import { WalletTransactionType, PaymentRequestIn } from "../api/wallet/walletmodels";

export default function WalletPayment({ onPayment }: { onPayment: (payment: PaymentRequestIn) => Promise<void> }) {
  const initialPayment = {
    counterparty_instrument_id: "",
    amount: "",
    description: "",
    transaction_type: WalletTransactionType.WALLET_TO_WALLET,
  };

  const [payment, setPayment] = useState(initialPayment);
  const [paymentError, setPaymentError] = useState<string | null>(null);

  const handlePayment = async () => {
    setPaymentError(null);
    if (!payment.counterparty_instrument_id || !payment.amount || isNaN(Number(payment.amount)) || Number(payment.amount) <= 0)
      return setPaymentError("Compila destinatario e importo correttamente.");
    try {
      await onPayment(payment);
      setPayment(initialPayment);
    } catch {
      setPaymentError("Pagamento fallito.");
    }
  };

  return (
    <div className="card bg-base-100 shadow-lg p-4">
      <h2 className="card-title">Pagamento</h2>
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-2 mt-2">
        <select className="select select-bordered" value={payment.transaction_type} onChange={e => setPayment({ ...payment, transaction_type: e.target.value as WalletTransactionType })}>
          <option value={WalletTransactionType.WALLET_TO_WALLET}>Wallet → Wallet</option>
          <option value={WalletTransactionType.WALLET_TO_CARD}>Wallet → Card</option>
        </select>
        <input type="text" placeholder={payment.transaction_type===WalletTransactionType.WALLET_TO_WALLET?"ID Wallet destinatario":"ID Card destinatario"} value={payment.counterparty_instrument_id} onChange={e => setPayment({ ...payment, counterparty_instrument_id: e.target.value })} className="input input-bordered"/>
        <input type="text" placeholder="Importo" value={payment.amount} onChange={e => setPayment({ ...payment, amount: e.target.value })} className="input input-bordered"/>
        <input type="text" placeholder="Descrizione" value={payment.description} onChange={e => setPayment({ ...payment, description: e.target.value })} className="input input-bordered"/>
      </div>
      {paymentError && <p className="text-error mt-2">{paymentError}</p>}
      <button className="btn btn-accent mt-2" onClick={handlePayment}>Invia Pagamento</button>
    </div>
  );
}