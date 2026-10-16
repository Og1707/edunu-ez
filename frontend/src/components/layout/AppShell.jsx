import React, { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { BookOpen, Gamepad2, LayoutDashboard, LogOut, Menu, Users, X } from 'lucide-react';
import useAuth from '../../hooks/useAuth';
import './layouts.css';

const sharedItems = [
  { label: 'Dashboard', to: '/dashboard', icon: LayoutDashboard, end: true },
  { label: 'Cursos', to: '/courses', icon: BookOpen },
  { label: 'Actividades', to: '/activities', icon: BookOpen },
  { label: 'Juegos', to: '/games', icon: Gamepad2 },
];

export default function AppShell() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const items = user?.rol === 'administrador'
    ? [...sharedItems.slice(0, 3), { label: 'Usuarios', to: '/users', icon: Users }, sharedItems[3]]
    : sharedItems;
  const displayName = user?.nombre_completo || user?.username || 'Usuario';

  const handleLogout = () => {
    logout();
    navigate('/', { replace: true });
  };

  const closeMenu = () => setMenuOpen(false);

  return (
    <div className={`app-shell${menuOpen ? ' app-shell--menu-open' : ''}`}>
      <button
        className="layout-menu-toggle"
        type="button"
        aria-label={menuOpen ? 'Cerrar navegación' : 'Abrir navegación'}
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen(open => !open)}
      >
        {menuOpen ? <X aria-hidden="true" /> : <Menu aria-hidden="true" />}
      </button>
      {menuOpen && <button className="layout-backdrop" type="button" aria-label="Cerrar navegación" onClick={closeMenu} />}

      <aside className="app-sidebar">
        <NavLink className="layout-brand" to="/dashboard" onClick={closeMenu}>
          <span className="layout-brand__mark" aria-hidden="true">E</span>
          <span>EduNúñez</span>
        </NavLink>

        <nav className="layout-nav" aria-label="Navegación principal">
          {items.map(({ label, to, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={closeMenu}
              className={({ isActive }) => `layout-nav__link${isActive ? ' is-active' : ''}`}
            >
              <Icon size={19} aria-hidden="true" />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="layout-user-footer">
          <div className="layout-user-footer__identity">
            <span className="layout-avatar" aria-hidden="true">{displayName.charAt(0).toUpperCase()}</span>
            <span className="layout-user-footer__copy">
              <strong>{displayName}</strong>
              <small>{user?.rol}</small>
            </span>
          </div>
          <button className="layout-logout" type="button" onClick={handleLogout}>
            <LogOut size={18} aria-hidden="true" />
            <span>Cerrar sesión</span>
          </button>
        </div>
      </aside>

      <div className="app-shell__workspace">
        <header className="app-shell__header" aria-label="Cabecera del panel">
          <div className="app-shell__header-user">
            <span className="layout-avatar" aria-hidden="true">{displayName.charAt(0).toUpperCase()}</span>
            <span>{displayName}</span>
          </div>
        </header>
        <main className="app-shell__content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
