import { WalletTransactionDetailsOut } from "../api/wallet/walletmodels";
import { CardTransactionDetailsOut } from "../api/card/cardmodels";

type Transaction = WalletTransactionDetailsOut | CardTransactionDetailsOut;

interface TransactionModalProps {
  transaction: Transaction;
  onClose: () => void;
}

function isWalletTransaction(tx: Transaction): tx is WalletTransactionDetailsOut {
  return "wallet_id" in tx && tx.wallet_id !== undefined;
}

export default function TransactionModal({ transaction, onClose }: TransactionModalProps) {
  const walletTx = isWalletTransaction(transaction);

  return (
    <div className="modal modal-open">
      <div className="modal-box relative max-w-lg">
        <h3 className="text-lg font-bold mb-4">Dettagli Transazione</h3>
        <button 
          className="btn btn-sm btn-circle absolute right-2 top-2" 
          onClick={onClose}
        >
          ✕
        </button>

        <div className="space-y-2 text-sm">
          <p><strong>ID:</strong> {transaction.id}</p>

          {walletTx ? (
            <p><strong>Wallet ID:</strong> {transaction.wallet_id}</p>
          ) : (
            <p><strong>Card ID:</strong> {(transaction as CardTransactionDetailsOut).card_id}</p>
          )}

          <p>
            <strong>Controparte:</strong> {transaction.counterparty_name} {transaction.counterparty_surname}
          </p>
          <p><strong>Strumento:</strong> {transaction.counterparty_instrument_id}</p>
          <p><strong>Importo:</strong> € {transaction.amount}</p>
          <p><strong>Tipo:</strong> {transaction.type}</p>
          <p><strong>Direzione:</strong> {transaction.direction}</p>
          <p><strong>Descrizione:</strong> {transaction.description || "-"}</p>
          <p><strong>Data:</strong> {new Date(transaction.created_at).toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
}
