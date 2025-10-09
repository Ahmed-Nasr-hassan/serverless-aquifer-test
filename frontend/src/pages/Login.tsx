import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'

export default function Login() {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('any')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const { isDarkMode, toggleTheme } = useTheme()
  const navigate = useNavigate()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')
    
    try {
      const success = await login(username, password)
      if (success) {
        navigate('/')
      } else {
        setMessage('Invalid username or password')
      }
    } catch (error: any) {
      setMessage(error?.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
            <div style={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center', 
              minHeight: '100vh',
              background: 'var(--bg-secondary)',
              padding: '1rem'
            }}>
      <div style={{
        width: '100%',
        maxWidth: '400px',
        background: 'var(--bg-card)',
        border: '1px solid var(--border-primary)',
        borderRadius: '16px',
        padding: '2rem',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
        position: 'relative'
      }}>
        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
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
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ 
            margin: '0 0 0.5rem 0', 
            color: 'var(--text-primary)',
            fontSize: '1.875rem',
            fontWeight: '700'
          }}>
            Welcome Back
          </h1>
          <p style={{ 
            color: 'var(--text-muted)', 
            margin: 0,
            fontSize: '0.875rem'
          }}>
            Sign in to Aquifer Console
          </p>
        </div>

        <form onSubmit={submit}>
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '0.5rem', 
              color: 'var(--text-secondary)',
              fontSize: '0.875rem',
              fontWeight: '500'
            }}>
              Username
            </label>
            <input 
              value={username} 
              onChange={e => setUsername(e.target.value)} 
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                border: '1px solid var(--border-primary)',
                background: 'var(--bg-tertiary)',
                color: 'var(--text-primary)',
                fontSize: '0.875rem',
                boxSizing: 'border-box'
              }}
              placeholder="Enter username"
              required
            />
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '0.5rem', 
              color: 'var(--text-secondary)',
              fontSize: '0.875rem',
              fontWeight: '500'
            }}>
              Password
            </label>
            <input 
              type="password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                border: '1px solid var(--border-primary)',
                background: 'var(--bg-tertiary)',
                color: 'var(--text-primary)',
                fontSize: '0.875rem',
                boxSizing: 'border-box'
              }}
              placeholder="Enter password"
              required
            />
          </div>

          <button 
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
                      background: loading ? 'var(--text-disabled)' : 'var(--blue-500)',
              color: 'white',
              border: 'none',
              padding: '0.875rem 1rem',
              borderRadius: '8px',
              fontSize: '0.875rem',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease',
              marginBottom: '1rem'
            }}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>

          {message && (
            <div style={{ 
              padding: '0.75rem 1rem',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.2)',
              borderRadius: '8px',
              color: 'var(--error)',
              fontSize: '0.875rem',
              textAlign: 'center'
            }}>
              {message}
            </div>
          )}
        </form>

        <div style={{ 
          marginTop: '1.5rem', 
          padding: '1rem',
          background: 'var(--bg-panel)',
          borderRadius: '8px',
          border: '1px solid var(--border-primary)'
        }}>
          <div style={{ 
            color: 'var(--text-muted)', 
            fontSize: '0.75rem',
            marginBottom: '0.5rem',
            fontWeight: '500'
          }}>
            Demo Credentials:
          </div>
          <div style={{ 
            color: 'var(--text-secondary)', 
            fontSize: '0.75rem',
            fontFamily: 'monospace'
          }}>
            Username: admin<br />
            Password: any
          </div>
        </div>
      </div>
    </div>
  )
}


