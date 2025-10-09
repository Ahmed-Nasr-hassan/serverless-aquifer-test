import { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'

export default function Dashboard() {
  const { isAuthenticated } = useAuth()
  const [stats, setStats] = useState({
    simulations: 0,
    modelInputs: 0,
    wells: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated) return

    const fetchStats = async () => {
      try {
        const [simRes, modelRes] = await Promise.all([
          axios.get('/api/v1/simulations/'),
          axios.get('/api/v1/model-inputs/')
        ])
        
        setStats({
          simulations: Array.isArray(simRes.data) ? simRes.data.length : 0,
          modelInputs: Array.isArray(modelRes.data) ? modelRes.data.length : 0,
          wells: 0 // Placeholder
        })
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [isAuthenticated])

  if (!isAuthenticated) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '400px',
        background: 'var(--bg-card)',
        borderRadius: '12px',
        border: '1px solid var(--border-primary)'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h3 style={{ color: 'var(--text-muted)', margin: '0 0 1rem 0' }}>
            Please log in to view dashboard
          </h3>
          <p style={{ color: 'var(--text-disabled)', margin: 0 }}>
            Authentication required to access data
          </p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ 
          margin: '0 0 0.5rem 0', 
          color: 'var(--text-primary)',
          fontSize: '2rem',
          fontWeight: '700'
        }}>
          Dashboard
        </h1>
        <p style={{ 
          color: 'var(--text-muted)', 
          margin: 0,
          fontSize: '1rem'
        }}>
          Welcome to the Aquifer Console. Monitor your simulations and data.
        </p>
      </div>

      {loading ? (
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '200px',
          background: 'var(--bg-card)',
          borderRadius: '12px',
          border: '1px solid var(--border-primary)'
        }}>
          <div style={{ color: 'var(--text-muted)' }}>Loading dashboard...</div>
        </div>
      ) : (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '1.5rem',
          marginBottom: '2rem'
        }}>
          <StatCard 
            title="Simulations" 
            value={stats.simulations} 
            icon="⚡"
            color="var(--blue-500)"
            description="Total simulations run"
          />
          <StatCard 
            title="Model Inputs" 
            value={stats.modelInputs} 
            icon="📋"
            color="var(--success)"
            description="Data submissions"
          />
          <StatCard 
            title="Wells" 
            value={stats.wells} 
            icon="🏗️"
            color="var(--warning)"
            description="Well configurations"
          />
        </div>
      )}

      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-primary)',
        borderRadius: '12px',
        padding: '1.5rem',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
      }}>
        <h3 style={{ 
          margin: '0 0 1rem 0', 
          color: 'var(--text-primary)',
          fontSize: '1.25rem',
          fontWeight: '600'
        }}>
          Quick Actions
        </h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '1rem' 
        }}>
          <ActionButton 
            title="Create Simulation" 
            description="Start a new simulation"
            icon="⚡"
            onClick={() => window.location.href = '/simulations'}
          />
          <ActionButton 
            title="Upload Data" 
            description="Submit model inputs"
            icon="📋"
            onClick={() => window.location.href = '/model-inputs'}
          />
          <ActionButton 
            title="View Wells" 
            description="Manage well data"
            icon="🏗️"
            disabled
          />
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon, color, description }: {
  title: string
  value: number
  icon: string
  color: string
  description: string
}) {
  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-primary)',
      borderRadius: '12px',
      padding: '1.5rem',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      transition: 'transform 0.2s ease',
      cursor: 'pointer'
    }}
    onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
    onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
    >
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
        <div style={{
          fontSize: '1.5rem',
          marginRight: '0.75rem'
        }}>
          {icon}
        </div>
        <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', fontWeight: '500' }}>
          {title}
        </div>
      </div>
      <div style={{ 
        fontSize: '2.5rem', 
        fontWeight: '700', 
        color: color,
        marginBottom: '0.5rem'
      }}>
        {value}
      </div>
      <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
        {description}
      </div>
    </div>
  )
}

function ActionButton({ title, description, icon, onClick, disabled }: {
  title: string
  description: string
  icon: string
  onClick?: () => void
  disabled?: boolean
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        background: disabled ? 'var(--bg-panel)' : 'var(--bg-card)',
        border: '1px solid var(--border-primary)',
        borderRadius: '8px',
        padding: '1rem',
        textAlign: 'left',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.6 : 1,
        transition: 'all 0.2s ease',
        width: '100%'
      }}
      onMouseEnter={(e) => {
        if (!disabled) {
          e.currentTarget.style.background = 'var(--bg-panel-accent)'
          e.currentTarget.style.borderColor = 'var(--border-accent)'
        }
      }}
      onMouseLeave={(e) => {
        if (!disabled) {
          e.currentTarget.style.background = 'var(--bg-card)'
          e.currentTarget.style.borderColor = 'var(--border-primary)'
        }
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '0.5rem' }}>
        <span style={{ fontSize: '1.25rem', marginRight: '0.5rem' }}>{icon}</span>
        <div style={{ 
          color: 'var(--text-primary)', 
          fontSize: '0.875rem', 
          fontWeight: '600' 
        }}>
          {title}
        </div>
      </div>
      <div style={{ 
        color: 'var(--text-muted)', 
        fontSize: '0.75rem' 
      }}>
        {description}
      </div>
    </button>
  )
}


