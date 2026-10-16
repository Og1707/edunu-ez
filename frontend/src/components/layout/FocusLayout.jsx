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
  const [childFocus, setChildFocus] = useState({ progress: 0, status: 'Actividad en curso', score: null, remainingTime: null, backLabel: 'Volver', exitPath: null, exitTitle: '¿Salir de la actividad?', exitDescription: 'Tu progreso podría no guardarse si sales ahora.' });
  const navigate = useNavigate();
  const shownProgress = progress ?? childFocus.progress;
  const shownStatus = status !== 'Actividad en curso' ? status : childFocus.status;
  const shownScore = score ?? childFocus.score;
  const shownRemainingTime = remainingTime ?? childFocus.remainingTime;

  const leave = () => {
    setConfirmExit(false);
    if (onExit) onExit();
    else if (childFocus.exitPath) navigate(childFocus.exitPath);
    else navigate(-1);
  };
  const requestExit = () => setConfirmExit(true);

  return (
    <div className="focus-layout">
      <header className="focus-layout__header">
        <button className="focus-layout__back" type="button" onClick={requestExit}>
          <ArrowLeft size={18} aria-hidden="true" />
          <span>{childFocus.backLabel}</span>
        </button>
        <div className="focus-layout__progress" aria-label={`Progreso: ${shownProgress}%`}>
          <span>{shownStatus}</span>
          <div className="focus-layout__progress-track" role="progressbar" aria-valuenow={shownProgress} aria-valuemin="0" aria-valuemax="100">
            <span style={{ width: `${Math.min(100, Math.max(0, shownProgress))}%` }} />
          </div>
        </div>
        <div className="focus-layout__meta" aria-live="polite">
          {shownRemainingTime != null && <span>{shownRemainingTime}</span>}
          {shownScore != null && <span>{shownScore} puntos</span>}
          {shownRemainingTime == null && shownScore == null && <span>En curso</span>}
        </div>
      </header>
      <main className="focus-layout__content"><Outlet context={{ setFocus: setChildFocus, requestExit }} /></main>

      {confirmExit && (
        <div className="focus-confirm__backdrop">
          <section className="focus-confirm" role="alertdialog" aria-modal="true" aria-labelledby="focus-confirm-title" aria-describedby="focus-confirm-description">
            <h2 id="focus-confirm-title">{childFocus.exitTitle}</h2>
            <p id="focus-confirm-description">{childFocus.exitDescription}</p>
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
