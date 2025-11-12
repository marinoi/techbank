import { useState } from "react";
import { authServiceAPI } from "../api/auth/authapi";
import { cardServiceAPI } from "../api/card/cardapi";
import { notificationServiceAPI } from "../api/notification/notificationapi";
import { walletServiceAPI } from "../api/wallet/walletapi";

type MethodStats = { total: number; success: number; error: number; avgTime: number };
type ServiceMethod = { serviceName: string; methodName: string; fn: () => Promise<any>; skip?: boolean };

export default function AdminApiPage() {
  const [stats, setStats] = useState<Record<string, MethodStats>>({});
  const [running, setRunning] = useState(false);
  const [repetitions, setRepetitions] = useState(5);

  const runTest = async () => {
    setRunning(true);
    const newStats: Record<string, MethodStats> = {};

    try {
      const users = await authServiceAPI.adminGetUsers();
      const firstUser = users.find(u => u.role === "user");
      if (!firstUser) console.warn("Nessun utente di tipo 'user' trovato");
      const firstUserId = firstUser?.id;

      const cards = await cardServiceAPI.adminGetCards();
      const firstCardId = cards[0]?.id;
      if (!firstCardId) console.warn("Nessuna carta trovata");

      const wallets = await walletServiceAPI.adminGetAllWallets();
      const firstWalletId = wallets[0]?.id;
      if (!firstWalletId) console.warn("Nessun wallet trovato");

      const notifications = firstUserId ? await notificationServiceAPI.adminGetUserNotifications(firstUserId) : [];
      const firstNotificationId = notifications[0]?.id;
      if (firstUserId && !firstNotificationId) console.warn("Nessuna notifica per il primo utente");

      const walletTransactions = firstWalletId ? await walletServiceAPI.adminGetWalletTransactions(firstWalletId) : [];
      const firstWalletTransactionId = walletTransactions[0]?.id;
      if (firstWalletId && !firstWalletTransactionId) console.warn("Nessuna transazione wallet trovata");

      const cardTransactions = firstCardId ? await cardServiceAPI.adminGetCardTransactions(firstCardId) : [];
      const firstCardTransactionId = cardTransactions[0]?.id;
      if (firstCardId && !firstCardTransactionId) console.warn("Nessuna transazione carta trovata");

      const methods: ServiceMethod[] = [
        { serviceName: "Auth", methodName: "adminGetUsers", fn: () => authServiceAPI.adminGetUsers() },
        { serviceName: "Auth", methodName: "adminGetUser", fn: () => firstUserId ? authServiceAPI.adminGetUser(firstUserId) : Promise.resolve({}), skip: !firstUserId },
        { serviceName: "Card", methodName: "adminGetCards", fn: () => cardServiceAPI.adminGetCards() },
        { serviceName: "Card", methodName: "adminGetCardsByUser", fn: () => firstUserId ? cardServiceAPI.adminGetCardsByUser(firstUserId) : Promise.resolve([]), skip: !firstUserId },
        { serviceName: "Card", methodName: "adminGetCardDetails", fn: () => firstCardId ? cardServiceAPI.adminGetCardDetails(firstCardId) : Promise.resolve({}), skip: !firstCardId },
        { serviceName: "Card", methodName: "adminGetCardTransactions", fn: () => firstCardId ? cardServiceAPI.adminGetCardTransactions(firstCardId) : Promise.resolve([]), skip: !firstCardId },
        { serviceName: "Card", methodName: "adminGetTransactionDetails", fn: () => firstCardId && firstCardTransactionId ? cardServiceAPI.adminGetTransactionDetails(firstCardId, firstCardTransactionId) : Promise.resolve({}), skip: !firstCardId || !firstCardTransactionId },
        { serviceName: "Notification", methodName: "adminGetUserNotifications", fn: () => firstUserId ? notificationServiceAPI.adminGetUserNotifications(firstUserId) : Promise.resolve([]), skip: !firstUserId },
        { serviceName: "Notification", methodName: "adminGetUserNotificationDetails", fn: () => firstUserId && firstNotificationId ? notificationServiceAPI.adminGetUserNotificationDetails(firstUserId, firstNotificationId) : Promise.resolve({}), skip: !firstUserId || !firstNotificationId },
        { serviceName: "Wallet", methodName: "adminGetAllWallets", fn: () => walletServiceAPI.adminGetAllWallets() },
        { serviceName: "Wallet", methodName: "adminGetWalletByUser", fn: () => firstUserId ? walletServiceAPI.adminGetWalletByUser(firstUserId) : Promise.resolve({}), skip: !firstUserId },
        { serviceName: "Wallet", methodName: "adminGetWalletDetails", fn: () => firstWalletId ? walletServiceAPI.adminGetWalletDetails(firstWalletId) : Promise.resolve({}), skip: !firstWalletId },
        { serviceName: "Wallet", methodName: "adminGetWalletTransactions", fn: () => firstWalletId ? walletServiceAPI.adminGetWalletTransactions(firstWalletId) : Promise.resolve([]), skip: !firstWalletId },
        { serviceName: "Wallet", methodName: "adminGetTransactionDetails", fn: () => firstWalletId && firstWalletTransactionId ? walletServiceAPI.adminGetTransactionDetails(firstWalletId, firstWalletTransactionId) : Promise.resolve({}), skip: !firstWalletId || !firstWalletTransactionId },
      ];

      for (const method of methods) {
        if (method.skip) {
          console.warn(`Skipping ${method.serviceName}.${method.methodName} perché la risorsa non esiste`);
          newStats[`${method.serviceName}.${method.methodName}`] = { total: 0, success: 0, error: 0, avgTime: 0 };
          setStats({ ...newStats });
          continue;
        }

        let total = 0, success = 0, error = 0, timeSum = 0;
        for (let i = 0; i < repetitions; i++) {
          const start = performance.now();
          total++;
          try { await method.fn(); success++; } 
          catch (e) { error++; console.error(`Errore ${method.serviceName}.${method.methodName}:`, e); }
          finally { timeSum += performance.now() - start; }
        }
        newStats[`${method.serviceName}.${method.methodName}`] = { total, success, error, avgTime: total ? timeSum / total : 0 };
        setStats({ ...newStats });
      }
    } catch (err) {
      console.error("Errore nel test:", err);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 font-sans max-w-full overflow-x-auto">
      <h1 className="text-2xl mb-4">Admin API Test</h1>
      <div className="flex flex-col sm:flex-row sm:items-center gap-4 mb-4">
        <label className="flex items-center gap-2">
          Numero richieste per metodo:
          <input type="number" value={repetitions} min={1} onChange={e => setRepetitions(Number(e.target.value))} className="input input-bordered w-20" />
        </label>
        <button onClick={runTest} disabled={running} className="btn btn-primary">{running ? "Running..." : "Inizia Test"}</button>
      </div>
      <div className="overflow-x-auto">
        <table className="table table-zebra w-full min-w-[700px]">
          <thead>
            <tr><th>Metodo</th><th>Totale</th><th>Successi</th><th>Errori</th><th>% Successo</th><th>Tempo Medio (ms)</th></tr>
          </thead>
          <tbody>
            {Object.entries(stats).map(([method, s]) => {
              const successPct = s.total ? ((s.success / s.total) * 100).toFixed(1) : "0.0";
              return (
                <tr key={method}>
                  <td>{method}</td>
                  <td>{s.total}</td>
                  <td className="text-green-600">{s.success}</td>
                  <td className="text-red-600">{s.error}</td>
                  <td className="w-32">
                    <div className="w-full bg-gray-200 rounded h-4 mb-1">
                      <div className="bg-green-500 h-4 rounded transition-all" style={{ width: `${successPct}%` }}></div>
                    </div>{successPct}%
                  </td>
                  <td>{s.avgTime.toFixed(2)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
