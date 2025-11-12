import { useState } from "react";


export default function WalletDeposit({ onDeposit }: { onDeposit: (amount: string) => Promise<void> }) {
  const [depositAmount, setDepositAmount] = useState("");
  const [depositError, setDepositError] = useState<string | null>(null);

  const handleDeposit = async () => {
    setDepositError(null);
    if (!depositAmount || isNaN(Number(depositAmount)) || Number(depositAmount) <= 0) return setDepositError("Importo non valido.");
    try {
      await onDeposit(depositAmount);
      setDepositAmount("");
    } catch {
      setDepositError("Deposito fallito.");
    }
  };

  return (
    <div className="card bg-base-100 shadow-lg p-4">
      <h2 className="card-title">Deposito</h2>
      <div className="flex flex-wrap gap-3 mt-2">
        <input type="text" placeholder="Importo" value={depositAmount} onChange={e => setDepositAmount(e.target.value)} className="input input-bordered flex-1"/>
        <button className="btn btn-primary" onClick={handleDeposit}>Deposita</button>
      </div>
      {depositError && <p className="text-error mt-2">{depositError}</p>}
    </div>
  );
}
