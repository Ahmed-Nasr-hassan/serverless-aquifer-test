import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface ThemeContextType {
  isDarkMode: boolean
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check localStorage first, then system preference
    const saved = localStorage.getItem('theme')
    if (saved) {
      return saved === 'dark'
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    // Update CSS variables based on theme
    const root = document.documentElement
    
    if (isDarkMode) {
      // Dark theme colors
      root.style.setProperty('--bg-primary', '#0a0f1c')
      root.style.setProperty('--bg-secondary', '#0f172a')
      root.style.setProperty('--bg-tertiary', '#1e293b')
      root.style.setProperty('--bg-panel', '#0f1419')
      root.style.setProperty('--bg-panel-accent', '#1a2332')
      root.style.setProperty('--bg-card', '#111827')
      
      root.style.setProperty('--text-primary', '#f8fafc')
      root.style.setProperty('--text-secondary', '#cbd5e1')
      root.style.setProperty('--text-muted', '#94a3b8')
      root.style.setProperty('--text-disabled', '#64748b')
      
      root.style.setProperty('--border-primary', '#1e293b')
      root.style.setProperty('--border-secondary', '#334155')
      root.style.setProperty('--border-accent', '#475569')
      
      root.style.setProperty('--background', 'linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 50%, #0c1220 100%)')
    } else {
      // Light theme colors
      root.style.setProperty('--bg-primary', '#f8fafc')
      root.style.setProperty('--bg-secondary', '#f1f5f9')
      root.style.setProperty('--bg-tertiary', '#e2e8f0')
      root.style.setProperty('--bg-panel', '#ffffff')
      root.style.setProperty('--bg-panel-accent', '#f8fafc')
      root.style.setProperty('--bg-card', '#ffffff')
      
      root.style.setProperty('--text-primary', '#1e293b')
      root.style.setProperty('--text-secondary', '#475569')
      root.style.setProperty('--text-muted', '#64748b')
      root.style.setProperty('--text-disabled', '#94a3b8')
      
      root.style.setProperty('--border-primary', '#e2e8f0')
      root.style.setProperty('--border-secondary', '#cbd5e1')
      root.style.setProperty('--border-accent', '#94a3b8')
      
      root.style.setProperty('--background', 'linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 50%, #e2e8f0 100%)')
    }
    
    // Update body background
    document.body.style.background = 'var(--background)'
    
    // Save to localStorage
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light')
  }, [isDarkMode])

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode)
  }

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}
