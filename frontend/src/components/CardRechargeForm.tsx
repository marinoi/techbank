import { useState } from "react";

interface CardRechargeFormProps {
  onRecharge: (amount: string) => void;
}

export default function CardRecharge({ onRecharge }: CardRechargeFormProps) {
  const [amount, setAmount] = useState("");
  return (
    <div className="card bg-base-100 shadow p-4">
      <h3 className="card-title">Ricarica carta</h3>
      <div className="flex flex-wrap gap-3 mt-2">
        <input type="text" placeholder="Importo" className="input input-bordered flex-1" value={amount} onChange={e => setAmount(e.target.value)} />
        <button className="btn btn-primary" onClick={() => { onRecharge(amount); setAmount(""); }}>Ricarica</button>
      </div>
    </div>
  );
}