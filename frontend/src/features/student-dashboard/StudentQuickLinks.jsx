import React from 'react';
import { ArrowRight, BookOpen, Gamepad2, LineChart } from 'lucide-react';
import { Link } from 'react-router-dom';

const links = [
  {
    to: '/activities',
    label: 'Mis actividades',
    description: 'Continúa tus tareas y revisa tus resultados.',
    icon: BookOpen,
    tone: 'indigo',
  },
  {
    to: '/games',
    label: 'Explorar juegos',
    description: 'Practica con juegos educativos.',
    icon: Gamepad2,
    tone: 'sky',
  },
  {
    to: '/progress',
    label: 'Mi progreso',
    description: 'Consulta tus estadísticas e historial.',
    icon: LineChart,
    tone: 'mint',
  },
];

export default function StudentQuickLinks() {
  return (
    <section className="student-dashboard__links" aria-labelledby="student-dashboard-links-title">
      <div className="student-dashboard__section-heading">
        <div>
          <span className="student-dashboard__eyebrow">A un paso</span>
          <h2 id="student-dashboard-links-title">¿Qué quieres hacer hoy?</h2>
        </div>
      </div>
      <div className="student-dashboard__link-grid">
        {links.map(({ to, label, description, icon: Icon, tone }) => (
          <Link className={`student-dashboard__link student-dashboard__link--${tone}`} to={to} key={to}>
            <span className="student-dashboard__link-icon" aria-hidden="true"><Icon size={23} /></span>
            <span className="student-dashboard__link-copy">
              <strong>{label}</strong>
              <span>{description}</span>
            </span>
            <ArrowRight className="student-dashboard__link-arrow" size={19} aria-hidden="true" />
          </Link>
        ))}
      </div>
    </section>
  );
}
