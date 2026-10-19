import React from 'react';

export default function StudentTrend({ values = [] }) {
  if (!values.length) return <span className="dashboard-trend__empty">—</span>;
  const width = 100;
  const height = 30;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const points = values.map((value, index) => {
    const x = values.length === 1 ? width / 2 : (index / (values.length - 1)) * width;
    const y = max === min ? height / 2 : height - ((value - min) / (max - min)) * (height - 4) - 2;
    return `${x},${y}`;
  }).join(' ');
  return <svg className="dashboard-trend" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Tendencia de calificaciones">
    <polyline points={points} fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
  </svg>;
}
