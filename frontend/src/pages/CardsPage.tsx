import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { cardServiceAPI } from "../api/card/cardapi";
import {
  CardOut,
  CardDetailsOut,
  CardTransactionOut,
  CardTransactionDetailsOut,
  NewCardIn,
  CardRechargeIn,
  PaymentRequestIn,
} from "../api/card/cardmodels";

import CardForm from "../components/CardForm";
import CardCarousel from "../components/CardCarousel";
import CardRechargeForm from "../components/CardRechargeForm";
import CardPaymentForm from "../components/CardPaymentForm";
import companyName from "../constants/companyName";
import TransactionModal from "../components/TransactionModal";
import TransactionsList from "../components/TransactionsList";

export default function CardPage() {
  const [cards, setCards] = useState<CardOut[]>([]);
  const [selectedCard, setSelectedCard] = useState<CardDetailsOut | null>(null);
  const [transactions, setTransactions] = useState<CardTransactionOut[]>([]);
  const [modalTx, setModalTx] = useState<CardTransactionDetailsOut | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /** Fetch all cards */
  const fetchCards = async () => {
    try {
      setLoading(true);
      const data = await cardServiceAPI.privateGetCards();
      setCards(data);
      if (data.length) await selectCard(data[0].id, false);
    } catch {
      setError("Errore nel caricamento delle carte.");
    } finally {
      setLoading(false);
    }
  };

  /** Select a card and optionally load its full details */
  const selectCard = async (cardId: string, loadDetails = true) => {
    // Cambio immediato della card selezionata
    setSelectedCard(prev => (prev?.id === cardId ? prev : { id: cardId } as CardDetailsOut));

    if (!loadDetails) return;

    try {
      setLoading(true);
      const details = await cardServiceAPI.privateGetCard(cardId);
      const txs = await cardServiceAPI.privateGetCardTransactions(cardId);
      setSelectedCard(details);
      setTransactions(txs);
    } finally {
      setLoading(false);
    }
  };

  /** Dismiss (delete) a card */
  const dismissCard = async (cardId: string) => {
    if (!confirm("Vuoi eliminare la carta?")) return;
    try {
      setLoading(true);
      await cardServiceAPI.privateDismissCard(cardId);
      await fetchCards();
    } finally {
      setLoading(false);
    }
  };

  /** Handle new card creation */
  const createCard = async (payload: NewCardIn) => {
    try {
      setLoading(true);
      await cardServiceAPI.privateNewCard(payload);
      await fetchCards();
    } finally {
      setLoading(false);
    }
  };

  /** Recharge selected card */
  const rechargeCard = async (amount: string) => {
    if (!selectedCard) return;
    try {
      setLoading(true);
      const payload: CardRechargeIn = { amount };
      await cardServiceAPI.privateRechargeCard(selectedCard.id, payload);
      await selectCard(selectedCard.id);
    } finally {
      setLoading(false);
    }
  };

  /** Make a payment from the card */
  const payFromCard = async (payload: PaymentRequestIn) => {
    if (!selectedCard) return;
    try {
      setLoading(true);
      await cardServiceAPI.privatePayment(selectedCard.id, payload);
      await selectCard(selectedCard.id);
    } finally {
      setLoading(false);
    }
  };

  /** Show transaction details */
  const showTransactionDetails = async (txId: string) => {
    if (!selectedCard) return;
    try {
      setLoading(true);
      const detail = await cardServiceAPI.privateGetTransactionDetails(selectedCard.id, txId);
      setModalTx(detail);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCards();
  }, []);

  if (error) return <p className="text-error text-center mt-10">{error}</p>;

  return (
    <div className="max-w-5xl mx-auto p-4 sm:p-6 space-y-6">
      <div className="flex justify-between items-center flex-wrap gap-3">
        <h2 className="text-2xl font-bold">💳 Le mie Carte</h2>
        <Link to="/wallet">
          <button className="btn btn-outline btn-sm">⬅ Torna al Wallet</button>
        </Link>
      </div>

      <CardCarousel
        cards={cards}
        selectedCardId={selectedCard?.id}
        onSelect={selectCard}
        onDismiss={dismissCard}
        companyName={companyName}
      />

      <CardForm onCreate={createCard} />

      {selectedCard && <CardRechargeForm onRecharge={rechargeCard} />}
      {selectedCard && <CardPaymentForm onPayment={payFromCard} />}
      {selectedCard && <TransactionsList transactions={transactions} onViewDetails={showTransactionDetails} />}

      {loading && (
        <div className="flex justify-center mt-4">
          <span className="loading loading-lg"></span>
        </div>
      )}

      {modalTx && <TransactionModal transaction={modalTx} onClose={() => setModalTx(null)}/>}
    </div>
  );
}
