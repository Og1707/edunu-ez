import React from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import EmptyState from '../../components/ui/EmptyState';

const axisTick = { fill: 'var(--color-neutral-600)', fontSize: 12 };
const tooltipStyle = {
  background: '#fff',
  border: '1px solid var(--color-neutral-200)',
  borderRadius: 'var(--radius-md)',
  boxShadow: 'var(--shadow-md)',
};

export function CoursePerformanceChart({ courses }) {
  const data = courses.filter((course) => course.promedio !== null && course.promedio !== undefined);
  if (!data.length) return <EmptyState title="Aún no hay calificaciones" description="El gráfico aparecerá cuando haya actividades calificadas."/>;

  return <div className="dashboard-recharts" role="figure" aria-label="Rendimiento promedio por curso">
    <ResponsiveContainer width="100%" height={Math.max(230, data.length * 48)}>
      <BarChart data={data} layout="vertical" margin={{ top: 6, right: 14, left: 0, bottom: 4 }}>
        <CartesianGrid horizontal={false} stroke="var(--color-neutral-200)" strokeDasharray="3 4" />
        <XAxis type="number" domain={[0, 100]} tickCount={6} tickFormatter={(value) => `${value}%`} tick={axisTick} tickLine={false} axisLine={false} />
        <YAxis type="category" dataKey="nombre" width={112} interval={0} tick={axisTick} tickLine={false} axisLine={false} />
        <Tooltip formatter={(value) => [`${value}%`, 'Promedio']} contentStyle={tooltipStyle} cursor={{ fill: 'var(--color-primary-50)' }} />
        <Bar dataKey="promedio" name="Promedio" fill="var(--color-primary-500)" radius={[0, 7, 7, 0]} maxBarSize={28} />
      </BarChart>
    </ResponsiveContainer>
  </div>;
}

export function SubjectPerformanceChart({ subjects, emptyDescription }) {
  if (!subjects.length) return <EmptyState title="Sin asignaturas vinculadas" description={emptyDescription || 'Las asignaturas aparecerán cuando tengan resultados calificados.'}/>;

  return <div className="dashboard-recharts" role="figure" aria-label="Rendimiento promedio por asignatura">
    <ResponsiveContainer width="100%" height={Math.max(220, subjects.length * 48)}>
      <BarChart data={subjects} layout="vertical" margin={{ top: 6, right: 14, left: 0, bottom: 4 }}>
        <CartesianGrid horizontal={false} stroke="var(--color-neutral-200)" strokeDasharray="3 4" />
        <XAxis type="number" domain={[0, 100]} tickCount={6} tickFormatter={(value) => `${value}%`} tick={axisTick} tickLine={false} axisLine={false} />
        <YAxis type="category" dataKey="nombre" width={112} interval={0} tick={axisTick} tickLine={false} axisLine={false} />
        <Tooltip formatter={(value, _name, item) => [`${value}% · ${item.payload.resultados} resultados`, 'Promedio']} contentStyle={tooltipStyle} cursor={{ fill: 'var(--color-primary-50)' }} />
        <Bar dataKey="promedio" name="Promedio" fill="var(--color-primary-500)" radius={[0, 7, 7, 0]} maxBarSize={28} />
      </BarChart>
    </ResponsiveContainer>
  </div>;
}

export function StudentGradeChart({ history }) {
  const data = history
    .filter((item) => item.calificacion !== null && item.calificacion !== undefined)
    .map((item) => ({
      fecha: new Date(item.fecha).toLocaleDateString(),
      actividad: item.actividad,
      calificacion: item.calificacion,
    }));
  if (!data.length) return <p className="dashboard-chart-empty">Aún no hay calificaciones para mostrar.</p>;

  return <div className="dashboard-recharts dashboard-recharts--line" role="figure" aria-label="Evolución de calificaciones del estudiante">
    <ResponsiveContainer width="100%" height={170}>
      <LineChart data={data} margin={{ top: 8, right: 10, left: -20, bottom: 0 }}>
        <CartesianGrid stroke="var(--color-neutral-200)" strokeDasharray="3 4" />
        <XAxis dataKey="fecha" tick={axisTick} tickLine={false} axisLine={false} minTickGap={24} />
        <YAxis domain={[0, 100]} tick={axisTick} tickLine={false} axisLine={false} />
        <Tooltip labelFormatter={(_label, payload) => payload?.[0]?.payload?.actividad || ''} formatter={(value) => [`${value}%`, 'Calificación']} contentStyle={tooltipStyle} />
        <Line type="monotone" dataKey="calificacion" stroke="var(--color-primary-600)" strokeWidth={3} dot={{ r: 3, fill: 'var(--color-primary-600)' }} activeDot={{ r: 5 }} />
      </LineChart>
    </ResponsiveContainer>
  </div>;
}

export function ActivityStatusChart({ items }) {
  const colors = {
    completed: 'var(--color-success-base)',
    pending: 'var(--color-primary-500)',
    due: '#f59e0b',
  };
  return <div className="dashboard-recharts" role="figure" aria-label={items.map((item) => `${item.label}: ${item.value}`).join(', ')}>
    <ResponsiveContainer width="100%" height={190}>
      <BarChart data={items} layout="vertical" margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
        <CartesianGrid horizontal={false} stroke="var(--color-neutral-200)" strokeDasharray="3 4" />
        <XAxis type="number" allowDecimals={false} tick={axisTick} tickLine={false} axisLine={false} />
        <YAxis type="category" dataKey="label" width={94} tick={axisTick} tickLine={false} axisLine={false} />
        <Tooltip formatter={(value) => [value, 'Actividades']} contentStyle={tooltipStyle} cursor={{ fill: 'var(--color-primary-50)' }} />
        <Bar dataKey="value" name="Actividades" radius={[0, 7, 7, 0]} maxBarSize={28}>
          {items.map((item) => <Cell key={item.label} fill={colors[item.color] || 'var(--color-primary-500)'}/>)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  </div>;
}
