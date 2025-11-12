import { useState, useMemo } from "react";
import type { WalletTransactionOut } from "../api/wallet/walletmodels";
import type { CardTransactionOut } from "../api/card/cardmodels";

interface AdminTransactionsTableProps {
  transactions: WalletTransactionOut[] | CardTransactionOut[];
  type: "wallet" | "card";
  onSelectTransaction: (id: string) => void;
}

export default function AdminTransactionsTable({ transactions, type, onSelectTransaction }: AdminTransactionsTableProps) {
  const [search, setSearch] = useState("");

  const filteredTransactions = useMemo(() => {
    if (!search) return transactions;
    const lowerSearch = search.toLowerCase();
    return transactions.filter(tx =>
      tx.id.toLowerCase().includes(lowerSearch) ||
      tx.direction.toLowerCase().includes(lowerSearch) ||
      tx.amount.toString().includes(lowerSearch)
    );
  }, [search, transactions]);

  return (
    <div className="card bg-base-100 shadow-lg overflow-hidden">
      <div className="card-body p-4">
        <h2 className="text-lg font-semibold mb-2 text-center">
          Transazioni {type === "wallet" ? "Wallet" : "Carta"}
        </h2>

        <input
          type="text"
          placeholder="Cerca per ID, direzione o importo..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="input input-bordered w-full mb-4"
        />

        <div className="overflow-x-auto max-h-[400px]">
          <table className="table table-zebra w-full min-w-[600px]">
            <thead>
              <tr className="text-sm text-base-content/70">
                <th>ID</th>
                <th>Data</th>
                <th>Importo</th>
                <th>Direzione</th>
              </tr>
            </thead>
            <tbody>
              {filteredTransactions.length === 0 ? (
                <tr>
                  <td colSpan={4} className="text-center text-sm text-base-content/60">
                    Nessuna transazione trovata
                  </td>
                </tr>
              ) : (
                filteredTransactions.map(tx => (
                  <tr
                    key={tx.id}
                    onClick={() => onSelectTransaction(tx.id)}
                    className="cursor-pointer hover:bg-base-200 transition"
                  >
                    <td className="text-xs font-mono truncate max-w-[100px]" title={tx.id}>{tx.id}</td>
                    <td>{new Date(tx.created_at).toLocaleString()}</td>
                    <td className={tx.direction === "transfer-in" ? "text-success" : "text-error"}>
                      {tx.direction === "transfer-in" ? "+" : "-"} {tx.amount} €
                    </td>
                    <td>
                      <span className={`badge ${tx.direction === "transfer-in" ? "badge-success" : "badge-error"}`}>
                        {tx.direction.replace("transfer-", "")}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
