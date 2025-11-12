import { useState, useEffect } from "react";
import type { UserOutAdmin, UserDataIn } from "../api/auth/authmodels";
import type { WalletDetailsOut, WalletTransactionOut } from "../api/wallet/walletmodels";
import type { CardOut, CardDetailsOut, CardTransactionOut } from "../api/card/cardmodels";
import type { NotificationOut, NotificationDetailsOut } from "../api/notification/notificationmodels";
import type { GenericResponse } from "../api/common/models";

import { authServiceAPI } from "../api/auth/authapi";
import { walletServiceAPI } from "../api/wallet/walletapi";
import { cardServiceAPI } from "../api/card/cardapi";
import { notificationServiceAPI } from "../api/notification/notificationapi";

import AdminUsersTable from "../components/AdminUsersTable";
import AdminUserDetail from "../components/AdminUserDetail";
import AdminUserWallet from "../components/AdminUserWallet";
import AdminTransactionsTable from "../components/AdminTransactionsTable";
import TransactionModal from "../components/TransactionModal";
import AdminCardsTable from "../components/AdminCardsTable";
import AdminCardDetail from "../components/AdminCardDetail";
import AdminNotificationsTable from "../components/AdminNotificationTable";
import NotificationModal from "../components/NotificationModal";
import AdminNewUserModal from "../components/AdminNewUserModal";

export default function AdminDashboard() {
  const [users, setUsers] = useState<UserOutAdmin[]>([]);
  const [selectedUser, setSelectedUser] = useState<UserOutAdmin | null>(null);

  const [walletDetails, setWalletDetails] = useState<WalletDetailsOut | null>(null);
  const [walletTransactions, setWalletTransactions] = useState<WalletTransactionOut[]>([]);

  const [cards, setCards] = useState<CardOut[]>([]);
  const [selectedCard, setSelectedCard] = useState<CardDetailsOut | null>(null);
  const [cardTransactions, setCardTransactions] = useState<CardTransactionOut[]>([]);

  const [notifications, setNotifications] = useState<NotificationOut[]>([]);

  const [transactionModalOpen, setTransactionModalOpen] = useState(false);
  const [currentTransaction, setCurrentTransaction] = useState<any>(null);

  const [notificationModalOpen, setNotificationModalOpen] = useState(false);
  const [currentNotification, setCurrentNotification] = useState<NotificationDetailsOut | null>(null);

  const [newUserModalOpen, setNewUserModalOpen] = useState(false);

  // --- Carica lista utenti ---
  useEffect(() => {
    const fetchUsers = async () => {
      const data = await authServiceAPI.adminGetUsers();
      setUsers(data);
    };
    fetchUsers();
  }, []);

  // --- Carica dati utente selezionato ---
  useEffect(() => {
    if (!selectedUser) {
      setWalletDetails(null);
      setWalletTransactions([]);
      setCards([]);
      setSelectedCard(null);
      setCardTransactions([]);
      setNotifications([]);
      setTransactionModalOpen(false);
      setCurrentTransaction(null);
      setNotificationModalOpen(false);
      setCurrentNotification(null);
      return;
    }

    setWalletDetails(null);
    setWalletTransactions([]);
    setCards([]);
    setSelectedCard(null);
    setCardTransactions([]);
    setNotifications([]);
    setTransactionModalOpen(false);
    setCurrentTransaction(null);
    setNotificationModalOpen(false);
    setCurrentNotification(null);

    const fetchUserData = async () => {
      const userResult = await authServiceAPI.adminGetUser(selectedUser.id);
      if ('id' in userResult) {
        setSelectedUser(userResult as UserOutAdmin);
      } else {
        console.error("Errore caricamento utente:", (userResult as GenericResponse) ?? "Unknown error");
        return;
      }

      const wallet = await walletServiceAPI.adminGetWalletByUser(selectedUser.id);
      if (wallet && 'id' in wallet) {
        setWalletDetails(await walletServiceAPI.adminGetWalletDetails(wallet.id));
        setWalletTransactions(await walletServiceAPI.adminGetWalletTransactions(wallet.id));
      }

      setCards(await cardServiceAPI.adminGetCardsByUser(selectedUser.id));
      setNotifications(await notificationServiceAPI.adminGetUserNotifications(selectedUser.id));
    };

    fetchUserData();
  }, [selectedUser?.id]);

  // --- Seleziona carta ---
  const handleSelectCard = async (card: CardOut) => {
    const details = await cardServiceAPI.adminGetCardDetails(card.id);
    setSelectedCard(details);
    const transactions = await cardServiceAPI.adminGetCardTransactions(card.id);
    setCardTransactions(transactions);
  };

  // --- Funzioni utente ---
  const handleBanUser = async () => {
    if (!selectedUser) return;
    await authServiceAPI.adminBanUser(selectedUser.id);
    setUsers(users.map(u => u.id === selectedUser.id ? { ...u, is_banned: true } : u));
    setSelectedUser(prev => prev ? { ...prev, is_banned: true } : null);
  };

  const handleDeleteUser = async () => {
    if (!selectedUser) return;
    await authServiceAPI.adminDeleteUser(selectedUser.id);
    setUsers(users.filter(u => u.id !== selectedUser.id));
    setSelectedUser(null);
  };

  const handleUpdateUser = async (payload: UserDataIn) => {
    if (!selectedUser) return;
    const updated = await authServiceAPI.adminUpdateUser(selectedUser.id, payload);
    if ('id' in updated) {
      const updatedUser = updated as UserOutAdmin;
      setUsers(users.map(u => u.id === selectedUser.id ? updatedUser : u));
      setSelectedUser(updatedUser);
    } else {
      console.error("Errore aggiornamento utente:", (updated as GenericResponse) ?? "Unknown error");
    }
  };

  const handleCreateUser = async (data: UserDataIn) => {
    const created = await authServiceAPI.adminCreateUser(data);
    if ('id' in created) {
      setUsers(prev => [...prev, created as UserOutAdmin]);
    } else {
      console.error("Errore creazione utente:", (created as GenericResponse) ?? "Unknown error");
    }
  };

  // --- Blocca / Sblocca Wallet ---
  const handleBlockWallet = async (walletId: string) => {
    await walletServiceAPI.adminBlockWallet(walletId);
    setWalletDetails(prev => prev ? { ...prev, is_active: false } : null);
  };

  const handleUnblockWallet = async (walletId: string) => {
    await walletServiceAPI.adminUnblockWallet(walletId);
    setWalletDetails(prev => prev ? { ...prev, is_active: true } : null);
  };

  // --- Modali ---
  const handleOpenTransactionModal = async (transactionId: string, type: "wallet" | "card") => {
    if (!selectedUser) return;

    let details = null;
    if (type === "wallet" && walletDetails) {
      details = await walletServiceAPI.adminGetTransactionDetails(walletDetails.id, transactionId);
    } else if (type === "card" && selectedCard) {
      details = await cardServiceAPI.adminGetTransactionDetails(selectedCard.id, transactionId);
    }

    if (details) {
      setCurrentTransaction(details);
      setTransactionModalOpen(true);
    }
  };

  const handleOpenNotificationModal = async (notificationId: string) => {
    if (!selectedUser) return;
    const details = await notificationServiceAPI.adminGetUserNotificationDetails(selectedUser.id, notificationId);
    setCurrentNotification(details);
    setNotificationModalOpen(true);
  };

  return (
    <div className="max-w-5xl mx-auto p-2 sm:p-6 space-y-6">
      <div className="flex justify-end mb-2">
        <button className="btn btn-primary" onClick={() => setNewUserModalOpen(true)}>Nuovo Utente</button>
      </div>

      <AdminUsersTable users={users} onSelectUser={setSelectedUser} />

      {selectedUser && (
        <AdminUserDetail
          user={selectedUser}
          onBan={handleBanUser}
          onDelete={handleDeleteUser}
          onUpdate={handleUpdateUser}
        />
      )}

      {selectedUser && notifications.length > 0 && (
        <AdminNotificationsTable
          notifications={notifications}
          onViewNotification={handleOpenNotificationModal}
        />
      )}

      {notificationModalOpen && currentNotification && (
        <NotificationModal
          notification={currentNotification}
          onClose={() => setNotificationModalOpen(false)}
        />
      )}

      {selectedUser && walletDetails && (
        <>
          <AdminUserWallet
            wallet={walletDetails}
            onBlock={() => handleBlockWallet(walletDetails.id)}
            onUnblock={() => handleUnblockWallet(walletDetails.id)}
          />
          {walletTransactions.length > 0 && (
            <AdminTransactionsTable
              transactions={walletTransactions}
              type="wallet"
              onSelectTransaction={(id) => handleOpenTransactionModal(id, "wallet")}
            />
          )}
        </>
      )}

      {transactionModalOpen && currentTransaction && (
        <TransactionModal
          transaction={currentTransaction}
          onClose={() => setTransactionModalOpen(false)}
        />
      )}

      {selectedUser && cards.length > 0 && (
        <>
          <AdminCardsTable
            cards={cards}
            selectedCardId={selectedCard?.id || null}
            onSelectCard={handleSelectCard}
          />

          {selectedCard && (
            <>
              <AdminCardDetail
                card={selectedCard}
                onBlockCard={async (cardId) => {
                  await cardServiceAPI.adminBlockCard(cardId);
                  setSelectedCard(prev => prev ? { ...prev, is_active: false } : null);
                  setCards(prev => prev.map(c => c.id === cardId ? { ...c, is_active: false } : c));
                }}
                onUnblockCard={async (cardId) => {
                  await cardServiceAPI.adminUnblockCard(cardId);
                  setSelectedCard(prev => prev ? { ...prev, is_active: true } : null);
                  setCards(prev => prev.map(c => c.id === cardId ? { ...c, is_active: true } : c));
                }}
              />
              {cardTransactions.length > 0 && (
                <AdminTransactionsTable
                  transactions={cardTransactions}
                  type="card"
                  onSelectTransaction={(id) => handleOpenTransactionModal(id, "card")}
                />
              )}
            </>
          )}
        </>
      )}

      {newUserModalOpen && (
        <AdminNewUserModal
          onClose={() => setNewUserModalOpen(false)}
          onCreate={handleCreateUser}
        />
      )}
    </div>
  );
}
