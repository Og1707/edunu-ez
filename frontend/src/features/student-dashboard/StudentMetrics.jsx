import React from 'react';
import { Activity, CheckCircle2, ClipboardList } from 'lucide-react';
import StatCard from '../../components/ui/StatCard';

const metrics = [
  {
    key: 'completed',
    label: 'Actividades completadas',
    icon: <CheckCircle2 size={22} />,
    value: (stats) => stats.actividades_completadas,
    description: (stats) => `${stats.porcentaje_completado}% de avance`,
  },
  {
    key: 'pending',
    label: 'Actividades pendientes',
    icon: <ClipboardList size={22} />,
    value: (stats) => stats.actividades_pendientes,
    description: (stats) => `${stats.actividades_por_vencer} por vencer pronto`,
  },
  {
    key: 'average',
    label: 'Promedio',
    icon: <Activity size={22} />,
    value: (stats) => `${stats.puntuacion_promedio}%`,
    description: () => 'Según tus actividades calificadas',
  },
];

export default function StudentMetrics({ stats, loading }) {
  if (!loading && !stats) return null;

  return (
    <section className="student-dashboard__metrics" aria-label="Resumen de aprendizaje" aria-busy={loading}>
      {loading ? (
        <>
          <p className="student-dashboard__sr-only" role="status">Cargando el resumen de aprendizaje…</p>
          {metrics.map(({ key }) => <div className="student-dashboard__skeleton" key={key} aria-hidden="true" />)}
        </>
      ) : metrics.map((metric) => (
        <StatCard
          key={metric.key}
          className={`student-dashboard__metric student-dashboard__metric--${metric.key}`}
          label={metric.label}
          value={metric.value(stats)}
          icon={metric.icon}
          description={metric.description(stats)}
        />
      ))}
    </section>
  );
}
