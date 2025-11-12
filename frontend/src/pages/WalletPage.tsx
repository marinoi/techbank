import { useEffect, useState } from "react";
import { walletServiceAPI } from "../api/wallet/walletapi";
import {
  WalletDetailsOut,
  WalletTransactionOut,
  WalletTransactionDetailsOut,
} from "../api/wallet/walletmodels";
import WalletSummary from "../components/WalletSummary";
import WalletDeposit from "../components/WalletDeposit";
import WalletPayment from "../components/WalletPayment";
import TransactionModal from "../components/TransactionModal";
import TransactionsList from "../components/TransactionsList";

export default function WalletPage() {
  const [wallet, setWallet] = useState<WalletDetailsOut | null>(null);
  const [transactions, setTransactions] = useState<WalletTransactionOut[]>([]);
  const [selectedTransaction, setSelectedTransaction] = useState<WalletTransactionDetailsOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const [w, txs] = await Promise.all([
          walletServiceAPI.privateGetWallet(),
          walletServiceAPI.privateGetTransactions()
        ]);
        setWallet({ ...w, amount: w.amount});
        setTransactions(txs);
      } catch {
        setError("Errore nel caricamento del wallet.");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className="text-center mt-10 loading loading-lg"></div>;
  if (error) return <p className="text-error text-center mt-10">{error}</p>;
  if (!wallet) return <p className="text-center mt-10">Wallet non trovato.</p>;

  return (
    <div className="max-w-5xl mx-auto p-4 sm:p-6 space-y-6">
      <WalletSummary wallet={wallet} />

      <WalletDeposit onDeposit={async (amount) => {
        await walletServiceAPI.privateDeposit({ amount });
        const w = await walletServiceAPI.privateGetWallet();
        setWallet({ ...w, amount: w.amount });
        setTransactions(await walletServiceAPI.privateGetTransactions());
      }} />

      <WalletPayment onPayment={async (payment) => {
        await walletServiceAPI.privatePayment(payment);
        const w = await walletServiceAPI.privateGetWallet();
        setWallet({ ...w, amount: Number(w.amount) });
        setTransactions(await walletServiceAPI.privateGetTransactions());
      }} />

      <TransactionsList transactions={transactions} onViewDetails={async (id) => {
        setSelectedTransaction(await walletServiceAPI.privateGetTransaction(id));
      }} />

      {selectedTransaction && (
        <TransactionModal transaction={selectedTransaction} onClose={() => setSelectedTransaction(null)} />
      )}
    </div>
  );
}
