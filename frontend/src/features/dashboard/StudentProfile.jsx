import React from 'react';
import { X } from 'lucide-react';
import { StudentGradeChart } from './DashboardCharts';

export default function StudentProfile({ student, loading, onClose }) {
  if (!student && !loading) return null;
  const history = student?.historial || [];
  return <aside className="dashboard-profile" aria-label="Perfil del estudiante" aria-busy={loading}>
    <div className="dashboard-profile__header"><div><span className="dashboard-eyebrow">Perfil de estudiante</span><h2>{loading ? 'Cargando…' : student.nombre}</h2></div><button type="button" className="dashboard-icon-button" onClick={onClose} aria-label="Cerrar perfil"><X size={18}/></button></div>
    {student && <>
      <p className="dashboard-muted">{student.cursos.join(' · ') || 'Sin cursos'}</p>
      <div className="dashboard-profile__metric"><span>Promedio</span><strong>{student.promedio === null ? '—' : `${student.promedio}%`}</strong></div>
      <h3>Evolución académica</h3>
      <StudentGradeChart history={history}/>
      <h3>Actividad reciente</h3>
      <ul className="dashboard-history">{history.slice(-6).reverse().map((item) => <li key={item.id}><span>{item.actividad}<small>{item.curso} · {new Date(item.fecha).toLocaleDateString()}</small></span><strong>{item.calificacion === null ? item.estado : `${item.calificacion}%`}</strong></li>)}</ul>
    </>}
  </aside>;
}
