import React, { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import { Outlet, useNavigate } from 'react-router-dom';
import './layouts.css';

export default function FocusLayout({
  progress,
  status = 'Actividad en curso',
  remainingTime,
  score,
  onExit,
}) {
  const [confirmExit, setConfirmExit] = useState(false);
  const navigate = useNavigate();

  const leave = () => {
    setConfirmExit(false);
    if (onExit) onExit();
    else navigate(-1);
  };

  return (
    <div className="focus-layout">
      <header className="focus-layout__header">
        <button className="focus-layout__back" type="button" onClick={() => setConfirmExit(true)}>
          <ArrowLeft size={18} aria-hidden="true" />
          <span>Volver</span>
        </button>
        <div className="focus-layout__progress" aria-label={`Progreso: ${progress ?? 0}%`}>
          <span>{status}</span>
          <div className="focus-layout__progress-track" role="progressbar" aria-valuenow={progress ?? 0} aria-valuemin="0" aria-valuemax="100">
            <span style={{ width: `${Math.min(100, Math.max(0, progress ?? 0))}%` }} />
          </div>
        </div>
        <div className="focus-layout__meta" aria-live="polite">
          {remainingTime != null && <span>{remainingTime}</span>}
          {score != null && <span>{score} puntos</span>}
          {remainingTime == null && score == null && <span>En curso</span>}
        </div>
      </header>
      <main className="focus-layout__content"><Outlet /></main>

      {confirmExit && (
        <div className="focus-confirm__backdrop">
          <section className="focus-confirm" role="alertdialog" aria-modal="true" aria-labelledby="focus-confirm-title" aria-describedby="focus-confirm-description">
            <h2 id="focus-confirm-title">¿Salir de la actividad?</h2>
            <p id="focus-confirm-description">Tu progreso podría no guardarse si sales ahora.</p>
            <div className="focus-confirm__actions">
              <button type="button" className="focus-confirm__cancel" onClick={() => setConfirmExit(false)}>Seguir aquí</button>
              <button type="button" className="focus-confirm__leave" onClick={leave}>Salir</button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
