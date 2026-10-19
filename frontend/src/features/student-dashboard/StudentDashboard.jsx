import React from 'react';
import { BookOpen } from 'lucide-react';
import { ActivityStatusChart } from '../dashboard/DashboardCharts';
import StudentMetrics from './StudentMetrics';
import StudentQuickLinks from './StudentQuickLinks';
import useStudentDashboard from './useStudentDashboard';
import './StudentDashboard.css';

export default function StudentDashboard({ user }) {
  const { stats, loading, error } = useStudentDashboard();
  const displayName = user?.nombre_completo || user?.username || 'Estudiante';
  const activityChart = [
    { label: 'Completadas', value: Number(stats?.actividades_completadas || 0), color: 'completed' },
    { label: 'Pendientes', value: Number(stats?.actividades_pendientes || 0), color: 'pending' },
    { label: 'Por vencer', value: Number(stats?.actividades_por_vencer || 0), color: 'due' },
  ];

  return (
    <main className="student-dashboard">
      <header className="student-dashboard__welcome">
        <div className="student-dashboard__welcome-copy">
          <span className="student-dashboard__eyebrow">Tu espacio de aprendizaje</span>
          <h1>¡Hola, {displayName}!</h1>
          <p>Cada actividad es un paso nuevo. Mira cómo vas y elige qué hacer hoy.</p>
        </div>
        <span className="student-dashboard__welcome-mark" aria-hidden="true">
          <BookOpen size={44} strokeWidth={1.8} />
        </span>
      </header>

      {error && <p className="student-dashboard__error" role="alert">{error}</p>}
      <StudentMetrics stats={stats} loading={loading} />
      {!loading && stats && <section className="student-dashboard__chart-panel" aria-labelledby="student-dashboard-activity-title"><div className="student-dashboard__section-heading"><span className="student-dashboard__eyebrow">Tu avance</span><h2 id="student-dashboard-activity-title">Estado de tus actividades</h2><p>Compara lo que terminaste con lo que tienes pendiente.</p></div><ActivityStatusChart items={activityChart}/></section>}
      <StudentQuickLinks />
    </main>
  );
}
