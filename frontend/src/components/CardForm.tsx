import { useState } from "react";
import { CardUsagePolicy, NewCardIn } from "../api/card/cardmodels";

interface CardFormProps {
  onCreate: (payload: NewCardIn) => void;
}

export default function CardForm({ onCreate }: CardFormProps) {
  const [amount, setAmount] = useState("");
  const [type, setType] = useState<CardUsagePolicy>(CardUsagePolicy.STANDARD);
  const [limit, setLimit] = useState("");

  const handleSubmit = () => {
    if (!amount) return;
    const payload: NewCardIn = {
      amount,
      policy: [type],
      ...(type === CardUsagePolicy.AMOUNT_LIMITED && { amount_limit: limit }),
    };
    onCreate(payload);
    setAmount("");
    setLimit("");
    setType(CardUsagePolicy.STANDARD);
  };

  return (
    <div className="card bg-base-100 shadow p-4">
      <h3 className="card-title text-lg">Crea nuova carta</h3>
      <div className="flex flex-col sm:flex-row flex-wrap justify-between gap-3 mt-2">
        <input type="text" placeholder="Importo iniziale" className="input input-bordered" value={amount} onChange={e => setAmount(e.target.value)} />
        <select className="select select-bordered" value={type} onChange={e => setType(e.target.value as CardUsagePolicy)}>
          <option value={CardUsagePolicy.STANDARD}>Standard 💳</option>
          <option value={CardUsagePolicy.AMOUNT_LIMITED}>Amount Limited 🔒</option>
        </select>
        {type === CardUsagePolicy.AMOUNT_LIMITED && (
          <input type="text" placeholder="Limite carta" className="input input-bordered" value={limit} onChange={e => setLimit(e.target.value)} />
        )}
        <button className="btn btn-primary sm:flex-none" onClick={handleSubmit}>Crea</button>
      </div>
    </div>
  );
}