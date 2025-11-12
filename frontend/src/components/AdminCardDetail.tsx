import type { CardDetailsOut } from "../api/card/cardmodels";

interface AdminCardDetailProps {
  card: CardDetailsOut | null;
  onBlockCard: (cardId: string) => void;
  onUnblockCard: (cardId: string) => void;
}

export default function AdminCardDetail({ card, onBlockCard, onUnblockCard }: AdminCardDetailProps) {
  if (!card) return <div className="alert alert-info max-w-5xl mx-auto my-4 text-center text-sm">Seleziona una carta per vedere i dettagli.</div>;

  return (
    <div className="card bg-base-100 shadow-lg border border-base-300 max-w-5xl mx-auto my-6 rounded-lg">
      <div className="card-body p-6">
        <h3 className="text-2xl font-semibold text-center mb-6">Dettagli Carta</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-base">
          <div className="space-y-2">
            <p><strong>ID Carta:</strong> {card.id}</p>
            <p><strong>Utente:</strong> {card.user_id}</p>
            <p><strong>Saldo:</strong> {card.amount} €</p>
            <p>
              <strong>Stato:</strong>{" "}
              <span className={`badge ${card.is_active ? "badge-success" : "badge-error"}`}>
                {card.is_active ? "Attiva" : "Bloccata"}
              </span>
            </p>
          </div>

          <div className="space-y-2">
            <p><strong>Policy:</strong> {card.policy.map(p => p.replace("card-", "").replace("-", " ")).join(", ")}</p>
            <p><strong>Limite carta:</strong> {card.amount_limit ?? "-"}</p>
            <p><strong>Creata il:</strong> {new Date(card.created_at).toLocaleString()}</p>
            <p><strong>Aggiornata il:</strong> {new Date(card.updated_at).toLocaleString()}</p>
          </div>
        </div>

        <div className="mt-6 flex flex-col sm:flex-row gap-4">
          {card.is_active ? (
            <button className="btn btn-error w-full sm:w-auto" onClick={() => onBlockCard(card.id)}>Blocca Carta</button>
          ) : (
            <button className="btn btn-success w-full sm:w-auto" onClick={() => onUnblockCard(card.id)}>Sblocca Carta</button>
          )}
        </div>
      </div>
    </div>
  );
}
