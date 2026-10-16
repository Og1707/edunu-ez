import React from 'react';
import './ui.css';

export default function EmptyState({ icon, title, description, action, className = '' }) {
  return (
    <section className={`ui-empty-state ${className}`.trim()} aria-live="polite">
      {icon && <span className="ui-empty-state__icon" aria-hidden="true">{icon}</span>}
      <h3 className="ui-empty-state__title">{title}</h3>
      {description && <p className="ui-empty-state__description">{description}</p>}
      {action && <div className="ui-empty-state__action">{action}</div>}
    </section>
  );
}
