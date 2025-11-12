import { Link } from "react-router-dom";
import { WalletDetailsOut } from "../api/wallet/walletmodels";

export default function WalletSummary({ wallet }: { wallet: WalletDetailsOut }) {
  return (
    <div className="card bg-base-200 shadow-md p-4 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
      <div className="flex flex-col">
        <h2 className="text-xl font-semibold">Wallet</h2>
        <p className="text-sm text-gray-500 break-all">{wallet.id}</p>
        <p className="text-3xl font-bold mt-2 sm:mt-0">€ {wallet.amount}</p>
      </div>
      <Link to="/cards">
        <button className="btn btn-outline btn-sm sm:self-auto">Le mie carte</button>
      </Link>
    </div>
  );
}