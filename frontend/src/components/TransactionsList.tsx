import { WalletTransactionOut } from "../api/wallet/walletmodels";
import { CardTransactionOut } from "../api/card/cardmodels";

type Transaction = WalletTransactionOut | CardTransactionOut;

interface TransactionsListProps {
  transactions: Transaction[];
  onViewDetails: (id: string) => Promise<void>;
}

function isWalletTransaction(tx: Transaction): tx is WalletTransactionOut {
  return "direction" in tx && typeof tx.amount === "number";
}

export default function TransactionsList({ transactions, onViewDetails }: TransactionsListProps) {
  if (!transactions.length) {
    return (
      <div className="card bg-base-200 shadow-md p-4">
        <h2 className="card-title">Transazioni</h2>
        <p className="text-sm text-gray-500 mt-2">Nessuna transazione disponibile.</p>
      </div>
    );
  }

  return (
    <div className="card bg-base-200 shadow-md p-4">
      <h2 className="card-title mb-3">Transazioni</h2>
      <div className="grid gap-3 grid-cols-1">
        {[...transactions].reverse().map(tx => {
          const isWallet = isWalletTransaction(tx);
          const direction = tx.direction;
          const amountSign = direction === "transfer-in" ? "+" : "-";
          const amount = isWallet ? tx.amount : tx.amount;

          return (
            <div
              key={tx.id}
              onClick={() => onViewDetails(tx.id)}
              className="card bg-base-100 shadow hover:shadow-lg transition cursor-pointer"
            >
              <div className="card-body p-4 space-y-1">
                <div className="flex justify-between items-start">
                  <p className="font-mono text-xs text-gray-500 truncate max-w-[70%]">{tx.id}</p>
                  <span className={`badge ${direction === "transfer-in" ? "badge-success" : "badge-error"}`}></span>
                </div>

                <p className="text-lg font-semibold">
                  {amountSign} € {amount}
                </p>

                <p className="text-xs text-gray-400">{new Date(tx.created_at).toLocaleString()}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
