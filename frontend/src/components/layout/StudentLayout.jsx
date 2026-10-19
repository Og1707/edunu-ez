import React, { useEffect, useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { BookOpen, Gamepad2, LayoutDashboard, LogOut, Menu, Trophy, X } from 'lucide-react';
import useAuth from '../../hooks/useAuth';
import './layouts.css';
import './student-theme.css';

const studentItems = [
  { label: 'Mi inicio', to: '/dashboard', icon: LayoutDashboard, end: true },
  { label: 'Mis tareas', to: '/activities', icon: BookOpen },
  { label: 'Explorar juegos', to: '/games', icon: Gamepad2 },
  { label: 'Mi progreso', to: '/progress', icon: Trophy },
];

export default function StudentLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const displayName = user?.nombre_completo || user?.username || 'Estudiante';
  const handleLogout = () => { logout(); navigate('/', { replace: true }); };
  useEffect(() => {
    const closeOnEscape = (event) => { if (event.key === 'Escape') setMenuOpen(false); };
    window.addEventListener('keydown', closeOnEscape);
    return () => window.removeEventListener('keydown', closeOnEscape);
  }, []);

  return <div className={`student-layout${menuOpen ? ' student-layout--menu-open' : ''}`}>
    <button className="layout-menu-toggle student-layout__menu-toggle" type="button" aria-label={menuOpen ? 'Cerrar menú' : 'Abrir menú'} aria-expanded={menuOpen} aria-controls="student-sidebar" onClick={() => setMenuOpen((open) => !open)}>{menuOpen ? <X size={20}/> : <Menu size={20}/>}</button>
    {menuOpen && <button className="layout-backdrop" type="button" aria-label="Cerrar menú" onClick={() => setMenuOpen(false)} />}
    <aside id="student-sidebar" className="student-sidebar">
      <NavLink className="layout-brand" to="/dashboard"><span className="layout-brand__mark" aria-hidden="true">E</span><span>EduNúñez</span></NavLink>
      <nav className="layout-nav" aria-label="Navegación principal">{studentItems.map(({ label, to, icon: Icon, end }) => <NavLink key={to} to={to} end={end} onClick={() => setMenuOpen(false)} className={({ isActive }) => `layout-nav__link${isActive ? ' is-active' : ''}`}><Icon size={19} aria-hidden="true"/><span>{label}</span></NavLink>)}</nav>
      <div className="student-sidebar__footer">

        <div className="layout-user-footer__identity"><span className="layout-avatar" aria-hidden="true">{displayName.charAt(0).toUpperCase()}</span><strong>{displayName}</strong></div>
        <button className="layout-logout" type="button" onClick={handleLogout}><LogOut size={18} aria-hidden="true"/><span>Cerrar sesión</span></button>
      </div>
    </aside>
    <div className="student-layout__workspace">
      <header className="student-layout__header" aria-label="Cabecera del panel"><div><span className="student-layout__eyebrow">¡Sigue aprendiendo!</span><strong>{displayName}</strong></div></header>
      <main className="student-layout__content"><Outlet /></main>
    </div>
    <nav className="student-mobile-nav" aria-label="Navegación principal">{studentItems.map(({ label, to, icon: Icon, end }) => <NavLink key={to} to={to} end={end} className={({ isActive }) => `student-mobile-nav__link${isActive ? ' is-active' : ''}`}><Icon size={19} aria-hidden="true"/><span>{label}</span></NavLink>)}</nav>
  </div>;
}
