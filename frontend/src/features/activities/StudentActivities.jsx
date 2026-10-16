import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, BookOpen, CheckCircle2, Clock3, Play } from 'lucide-react';
import { getStudentActivities, getStudentStats } from '../../services/games.service';
import EmptyState from '../../components/ui/EmptyState';
import './StudentActivities.css';

const isComplete = (item) => Boolean(item.progreso?.completada || ['completada', 'revisada', 'calificada'].includes(item.progreso?.estado || item.estado));
const isInProgress = (item) => !isComplete(item) && ['en_progreso', 'en progreso', 'in_progress'].includes(item.progreso?.estado || item.estado);

export default function StudentActivities() {
  const navigate = useNavigate();
  const [activities, setActivities] = useState([]);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState('todas');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    Promise.all([getStudentActivities(), getStudentStats()])
      .then(([activityResponse, statsResponse]) => {
        if (!mounted) return;
        const data = activityResponse.data;
        setActivities(Array.isArray(data) ? data : data?.actividades_asignadas || []);
        setStats(statsResponse.data);
      })
      .catch(() => { if (mounted) setError('No pudimos cargar tus actividades. Inténtalo de nuevo.'); })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, []);

  const counts = useMemo(() => ({
    todas: activities.length,
    pendientes: activities.filter((item) => !isComplete(item) && !isInProgress(item)).length,
    en_progreso: activities.filter(isInProgress).length,
    completadas: activities.filter(isComplete).length,
  }), [activities]);
  const filtered = activities.filter((item) => filter === 'todas' || (filter === 'pendientes' ? !isComplete(item) && !isInProgress(item) : filter === 'en_progreso' ? isInProgress(item) : isComplete(item)));
  const completion = Number(stats?.porcentaje_completado ?? (activities.length ? Math.round((counts.completadas / activities.length) * 100) : 0));

  const tabs = [
    ['todas', 'Todas'], ['pendientes', 'Pendientes'], ['en_progreso', 'En progreso'], ['completadas', 'Completadas'],
  ];

  return <main className="student-activities">
    <header className="student-activities__header">
      <div><span className="student-activities__eyebrow">Tu espacio de aprendizaje</span><h1>Mis actividades</h1><p>Continúa donde te quedaste y revisa lo que ya completaste.</p></div>
      <div className="student-activities__summary" aria-label={`${counts.completadas} de ${activities.length} actividades completadas`}><strong>{counts.completadas}<span>/{activities.length}</span></strong><small>completadas</small></div>
    </header>
    <section className="student-activities__progress" aria-label={`Progreso general: ${completion}%`}>
      <div><strong>Progreso general</strong><span>{completion}%</span></div>
      <div className="student-activities__progress-track" role="progressbar" aria-valuenow={completion} aria-valuemin="0" aria-valuemax="100"><span style={{ width: `${Math.max(0, Math.min(100, completion))}%` }}/></div>
      <p>{counts.completadas} de {activities.length} actividades completadas</p>
    </section>
    {error && <p className="student-activities__error" role="alert">{error}</p>}
    <div className="student-activities__tabs" role="tablist" aria-label="Filtrar actividades">{tabs.map(([key, label], index) => <button key={key} id={`activities-tab-${key}`} role="tab" type="button" tabIndex={filter === key ? 0 : -1} aria-selected={filter === key} aria-controls="activities-panel" onKeyDown={(event) => { if (!['ArrowRight', 'ArrowLeft', 'Home', 'End'].includes(event.key)) return; event.preventDefault(); const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : (index + (event.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length; document.getElementById(`activities-tab-${tabs[next][0]}`)?.click(); document.getElementById(`activities-tab-${tabs[next][0]}`)?.focus(); }} onClick={() => setFilter(key)}>{label}<span>{counts[key]}</span></button>)}</div>
    <section id="activities-panel" role="tabpanel" aria-labelledby={`activities-tab-${filter}`} className="student-activities__list" aria-live="polite">
      {loading ? <p className="student-activities__loading" role="status">Cargando tus actividades…</p> : filtered.length ? filtered.map((item) => {
        const done = isComplete(item);
        const active = isInProgress(item);
        const status = done ? 'Completada' : active ? 'En progreso' : 'Pendiente';
        return <article className={`student-activity-card${done ? ' is-complete' : active ? ' is-active' : ' is-pending'}`} key={item.asignacion_id || item.actividad_id || item.id}>
          <span className="student-activity-card__icon" aria-hidden="true">{done ? <CheckCircle2/> : active ? <Clock3/> : <BookOpen/>}</span>
          <div className="student-activity-card__body"><div className="student-activity-card__meta"><span>{item.curso_nombre || item.curso || 'Actividad educativa'}</span><span className={`student-activity-card__status student-activity-card__status--${done ? 'complete' : active ? 'active' : 'pending'}`}>{status}</span></div><h2>{item.titulo || item.nombre || 'Actividad'}</h2><p>{item.descripcion || 'Abre esta actividad para ver las instrucciones y comenzar.'}</p>{done && (item.progreso?.puntuacion ?? item.calificacion) != null && <small className="student-activity-card__score">Resultado: {item.progreso?.puntuacion ?? item.calificacion}%</small>}</div>
          {!done && <button className="student-activity-card__action" type="button" onClick={() => navigate(`/activities/${item.actividad_id || item.id}/play`)}><Play size={17} aria-hidden="true"/><span>{active ? 'Continuar' : 'Iniciar'}</span></button>}
        </article>;
      }) : <EmptyState icon={<Activity/>} title={filter === 'completadas' ? 'Aún no hay actividades completadas' : 'No hay actividades en esta sección'} description="Cuando tu docente asigne actividades, aparecerán aquí."/>}
    </section>
  </main>;
}
