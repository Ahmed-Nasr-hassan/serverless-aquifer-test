import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'
import { useState, useEffect } from 'react'

export default function RootLayout() {
  const { user, logout, isAuthenticated, loading } = useAuth()
  const { isDarkMode, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
      if (window.innerWidth >= 768) {
        setMobileMenuOpen(false)
      }
    }
    
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

          if (loading) {
            return (
              <div style={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                height: '100vh',
                background: 'var(--bg-secondary)'
              }}>
                <div style={{ color: 'var(--text-muted)' }}>Loading...</div>
              </div>
            )
          }

  if (!isAuthenticated) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: 'var(--bg-secondary)'
      }}>
        <div style={{ 
          textAlign: 'center',
          background: 'var(--bg-card)',
          padding: '2rem',
          borderRadius: '12px',
          border: '1px solid var(--border-primary)',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}>
          <h2 style={{ margin: '0 0 1rem 0', color: 'var(--text-primary)' }}>Authentication Required</h2>
          <p style={{ color: 'var(--text-muted)', margin: '0 0 1.5rem 0' }}>
            Please log in to access the Aquifer Console
          </p>
                  <button 
                    onClick={() => navigate('/login')}
                    style={{
                      background: 'var(--blue-500)',
                      color: 'white',
                      border: 'none',
                      padding: '0.75rem 1.5rem',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontSize: '1rem',
                      fontWeight: '500'
                    }}
                  >
                    Go to Login
                  </button>
        </div>
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', width: '100%' }}>
      {/* Mobile Overlay */}
      {isMobile && mobileMenuOpen && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            zIndex: 998
          }}
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside style={{ 
        background: 'var(--bg-panel)', 
        borderRight: '1px solid var(--border-primary)',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '2px 0 8px rgba(0, 0, 0, 0.05)',
        width: isMobile ? '280px' : (sidebarCollapsed ? '64px' : '280px'),
        position: isMobile ? 'fixed' : 'relative',
        top: 0,
        left: 0,
        height: '100vh',
        zIndex: 999,
        transform: isMobile ? (mobileMenuOpen ? 'translateX(0)' : 'translateX(-100%)') : 'translateX(0)',
        transition: 'all 0.3s ease',
        flexShrink: 0,
        margin: 0,
        padding: 0
      }}>
        <div style={{ 
          padding: '1.5rem 1.25rem', 
          borderBottom: '1px solid var(--border-primary)',
          background: 'var(--bg-panel-accent)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          {!sidebarCollapsed && (
            <div>
              <div style={{ 
                fontWeight: '800', 
                fontSize: '1.25rem',
                letterSpacing: '0.5px',
                color: 'var(--text-primary)',
                marginBottom: '0.25rem'
              }}>
                Aquifer Console
              </div>
              <div style={{ 
                fontSize: '0.75rem', 
                color: 'var(--text-muted)',
                fontWeight: '500'
              }}>
                Where Technology Meets Groundwater
              </div>
            </div>
          )}
          
          {/* Collapse Toggle Button */}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            style={{
              background: 'transparent',
              border: '1px solid var(--border-primary)',
              borderRadius: '6px',
              padding: '0.5rem',
              cursor: 'pointer',
              color: 'var(--text-secondary)',
              transition: 'all 0.2s ease',
              display: isMobile ? 'none' : 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {sidebarCollapsed ? '→' : '←'}
          </button>
        </div>
        
        <nav style={{ padding: '1rem 0.75rem', flex: 1 }}>
          <NavItem to="/" label="Dashboard" icon="📊" collapsed={sidebarCollapsed} />
          <NavItem to="/models" label="Models" icon="🔬" collapsed={sidebarCollapsed} />
          
          <div style={{ height: '1rem' }} />
          
          <NavItem to="/simulations" label="Simulations" icon="⚡" collapsed={sidebarCollapsed} />
        </nav>
        
        <div style={{ 
          padding: '1rem', 
          borderTop: '1px solid var(--border-primary)',
          background: 'var(--bg-panel-accent)'
        }}>
          {!sidebarCollapsed && (
            <div style={{ 
              color: 'var(--text-muted)', 
              fontSize: '0.75rem',
              marginBottom: '0.5rem'
            }}>
              Logged in as: <strong style={{ color: 'var(--text-primary)' }}>{user?.username}</strong>
            </div>
          )}
          <button 
            onClick={handleLogout}
            style={{
              background: 'transparent',
              color: 'var(--text-muted)',
              border: '1px solid var(--border-primary)',
              padding: '0.5rem 0.75rem',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.75rem',
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: sidebarCollapsed ? 'center' : 'flex-start',
              gap: '0.5rem'
            }}
            title={sidebarCollapsed ? 'Logout' : ''}
          >
            <span>🚪</span>
            {!sidebarCollapsed && 'Logout'}
          </button>
        </div>
      </aside>
      
      <main style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        flex: 1,
        minHeight: '100vh',
        overflow: 'hidden'
      }}>
        <Topbar 
          onMenuToggle={() => setMobileMenuOpen(!mobileMenuOpen)}
          isMobile={isMobile}
        />
        <div style={{ padding: '1.5rem', flex: 1 }}>
          <Outlet />
        </div>
      </main>
    </div>
  )
}

function Topbar({ onMenuToggle, isMobile }: { onMenuToggle: () => void; isMobile: boolean }) {
  const { isDarkMode, toggleTheme } = useTheme()
  
  return (
    <div style={{
      height: '64px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 1.5rem',
      borderBottom: '1px solid var(--border-primary)',
      background: 'linear-gradient(90deg, var(--bg-panel), var(--bg-panel-accent))',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
    }}>
      <div style={{ 
        display: 'flex',
        alignItems: 'center',
        gap: '1rem'
      }}>
        {/* Mobile Menu Button */}
        {isMobile && (
          <button
            onClick={onMenuToggle}
            style={{
              background: 'transparent',
              border: '1px solid var(--border-primary)',
              borderRadius: '8px',
              padding: '0.5rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-secondary)',
              transition: 'all 0.2s ease'
            }}
            title="Toggle menu"
          >
            ☰
          </button>
        )}
        
        <div style={{ 
          fontWeight: '600', 
          fontSize: '1.125rem',
          color: 'var(--text-primary)'
        }}>
          Aquifer API Dashboard
        </div>
      </div>
      
      <div style={{ 
        display: 'flex', 
        alignItems: 'center',
        gap: '0.75rem'
      }}>
        <button
          onClick={toggleTheme}
          style={{
            background: 'transparent',
            border: '1px solid var(--border-primary)',
            borderRadius: '8px',
            padding: '0.5rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-secondary)',
            transition: 'all 0.2s ease'
          }}
          title={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {isDarkMode ? '☀️' : '🌙'}
        </button>
        <div style={{
          background: 'var(--success)',
          color: 'white',
          padding: '0.25rem 0.75rem',
          borderRadius: '12px',
          fontSize: '0.75rem',
          fontWeight: '500'
        }}>
          ● Connected
        </div>
      </div>
    </div>
  )
}

function NavItem({ to, label, icon, disabled, collapsed }: { 
  to: string; 
  label: string; 
  icon: string; 
  disabled?: boolean;
  collapsed?: boolean;
}) {
  if (disabled) {
    return (
      <div style={{ 
        opacity: 0.5, 
        padding: '0.75rem 1rem', 
        color: 'var(--text-muted)',
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        borderRadius: '8px',
        margin: '0.25rem 0',
        justifyContent: collapsed ? 'center' : 'flex-start'
      }}>
        <span>{icon}</span>
        {!collapsed && label}
      </div>
    )
  }
  
  return (
    <NavLink
      to={to}
      style={({ isActive }) => ({
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        padding: '0.75rem 1rem',
        margin: '0.25rem 0',
        borderRadius: '8px',
        background: isActive ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
        border: isActive ? '1px solid rgba(59, 130, 246, 0.3)' : '1px solid transparent',
        color: isActive ? 'var(--blue-600)' : 'var(--text-secondary)',
        textDecoration: 'none',
        transition: 'all 0.2s ease',
        fontWeight: isActive ? '500' : '400',
        justifyContent: collapsed ? 'center' : 'flex-start'
      })}
    >
      <span>{icon}</span>
      {!collapsed && label}
    </NavLink>
  )
}


