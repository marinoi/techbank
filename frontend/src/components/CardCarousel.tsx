import { CardOut } from "../api/card/cardmodels";

interface CardCarouselProps {
  cards: CardOut[];
  selectedCardId?: string;
  onSelect: (id: string) => void;
  onDismiss: (id: string) => void;
  companyName?: string;
}

export default function CardCarousel({ cards, selectedCardId, onSelect, onDismiss, companyName = "" }: CardCarouselProps) {
  return (
    <div className="overflow-x-auto flex gap-4 py-6 px-2 snap-x snap-mandatory scrollbar-thin">
      {cards.map(card => {
        const isSelected = selectedCardId === card.id;
        const isActive = card.is_active;

        return (
          <div
            key={card.id}
            onClick={() => onSelect(card.id)}
            className={`
              relative w-72 h-44 flex-shrink-0 snap-center rounded-2xl shadow-md cursor-pointer
              transition-transform duration-300 hover:scale-105
              ${isSelected ? "bg-gradient-to-br from-gray-800 via-gray-700 to-gray-900 text-white shadow-lg" : "bg-gray-100 text-gray-800"}
              ${!isActive ? "opacity-50 pointer-events-none" : ""}
            `}
          >
            <div className="flex flex-col justify-between h-full p-4">
              <div className="flex justify-between items-center">
                <div className="w-10 h-7 bg-yellow-300 rounded-sm shadow-sm"></div>
                <div className="text-xs font-semibold tracking-wide opacity-80">{companyName.toUpperCase()}</div>
              </div>
              <div className="text-sm tracking-widest break-all mt-2">{card.id}</div>
              <div className="flex justify-between items-end mt-4">
                <div>
                  <p className="text-lg font-bold">€ {card.amount}</p>
                  <p className="text-xs opacity-70">{isActive ? "Attiva ✅" : "Non attiva ❌"}</p>
                </div>
                <button
                  className="btn btn-error btn-xs"
                  onClick={e => { e.stopPropagation(); onDismiss(card.id); }}
                >
                  Elimina
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
