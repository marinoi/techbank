import { useState, useMemo } from "react";
import type { CardOut } from "../api/card/cardmodels";

interface AdminCardsTableProps {
  cards: CardOut[];
  selectedCardId: string | null;
  onSelectCard: (card: CardOut) => void;
}

export default function AdminCardsTable({ cards, selectedCardId, onSelectCard }: AdminCardsTableProps) {
  const [search, setSearch] = useState("");

  const filteredCards = useMemo(() => {
    if (!search) return cards;
    const lower = search.toLowerCase();
    return cards.filter(c =>
      c.id.toLowerCase().includes(lower) ||
      c.amount.toString().includes(lower) ||
      (c.is_active ? "attiva" : "bloccata").includes(lower)
    );
  }, [search, cards]);

  return (
    <div className="card bg-base-100 shadow-lg overflow-hidden">
      <div className="card-body p-4">
        <h2 className="text-lg font-semibold mb-3 text-center">Carte Utente</h2>

        <input
          type="text"
          placeholder="Cerca per ID, importo o stato..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="input input-bordered w-full mb-4"
        />

        <div className="overflow-x-auto max-h-[400px]">
          <table className="table table-zebra w-full min-w-[400px]">
            <thead>
              <tr className="text-sm text-base-content/70">
                <th>ID</th>
                <th>Saldo</th>
                <th>Stato</th>
              </tr>
            </thead>
            <tbody>
              {!filteredCards.length ? (
                <tr>
                  <td colSpan={3} className="text-center text-sm text-base-content/60">
                    Nessuna carta trovata.
                  </td>
                </tr>
              ) : (
                filteredCards.map(c => (
                  <tr
                    key={c.id}
                    onClick={() => onSelectCard(c)}
                    className={`cursor-pointer hover:bg-base-200 transition ${selectedCardId === c.id ? "bg-base-200" : ""}`}
                  >
                    <td className="font-mono text-xs truncate max-w-[150px]" title={c.id}>{c.id}</td>
                    <td>{c.amount} €</td>
                    <td>
                      <span className={`badge ${c.is_active ? "badge-success" : "badge-error"}`}>
                        {c.is_active ? "Attiva" : "Bloccata"}
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
