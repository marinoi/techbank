import type { WalletDetailsOut } from "../api/wallet/walletmodels";

interface AdminUserWalletProps {
  wallet: WalletDetailsOut;
  onBlock: () => void;
  onUnblock: () => void;
}

export default function AdminUserWallet({ wallet, onBlock, onUnblock }: AdminUserWalletProps) {
  return (
    <div className="card bg-base-100 shadow-lg border border-base-300 max-w-5xl mx-auto my-6 rounded-lg">
      <div className="card-body p-6">
        <h2 className="text-2xl font-semibold text-center mb-6">Wallet dell’utente</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-base">
          <div className="space-y-2">
            <p><span className="font-semibold">ID Wallet:</span> {wallet.id}</p>
            <p><span className="font-semibold">Saldo:</span> {wallet.amount} €</p>
            <p>
              <span className="font-semibold">Stato:</span>{" "}
              <span className={`badge ${wallet.is_active ? "badge-success" : "badge-error"}`}>
                {wallet.is_active ? "Attivo" : "Bloccato"}
              </span>
            </p>
          </div>

          <div className="space-y-2">
            <p><span className="font-semibold">Creato il:</span> {new Date(wallet.created_at).toLocaleString()}</p>
            <p><span className="font-semibold">Ultimo aggiornamento:</span> {new Date(wallet.updated_at).toLocaleString()}</p>
          </div>
        </div>

        <div className="mt-6 flex flex-col sm:flex-row gap-4">
          {wallet.is_active ? (
            <button onClick={onBlock} className="btn btn-error w-full sm:w-auto">Blocca Wallet</button>
          ) : (
            <button onClick={onUnblock} className="btn btn-success w-full sm:w-auto">Sblocca Wallet</button>
          )}
        </div>
      </div>
    </div>
  );
}
