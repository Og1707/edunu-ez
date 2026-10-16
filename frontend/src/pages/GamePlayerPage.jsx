import React, { useEffect, useState } from 'react';
import { Link, useOutletContext, useParams } from 'react-router-dom';
import ColorGame from '../features/games/ColorGame';
import { finishGameSession, getGames, startGameSession } from '../services/games.service';

const playableTypes = new Set(['colores_primarios', 'memoria_colores']);

export default function GamePlayerPage() {
  const { id } = useParams();
  const { setFocus, requestExit } = useOutletContext();
  const [game, setGame] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const response = await getGames();
        const selected = (response.data.juegos || []).find((item) => String(item.id) === String(id));
        if (!selected) throw new Error('Juego no encontrado o inactivo.');
        if (!playableTypes.has(selected.tipo_juego)) throw new Error('Este juego todavía no tiene un reproductor compatible.');
        const session = await startGameSession({ juego_id: selected.id });
        if (active) { setGame(selected); setSessionId(session.data.partida.id); }
      } catch (failure) {
        if (active) setError(failure.response?.data?.mensaje || failure.message || 'No se pudo iniciar el juego.');
      } finally { if (active) setLoading(false); }
    })();
    return () => { active = false; };
  }, [id]);

  useEffect(() => {
    setFocus?.({ progress: result ? 100 : 0, status: game?.titulo || 'Cargando juego', score: result?.puntuacion ?? null, remainingTime: null, backLabel: 'Volver a juegos', exitPath: '/games', exitTitle: '¿Salir del juego?', exitDescription: 'Tu progreso de esta partida podría no guardarse si sales ahora.' });
  }, [game, result, setFocus]);

  const complete = async (outcome) => {
    if (!sessionId || saving) return;
    setSaving(true);
    setError('');
    try {
      const points = Number(outcome.puntuacion || 0);
      const response = await finishGameSession({
        partida_id: sessionId,
        puntuacion: points,
        aciertos: Number(outcome.aciertos || 0),
        errores: Math.max(0, 10 - Number(outcome.aciertos || 0)),
        tiempo_jugado: Math.max(0, Number(outcome.tiempoEmpleado || 0)),
        datos_partida: { tipo_juego: game.tipo_juego, respuestas: outcome.respuestas || [] },
      });
      setResult(response.data.resultados);
    } catch (failure) { setError(failure.response?.data?.mensaje || 'No se pudo guardar el resultado. Pulsa “Guardar resultados” para reintentar.'); }
    finally { setSaving(false); }
  };

  if (loading) return <div className="activity-player__message" role="status">Preparando el juego…</div>;
  if (error && !game) return <div className="activity-player__message" role="alert"><p>{error}</p><Link to="/games">Volver a juegos</Link></div>;
  if (result) return <section className="activity-player__result"><div className="activity-player__result-icon" aria-hidden="true">✓</div><h1>¡Juego completado!</h1><p>Resultado: {result.puntuacion}%</p><p>{result.tiempo_formateado}</p><Link to="/games">Volver a juegos</Link></section>;
  return <div className="game-player">{error && <p className="activity-player__error" role="alert">{error}</p>}{saving && <p role="status">Guardando resultado…</p>}<ColorGame onComplete={complete} onClose={requestExit}/></div>;
}
