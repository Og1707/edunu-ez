import React, { useState } from 'react';
import { BookOpen, ChevronDown, Users } from 'lucide-react';
import { getCourseStudents } from '../../services/courses.service';

export default function TeacherCourseCard({ course }) {
  const [students, setStudents] = useState(null);
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const panelId = `teacher-course-students-${course.id}`;
  const titleId = `teacher-course-title-${course.id}`;
  const subjects = course.asignaturas_nombres || [];

  const loadStudents = async () => {
    setLoading(true);
    setError('');
    try {
      const { data } = await getCourseStudents(course.id);
      setStudents(Array.isArray(data) ? data : data?.estudiantes || []);
    } catch (_) {
      setError('No se pudo cargar la lista de estudiantes.');
    } finally {
      setLoading(false);
    }
  };

  const toggleStudents = async () => {
    if (expanded) {
      setExpanded(false);
      return;
    }
    setExpanded(true);
    if (students === null || error) await loadStudents();
  };

  return (
    <article className="teacher-course-card" aria-labelledby={titleId}>
      <div className="teacher-course-card__topline">
        <span className="teacher-course-card__icon" aria-hidden="true"><BookOpen size={21} /></span>
        <span className="teacher-course-card__badge">Asignado a ti</span>
      </div>
      <h2 id={titleId}>{course.nombre}</h2>
      <p className="teacher-course-card__description">{course.descripcion || 'Sin descripción disponible.'}</p>

      <div className="teacher-course-card__subjects" aria-label="Asignaturas">
        {subjects.length ? subjects.map((subject) => (
          <span className="teacher-course-card__subject" key={subject}>{subject}</span>
        )) : <span className="teacher-course-card__no-subjects">Sin asignaturas registradas</span>}
      </div>

      <button
        className="teacher-course-card__students-toggle"
        type="button"
        aria-expanded={expanded}
        aria-controls={panelId}
        onClick={toggleStudents}
      >
        <span><Users size={18} aria-hidden="true" /> Ver estudiantes{students ? ` (${students.length})` : ''}</span>
        <ChevronDown size={18} aria-hidden="true" />
      </button>

      {expanded && (
        <div className="teacher-course-card__student-panel" id={panelId}>
          <h3>Estudiantes inscritos{students ? ` (${students.length})` : ''}</h3>
          {loading ? <p role="status">Cargando estudiantes…</p> : error ? (
            <div>
              <p className="teacher-course-card__error" role="alert">{error}</p>
              <button className="teacher-course-card__retry" type="button" onClick={loadStudents}>Reintentar</button>
            </div>
          ) : students?.length ? (
            <ul>
              {students.map((student) => {
                const name = student.nombre_completo || student.username || 'Estudiante';
                return (
                  <li key={student.inscripcion_id || student.id}>
                    <span className="teacher-course-card__avatar" aria-hidden="true">{name.charAt(0).toUpperCase()}</span>
                    <span><strong>{name}</strong>{student.username && <small>@{student.username}</small>}</span>
                  </li>
                );
              })}
            </ul>
          ) : <p>Este curso aún no tiene estudiantes inscritos.</p>}
        </div>
      )}
    </article>
  );
}
