import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { useEffect } from 'react'

const BOOK = '/step/10'

const items = [
  { to: '/', label: 'Учёба', icon: <path d="M4 6h16M4 12h16M4 18h10" /> },
  { to: '/step/10', label: 'Книга', icon: <path d="M12 6.5C10.2 5.2 7.6 4.7 4 5v13c3.6-.3 6.2.2 8 1.5 1.8-1.3 4.4-1.8 8-1.5V5c-3.6-.3-6.2.2-8 1.5zm0 0v13" /> },
  { to: '/journal', label: 'Журнал', icon: <path d="M6 3h12a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zm3 5h6M9 12h6M9 16h4" /> },
  { to: '/risk', label: 'Риск', icon: <path d="M12 3l9 16H3L12 3zm0 6v4m0 3v1" /> },
  { to: '/reference', label: 'Справка', icon: <path d="M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zm0-5v-1c0-1.5 2.5-2 2.5-4a2.5 2.5 0 0 0-5 0M12 18.5v.5" /> },
]

export function Layout() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])
  // Учебник — это ступень 10: его экраны подсвечивают «Книгу», остальные ступени — «Учёбу».
  const inBook = pathname === BOOK || pathname.startsWith(BOOK + '/')
  const active = (to: string, isActive: boolean) => {
    if (to === BOOK) return inBook
    if (to === '/') return isActive || (pathname.startsWith('/step') && !inBook)
    return isActive
  }
  return (
    <div className="app">
      <nav className="nav" aria-label="Основное меню">
        <div className="brand">Трейдинг с нуля</div>
        {items.map((it) => (
          <NavLink key={it.to} to={it.to} end={it.to === '/'} className={({ isActive }) => (active(it.to, isActive) ? 'active' : '')}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              {it.icon}
            </svg>
            <span>{it.label}</span>
          </NavLink>
        ))}
      </nav>
      <main className="main">
        <div className="container">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
