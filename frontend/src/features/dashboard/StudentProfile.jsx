import React, { useEffect, useMemo } from 'react';
import { X } from 'lucide-react';
import { StudentGradeChart } from './DashboardCharts';
import { assignSubjectColors, BLUE_MATEMATICAS } from './subjectColors';

const getInitials = (name = '') => {
  const parts = String(name).trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return '—';
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
};

export default function StudentProfile({
  student,
  loading,
  error,
  onClose,
  isClosing = false,
}) {
  const materias = student?.materias;
  const colorMap = useMemo(() => assignSubjectColors(materias || []), [materias]);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && typeof onClose === 'function') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  // During the closing animation (isClosing=true) the parent keeps us mounted
  // so the slide-out runs fully. We must render even if student data is null.
  if (!isClosing && !student && !loading && !error) return null;

  const history = student?.historial || [];
  const materiasList = materias || [];

  const totalActs = history.length;
  const completedActs = history.filter((item) =>
    ['completada', 'revisada', 'calificada'].includes(item.estado)
  ).length;

  const studentName = student?.nombre || student?.nombre_completo || student?.username || '';

  return (
    <aside
      className={`dashboard-profile ${isClosing ? 'is-closing' : ''}`}
      aria-label="Perfil del estudiante"
      aria-busy={loading}
    >
      <div className="dashboard-profile__header">
        <div className="dashboard-profile__user-info">
          {studentName && (
            <div className="dashboard-profile__avatar" aria-hidden="true">
              {getInitials(studentName)}
            </div>
          )}
          <div>
            <span className="dashboard-eyebrow">Perfil de estudiante</span>
            <h2>{studentName || (loading ? 'Cargando…' : 'Estudiante')}</h2>
            {student && (
              <p className="dashboard-muted">
                {student.cursos?.join(' · ') || 'Sin cursos'}
              </p>
            )}
          </div>
        </div>
        <button
          type="button"
          className="dashboard-icon-button"
          onClick={onClose}
          aria-label="Cerrar perfil"
        >
          <X size={18} />
        </button>
      </div>

      {error && (
        <div className="dashboard-profile__error" role="alert">
          <p>{error}</p>
        </div>
      )}

      {loading && !student && !error && (
        <div className="dashboard-profile__loading" role="status">
          <p>Cargando información del estudiante…</p>
        </div>
      )}

      {student && (
        <div className="dashboard-profile__content dashboard-profile-fade-in" key={student.id}>
          <div className="dashboard-profile__stats-grid">
            <div className="dashboard-profile__stat-box">
              <span className="dashboard-profile__stat-label">Promedio</span>
              <strong className="dashboard-profile__stat-val">
                {student.promedio === null || student.promedio === undefined
                  ? '—'
                  : `${student.promedio}%`}
              </strong>
            </div>
            <div className="dashboard-profile__stat-box">
              <span className="dashboard-profile__stat-label">Actividades</span>
              <strong className="dashboard-profile__stat-val">
                {totalActs > 0 ? `${completedActs}/${totalActs}` : '0/0'}
              </strong>
            </div>
          </div>

          <div className="dashboard-profile__section">
            <h3 className="dashboard-profile__subtitle">Evolución del Rendimiento</h3>
            <StudentGradeChart history={history} />
          </div>

          <div className="dashboard-profile__section">
            <div
              className="dashboard-subject-grid"
              role="group"
              aria-label="KPIs de rendimiento por materia"
            >
              {materiasList.length > 0 ? (
                materiasList.map((materia) => {
                  const color =
                    colorMap.get(materia.id) ||
                    colorMap.get(materia.nombre) ||
                    BLUE_MATEMATICAS;
                  const gradeDisplay =
                    materia.promedio === null || materia.promedio === undefined
                      ? '—'
                      : `${materia.promedio}%`;

                  return (
                    <div
                      key={materia.id}
                      className="dashboard-subject-card"
                      style={{ background: color }}
                      tabIndex={0}
                      role="article"
                      aria-label={`${materia.nombre}: ${gradeDisplay}`}
                    >
                      <span className="dashboard-subject-card__name">
                        {materia.nombre}
                      </span>
                      <strong className="dashboard-subject-card__val">
                        {gradeDisplay}
                      </strong>
                    </div>
                  );
                })
              ) : (
                <p className="dashboard-profile__empty">
                  Sin asignaturas vinculadas a este estudiante.
                </p>
              )}
            </div>
          </div>

          <div className="dashboard-profile__section">
            <h3 className="dashboard-profile__subtitle">Actividades Realizadas</h3>
            {history.length ? (
              <ul className="dashboard-history">
                {history
                  .slice(-6)
                  .reverse()
                  .map((item) => (
                    <li key={item.id}>
                      <span>
                        {item.actividad}
                        <small>
                          {item.curso} · {new Date(item.fecha).toLocaleDateString()}
                        </small>
                      </span>
                      <strong>
                        {item.calificacion === null
                          ? item.estado
                          : `${item.calificacion}%`}
                      </strong>
                    </li>
                  ))}
              </ul>
            ) : (
              <p className="dashboard-profile__empty">
                Aún no hay actividades registradas.
              </p>
            )}
          </div>
        </div>
      )}
    </aside>
  );
}
