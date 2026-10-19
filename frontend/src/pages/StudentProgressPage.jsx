import React, { useEffect, useMemo, useState } from 'react';
import { Activity, Award, Flame, Star, Trophy } from 'lucide-react';
import { getStudentActivities, getStudentStats } from '../services/games.service';
import StatCard from '../components/ui/StatCard';
import EmptyState from '../components/ui/EmptyState';
import './StudentProgressPage.css';

const completed = (activity) => Boolean(
  activity.progreso?.completada ||
  ['completada', 'revisada', 'calificada'].includes(activity.progreso?.estado || activity.estado),
);

export default function StudentProgressPage() {
  const [activities, setActivities] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    Promise.all([getStudentActivities(), getStudentStats()])
      .then(([activityResponse, statsResponse]) => {
        if (!active) return;
        const data = activityResponse.data;
        setActivities(Array.isArray(data) ? data : data?.actividades_asignadas || []);
        setStats(statsResponse.data);
      })
      .catch(() => { if (active) setError('No pudimos cargar tu progreso. Inténtalo de nuevo.'); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const history = useMemo(() => activities
    .filter(completed)
    .sort((a, b) => new Date(b.progreso?.fecha_completado || b.fecha_creacion || 0) - new Date(a.progreso?.fecha_completado || a.fecha_creacion || 0)), [activities]);
  const chart = [
    { label: 'Completadas', value: Number(stats?.actividades_completadas || 0), color: 'completed' },
    { label: 'Pendientes', value: Number(stats?.actividades_pendientes || 0), color: 'pending' },
    { label: 'Por vencer', value: Number(stats?.actividades_por_vencer || 0), color: 'due' },
  ];
  const maxValue = Math.max(1, ...chart.map((item) => item.value));
  return <main className="student-progress">
    <header className="student-progress__header"><div><span className="student-progress__eyebrow">Tu recorrido de aprendizaje</span><h1>Mi progreso</h1><p>Revisa tus actividades terminadas y cómo avanzas.</p></div><span className="student-progress__trophy" aria-hidden="true"><Trophy size={28}/></span></header>
    {error && <p className="student-progress__error" role="alert">{error}</p>}
    {loading ? <p className="student-progress__loading" role="status">Cargando tu progreso…</p> : <>
      <section className="student-progress__metrics" aria-label="Resumen de progreso">
        <StatCard label="Actividades completadas" value={stats?.actividades_completadas ?? 0} icon={<Activity/>} description={`${stats?.porcentaje_completado ?? 0}% de tus actividades`} />
        <StatCard label="Racha activa" value="No disponible" icon={<Flame/>} description="El servicio todavía no registra días de racha." />
      </section>
      <div className="student-progress__columns">
        <section className="student-progress__panel" aria-labelledby="student-progress-chart-title"><div className="student-progress__panel-heading"><div><h2 id="student-progress-chart-title">Actividad</h2><p>Resumen de tus tareas actuales</p></div><span>{stats?.puntuacion_promedio ?? 0}% promedio</span></div><div className="student-progress__chart" role="img" aria-label={chart.map((item) => `${item.label}: ${item.value}`).join(', ')}>{chart.map((item) => <div className="student-progress__bar-row" key={item.label}><span>{item.label}</span><div className="student-progress__bar-track"><div className={`student-progress__bar student-progress__bar--${item.color}`} style={{ width: `${(item.value / maxValue) * 100}%` }}/></div><strong>{item.value}</strong></div>)}</div></section>
        <section className="student-progress__panel student-progress__achievements" aria-labelledby="student-progress-achievements-title"><h2 id="student-progress-achievements-title">Logros</h2><p>Reconocimientos disponibles en esta versión.</p><div className="student-progress__achievement"><Award aria-hidden="true"/><span><strong>Primeros pasos</strong><small>Completa tu primera actividad</small></span></div><div className="student-progress__achievement"><Trophy aria-hidden="true"/><span><strong>Constancia</strong><small>Completa cinco actividades</small></span></div><div className="student-progress__achievement"><Star aria-hidden="true"/><span><strong>Buen resultado</strong><small>Alcanza un promedio de 80%</small></span></div></section>
      </div>
      <section className="student-progress__history" aria-labelledby="student-progress-history-title"><div className="student-progress__panel-heading"><div><h2 id="student-progress-history-title">Historial</h2><p>Actividades que ya completaste</p></div><span>{history.length} actividades</span></div>{history.length ? <ul>{history.map((activity) => <li key={activity.asignacion_id || activity.actividad_id || activity.id}><span className="student-progress__history-icon" aria-hidden="true"><Activity size={18}/></span><div><strong>{activity.titulo}</strong><small>{activity.curso_nombre || activity.curso || 'Actividad educativa'}{activity.progreso?.fecha_completado ? ` · ${new Date(activity.progreso.fecha_completado).toLocaleDateString()}` : ''}</small></div><span className="student-progress__score">{activity.progreso?.puntuacion ?? activity.calificacion ?? '—'}{activity.progreso?.puntuacion != null || activity.calificacion != null ? '%' : ''}</span></li>)}</ul> : <EmptyState icon={<Activity/>} title="Aún no hay actividades completadas" description="Cuando termines una actividad, aparecerá aquí."/>}</section>
    </>}
  </main>;
}
