import React from 'react';
import { BookOpen } from 'lucide-react';
import StudentMetrics from './StudentMetrics';
import StudentQuickLinks from './StudentQuickLinks';
import useStudentDashboard from './useStudentDashboard';
import './StudentDashboard.css';

export default function StudentDashboard({ user }) {
  const { stats, loading, error } = useStudentDashboard();
  const displayName = user?.nombre_completo || user?.username || 'Estudiante';

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
      <StudentQuickLinks />
    </main>
  );
}
