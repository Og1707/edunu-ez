import React, { useEffect, useMemo, useState } from 'react';
import { BookOpen, Search } from 'lucide-react';
import { getCourses } from '../../services/courses.service';
import TeacherCourseCard from './TeacherCourseCard';
import './TeacherCourses.css';

export default function TeacherCourses() {
  const [courses, setCourses] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;

    getCourses()
      .then(({ data }) => {
        if (!active) return;
        setCourses(Array.isArray(data) ? data : data?.cursos || []);
      })
      .catch(() => {
        if (active) setError('No fue posible cargar tus cursos. Intenta de nuevo.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const visibleCourses = useMemo(() => {
    const query = search.trim().toLocaleLowerCase();
    if (!query) return courses;
    return courses.filter((course) => (
      `${course.nombre || ''} ${course.descripcion || ''} ${(course.asignaturas_nombres || []).join(' ')}`
        .toLocaleLowerCase()
        .includes(query)
    ));
  }, [courses, search]);

  return (
    <section className="teacher-courses">
      <header className="teacher-courses__header">
        <div>
          <span className="teacher-courses__eyebrow">Espacio docente</span>
          <h1>Mis cursos</h1>
          <p>Consulta tus cursos asignados y revisa qué estudiantes están inscritos.</p>
        </div>
        <label className="teacher-courses__search">
          <Search size={18} aria-hidden="true" />
          <span className="teacher-courses__sr-only">Buscar en mis cursos</span>
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Buscar curso o asignatura"
          />
        </label>
      </header>

      {error && <p className="teacher-courses__error" role="alert">{error}</p>}
      {loading ? (
        <p className="teacher-courses__state" role="status">Cargando tus cursos…</p>
      ) : visibleCourses.length ? (
        <div className="teacher-courses__grid" aria-label="Cursos asignados">
          {visibleCourses.map((course) => <TeacherCourseCard key={course.id} course={course} />)}
        </div>
      ) : (
        <div className="teacher-courses__empty">
          <span aria-hidden="true"><BookOpen size={25} /></span>
          <h2>{courses.length ? 'No hay coincidencias' : 'Aún no tienes cursos asignados'}</h2>
          <p>{courses.length ? 'Prueba con otro nombre de curso o asignatura.' : 'Cuando te asignen un curso, aparecerá aquí.'}</p>
        </div>
      )}
    </section>
  );
}
