import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '@/features/auth';
import { Icon, LogoMark } from '@/shared/ui';
import { NAV_ITEMS, PASSWORD_ITEM, type NavItem } from './navigation';

function SidebarLink({ item }: { item: NavItem }) {
  return (
    <NavLink to={item.to} className={({ isActive }) => `sidebar__link${isActive ? ' active' : ''}`}>
      <Icon name={item.icon} />
      {item.label}
    </NavLink>
  );
}

export function AppLayout() {
  const { signOut } = useAuth();

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar__brand">
          <LogoMark />
          <span>
            <strong>Учёт посещаемости</strong>
            <span>Админ-панель</span>
          </span>
        </div>
        <nav className="sidebar__nav" aria-label="Основная навигация">
          {NAV_ITEMS.map((item) => (
            <SidebarLink key={item.to} item={item} />
          ))}
        </nav>
        <div className="sidebar__spacer" />
        <nav className="sidebar__nav">
          <SidebarLink item={PASSWORD_ITEM} />
          <button type="button" className="sidebar__link" onClick={signOut}>
            <Icon name="logout" />
            Выйти
          </button>
        </nav>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}
