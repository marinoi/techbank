import { CardTransactionOut } from "../api/card/cardmodels";

interface CardTransactionsProps {
  transactions: CardTransactionOut[];
  onTxClick: (txId: string) => void;
}

export default function CardTransactions({ transactions, onTxClick }: CardTransactionsProps) {
  if (!transactions.length) return <p className="text-gray-500 mt-2">Nessuna transazione disponibile.</p>;

  return (
    <div className="card bg-base-200 shadow p-4">
      <h3 className="card-title">Transazioni carta</h3>
      <div className="overflow-x-auto hidden sm:block mt-3">
        <table className="table table-zebra w-full">
          <thead><tr><th>ID</th><th>Importo</th><th>Direzione</th><th>Data</th></tr></thead>
          <tbody>
            {transactions.map(tx => (
              <tr key={tx.id} className="cursor-pointer" onClick={() => onTxClick(tx.id)}>
                <td className="font-mono truncate max-w-[150px]">{tx.id}</td>
                <td>€ {tx.amount}</td>
                <td><span className={`badge ${tx.direction === "transfer-in" ? "badge-success" : "badge-error"}`}>{tx.direction}</span></td>
                <td>{new Date(tx.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="sm:hidden flex flex-col gap-2 mt-3">
        {transactions.map(tx => (
          <div key={tx.id} className="p-3 bg-base-100 rounded-lg shadow cursor-pointer" onClick={() => onTxClick(tx.id)}>
            <p className="font-mono text-sm break-all">{tx.id}</p>
            <p className="font-semibold">€ {tx.amount}</p>
            <p><span className={`badge ${tx.direction === "transfer-in" ? "badge-success" : "badge-error"}`}>{tx.direction}</span></p>
            <p className="text-xs text-gray-500">{new Date(tx.created_at).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
