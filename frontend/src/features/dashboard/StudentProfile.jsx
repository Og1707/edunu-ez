import React from 'react';
import { X } from 'lucide-react';

export default function StudentProfile({ student, loading, onClose }) {
  if (!student && !loading) return null;
  const history = student?.historial || [];
  const grades = history.filter((item) => item.calificacion !== null);
  const points = grades.map((item, index) => `${grades.length < 2 ? 50 : (index / (grades.length - 1)) * 100},${100 - item.calificacion}`).join(' ');
  return <aside className="dashboard-profile" aria-label="Perfil del estudiante" aria-busy={loading}>
    <div className="dashboard-profile__header"><div><span className="dashboard-eyebrow">Perfil de estudiante</span><h2>{loading ? 'Cargando…' : student.nombre}</h2></div><button type="button" className="dashboard-icon-button" onClick={onClose} aria-label="Cerrar perfil"><X size={18}/></button></div>
    {student && <>
      <p className="dashboard-muted">{student.cursos.join(' · ') || 'Sin cursos'}</p>
      <div className="dashboard-profile__metric"><span>Promedio</span><strong>{student.promedio === null ? '—' : `${student.promedio}%`}</strong></div>
      <h3>Evolución académica</h3>
      <div className="dashboard-chart dashboard-chart--profile"><svg viewBox="0 0 100 100" role="img" aria-label="Evolución de calificaciones"><polyline points={points} fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round"/></svg></div>
      <h3>Actividad reciente</h3>
      <ul className="dashboard-history">{history.slice(-6).reverse().map((item) => <li key={item.id}><span>{item.actividad}<small>{item.curso} · {new Date(item.fecha).toLocaleDateString()}</small></span><strong>{item.calificacion === null ? item.estado : `${item.calificacion}%`}</strong></li>)}</ul>
    </>}
  </aside>;
}
