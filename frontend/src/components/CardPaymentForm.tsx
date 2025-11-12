import { useState } from "react";
import { CardTransactionType, PaymentRequestIn } from "../api/card/cardmodels";

interface CardPaymentProps {
  onPayment: (payload: PaymentRequestIn) => void;
}

export default function CardPayment({ onPayment }: CardPaymentProps) {
  const [amount, setAmount] = useState("");
  const [counterparty, setCounterparty] = useState("");
  const [description, setDescription] = useState("");
  const [type, setType] = useState<CardTransactionType>(CardTransactionType.CARD_TO_CARD);

  const handleSubmit = () => {
    if (!amount || !counterparty) return;
    onPayment({ amount, counterparty_instrument_id: counterparty, transaction_type: type, description });
    setAmount(""); setCounterparty(""); setDescription("");
  };

  return (
    <div className="card bg-base-100 shadow p-4">
      <h3 className="card-title">Pagamento</h3>
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-2 mt-2">
        <select className="select select-bordered" value={type} onChange={e => setType(e.target.value as CardTransactionType)}>
          <option value={CardTransactionType.CARD_TO_CARD}>Card → Card</option>
          <option value={CardTransactionType.CARD_TO_WALLET}>Card → Wallet</option>
        </select>
        <input type="text" placeholder={type === CardTransactionType.CARD_TO_CARD ? "ID Carta" : "ID Wallet"} className="input input-bordered" value={counterparty} onChange={e => setCounterparty(e.target.value)} />
        <input type="text" placeholder="Importo" className="input input-bordered" value={amount} onChange={e => setAmount(e.target.value)} />
        <input type="text" placeholder="Descrizione" className="input input-bordered" value={description} onChange={e => setDescription(e.target.value)} />
      </div>
      <button className="btn btn-accent mt-3" onClick={handleSubmit}>Invia pagamento</button>
    </div>
  );
}