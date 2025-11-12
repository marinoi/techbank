import { Link } from "react-router-dom";
import financeImage from "../assets/finance.jpg";

export default function HomePage() {
  return (
    <div className="hero bg-base-200 min-h-screen px-4 py-8">
      <div className="hero-content flex flex-col lg:flex-row items-center lg:items-start gap-8 lg:gap-16">
        
        <img
          src={financeImage}
          alt="Servizio finanziario"
          className="w-full sm:w-3/4 lg:w-96 rounded-lg shadow-2xl object-cover"
        />

        <div className="text-center lg:text-left max-w-lg">
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-primary">
            Il tuo wallet digitale tutto in uno
          </h1>
          <p className="py-4 sm:py-6 text-gray-700 text-base sm:text-lg leading-relaxed">
            Crea carte virtuali istantanee, effettua transazioni gratuite e gestisci 
            il tuo denaro completamente online ovunque ti trovi.
          </p>

          <div className="flex flex-col sm:flex-row justify-center lg:justify-start gap-4">
            <button className="btn btn-primary w-full sm:w-auto" onClick={() => alert("Questa pagina ancora non esiste.")}>
              Scopri di più
            </button>
            <Link to="/signin">
              <button className="btn btn-outline btn-secondary w-full sm:w-auto">
                Apri il tuo wallet
              </button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
