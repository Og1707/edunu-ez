import React from 'react';
import './ui.css';

export default function StatCard({ label, value, icon, description, className = '' }) {
  return (
    <section className={`ui-stat-card ${className}`.trim()} aria-label={label}>
      {icon && <span className="ui-stat-card__icon" aria-hidden="true">{icon}</span>}
      <div>
        <p className="ui-stat-card__label">{label}</p>
        <p className="ui-stat-card__value">{value}</p>
        {description && <p className="ui-stat-card__description">{description}</p>}
      </div>
    </section>
  );
}
