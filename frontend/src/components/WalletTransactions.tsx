import { WalletTransactionOut } from "../api/wallet/walletmodels";

export default function WalletTransactions({
  transactions,
  onViewDetails,
}: {
  transactions: WalletTransactionOut[];
  onViewDetails: (id: string) => Promise<void>;
}) {
  if (!transactions.length)
    return (
      <div className="card bg-base-200 shadow-md p-4">
        <h2 className="card-title">Transazioni</h2>
        <p className="text-sm text-gray-500 mt-2">Nessuna transazione disponibile.</p>
      </div>
    );

  return (
    <div className="card bg-base-200 shadow-md p-4">
      <h2 className="card-title mb-3">Transazioni</h2>
      <div className="grid gap-3 grid-cols-1">
        {[...transactions].reverse().map(t => (
          <div
            key={t.id}
            onClick={() => onViewDetails(t.id)}
            className="card bg-base-100 shadow hover:shadow-lg transition cursor-pointer"
          >
            <div className="card-body p-4 space-y-1">
              <div className="flex justify-between items-start">
                <p className="font-mono text-xs text-gray-500 truncate max-w-[70%]">{t.id}</p>
                <span className={`badge ${t.direction === "transfer-in" ? "badge-success" : "badge-error"}`}></span>
              </div>
              <p className="text-lg font-semibold">{t.direction === "transfer-in" ? "+" : "-"} € {t.amount}</p>
              <p className="text-xs text-gray-500">{new Date(t.created_at).toLocaleString()}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
