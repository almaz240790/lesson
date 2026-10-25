import { useEffect, useState } from 'react'

export type ThemeSetting = 'system' | 'light' | 'dark'
const KEY = 'theme'

export function readTheme(): ThemeSetting {
  try {
    const v = localStorage.getItem(KEY)
    if (v === 'light' || v === 'dark' || v === 'system') return v
  } catch {
    /* localStorage недоступен */
  }
  return 'system'
}

export function applyTheme(t: ThemeSetting) {
  const root = document.documentElement
  if (t === 'system') root.removeAttribute('data-theme')
  else root.setAttribute('data-theme', t)
}

export function useTheme() {
  const [theme, setThemeState] = useState<ThemeSetting>(readTheme)
  useEffect(() => {
    applyTheme(theme)
  }, [theme])
  const setTheme = (t: ThemeSetting) => {
    try {
      localStorage.setItem(KEY, t)
    } catch {
      /* ignore */
    }
    setThemeState(t)
  }
  return { theme, setTheme }
}

export function useIsDark(): boolean {
  const [dark, setDark] = useState(() => computeDark())
  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    const update = () => setDark(computeDark())
    mq.addEventListener('change', update)
    const obs = new MutationObserver(update)
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    return () => {
      mq.removeEventListener('change', update)
      obs.disconnect()
    }
  }, [])
  return dark
}

function computeDark(): boolean {
  const attr = document.documentElement.getAttribute('data-theme')
  if (attr === 'dark') return true
  if (attr === 'light') return false
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}
