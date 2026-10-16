import React, { useEffect, useMemo, useState } from 'react';
import { Link, useOutletContext, useParams } from 'react-router-dom';
import { getCompleteActivity } from '../services/activities.service';
import { completeStudentActivity, startStudentActivity } from '../services/games.service';
import './ActivityPlayerPage.css';

export default function ActivityPlayerPage() {
  const { id } = useParams();
  const { setFocus } = useOutletContext();
  const [activity, setActivity] = useState(null);
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [startedAt, setStartedAt] = useState(Date.now());
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const questions = useMemo(() => activity?.preguntas || [], [activity]);

  useEffect(() => {
    setFocus?.({ progress: questions.length ? Math.round(((index + 1) / questions.length) * 100) : 0, status: activity?.titulo || 'Cargando actividad', score: result?.score ?? null, remainingTime: null, backLabel: 'Volver a Mis tareas', exitPath: '/activities', exitTitle: '¿Salir de la actividad?', exitDescription: 'Tu progreso podría no guardarse si sales ahora.' });
  }, [index, questions.length, activity?.titulo, result?.score, setFocus]);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const [response] = await Promise.all([getCompleteActivity(id), startStudentActivity({ actividad_id: Number(id) })]);
        if (active) { setActivity(response.data); setStartedAt(Date.now()); }
      } catch (e) {
        if (active) setError(e.response?.data?.mensaje || 'No se pudo cargar o iniciar esta actividad.');
      } finally { if (active) setLoading(false); }
    })();
    return () => { active = false; };
  }, [id]);

  const finish = async () => {
    if (saving || !questions.length) return;
    setSaving(true);
    const details = questions.map((question, questionIndex) => {
      const chosen = answers[question.id];
      const option = question.opciones?.find((item) => String(item.id) === String(chosen));
      return { pregunta_id: question.id, respuesta_seleccionada: option?.texto || '', es_correcta: Boolean(option?.es_correcta), orden: questionIndex + 1 };
    });
    const score = Math.round((details.filter((item) => item.es_correcta).length / questions.length) * 100);
    try {
      const response = await completeStudentActivity({ actividad_id: Number(id), puntuacion: score, tiempo_empleado: Math.max(0, Math.round((Date.now() - startedAt) / 1000)), respuestas_detalle: details });
      setResult({ score, data: response.data });
    } catch (e) { setError(e.response?.data?.mensaje || 'No se pudo guardar el resultado. Tus respuestas siguen aquí; puedes intentar de nuevo.'); }
    finally { setSaving(false); }
  };

  if (loading) return <div className="activity-player__message" role="status">Cargando actividad…</div>;
  if (error && !activity) return <div className="activity-player__message" role="alert">{error}<p><Link to="/activities">Volver a Mis tareas</Link></p></div>;
  if (result) return <section className="activity-player__result"><div className="activity-player__result-icon">✓</div><h1>¡Actividad completada!</h1><p>Tu puntuación</p><strong>{result.score}%</strong><p>{result.data?.mensaje || 'Tus respuestas se guardaron correctamente.'}</p><Link to="/activities">Volver a Mis tareas</Link></section>;
  if (!questions.length) return <div className="activity-player__message" role="alert">Esta actividad todavía no tiene preguntas.<p><Link to="/activities">Volver a Mis tareas</Link></p></div>;
  const question = questions[index];
  return <section className="activity-player">
    <header><p>{activity.titulo}</p><span>Pregunta {index + 1} de {questions.length}</span></header>
    <div className="activity-player__bar" role="progressbar" aria-label="Progreso de la actividad" aria-valuemin="0" aria-valuemax={questions.length} aria-valuenow={index + 1}><span style={{ width: `${((index + 1) / questions.length) * 100}%` }} /></div>
    {error && <p role="alert" className="activity-player__error">{error}</p>}
    <article className="activity-player__question"><p className="activity-player__eyebrow">{activity.descripcion}</p><h1>{question.enunciado}</h1><fieldset><legend>Selecciona una respuesta</legend>{(question.opciones || []).map((option) => <label key={option.id} className={String(answers[question.id]) === String(option.id) ? 'is-selected' : ''}><input type="radio" name={`question-${question.id}`} value={option.id} checked={String(answers[question.id]) === String(option.id)} onChange={() => setAnswers((current) => ({ ...current, [question.id]: option.id }))} /><span>{option.texto}</span></label>)}</fieldset></article>
    <footer>{index > 0 && <button type="button" onClick={() => setIndex(index - 1)}>Anterior</button>}{index < questions.length - 1 ? <button type="button" disabled={!answers[question.id]} onClick={() => setIndex(index + 1)}>Siguiente</button> : <button type="button" disabled={!answers[question.id] || saving} onClick={finish}>{saving ? 'Guardando…' : 'Finalizar actividad'}</button>}</footer>
  </section>;
}
