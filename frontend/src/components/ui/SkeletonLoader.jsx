import React from 'react';
import './ui.css';

export default function SkeletonLoader({ count = 3, variant = 'card', label = 'Cargando contenido' }) {
  return (
    <div className={`ui-skeleton-list ui-skeleton-list--${variant}`} role="status" aria-label={label}>
      {Array.from({ length: count }, (_, index) => (
        <div className="ui-skeleton-card" key={index} aria-hidden="true">
          <span className="ui-skeleton ui-skeleton--heading" />
          <span className="ui-skeleton ui-skeleton--line" />
          <span className="ui-skeleton ui-skeleton--line ui-skeleton--short" />
        </div>
      ))}
      <span className="ui-visually-hidden">{label}…</span>
    </div>
  );
}
