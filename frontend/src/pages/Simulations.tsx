import { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'

type Simulation = {
  id: number
  name: string
  simulation_type: string
  status: string
  created_at: string
}

export default function Simulations() {
  const { isAuthenticated } = useAuth()
  const [items, setItems] = useState<Simulation[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated) return

    const run = async () => {
      try {
        setLoading(true)
        setError(null)
        const res = await axios.get('/api/v1/simulations/')
        // list endpoint returns array
        setItems(Array.isArray(res.data) ? res.data : res.data.simulations || [])
      } catch (e: any) {
        setError(e?.response?.data?.detail || e?.message || 'Failed to load simulations')
      } finally {
        setLoading(false)
      }
    }
    run()
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
            Please log in to view simulations
          </h3>
          <p style={{ color: 'var(--text-disabled)', margin: 0 }}>
            Authentication required to access simulation data
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
          Simulations
        </h1>
        <p style={{ 
          color: 'var(--text-muted)', 
          margin: 0,
          fontSize: '1rem'
        }}>
          Manage and monitor your aquifer simulations
        </p>
      </div>

      {loading && (
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '200px',
          background: 'var(--bg-card)',
          borderRadius: '12px',
          border: '1px solid var(--border-primary)'
        }}>
          <div style={{ color: 'var(--text-muted)' }}>Loading simulations...</div>
        </div>
      )}

      {error && (
        <div style={{ 
          padding: '1rem',
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.2)',
          borderRadius: '8px',
          color: 'var(--error)',
          marginBottom: '1rem'
        }}>
          {error}
        </div>
      )}

      {!loading && !error && (
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-primary)',
          borderRadius: '12px',
          overflow: 'hidden',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}>
          {items.length === 0 ? (
            <div style={{ 
              padding: '3rem', 
              textAlign: 'center',
              color: 'var(--text-muted)'
            }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚡</div>
              <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-secondary)' }}>
                No simulations found
              </h3>
              <p style={{ margin: 0 }}>
                Create your first simulation to get started
              </p>
            </div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: 'var(--bg-panel-accent)' }}>
                  <Th>ID</Th>
                  <Th>Name</Th>
                  <Th>Type</Th>
                  <Th>Status</Th>
                  <Th>Created</Th>
                </tr>
              </thead>
              <tbody>
                {items.map(s => (
                  <tr key={s.id} style={{ borderTop: '1px solid var(--border-primary)' }}>
                    <Td>{s.id}</Td>
                    <Td style={{ fontWeight: '500', color: 'var(--text-primary)' }}>
                      {s.name}
                    </Td>
                    <Td>
                      <StatusBadge status={s.simulation_type} />
                    </Td>
                    <Td>
                      <StatusBadge status={s.status} />
                    </Td>
                    <Td style={{ color: 'var(--text-muted)' }}>
                      {new Date(s.created_at).toLocaleString()}
                    </Td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  )
}

function Th({ children }: { children: any }) {
  return (
    <th style={{ 
      textAlign: 'left', 
      padding: '1rem', 
      color: 'var(--text-primary)',
      fontWeight: '600',
      fontSize: '0.875rem'
    }}>
      {children}
    </th>
  )
}

function Td({ children, style }: { children: any; style?: React.CSSProperties }) {
  return (
    <td style={{ 
      padding: '1rem', 
      color: 'var(--text-secondary)',
      fontSize: '0.875rem',
      ...style
    }}>
      {children}
    </td>
  )
}

function StatusBadge({ status }: { status: string }) {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'var(--warning)'
      case 'running':
        return 'var(--info)'
      case 'completed':
        return 'var(--success)'
      case 'failed':
        return 'var(--error)'
      case 'calibration':
        return 'var(--blue-500)'
      default:
        return 'var(--text-muted)'
    }
  }

  return (
    <span style={{
      background: `${getStatusColor(status)}20`,
      color: getStatusColor(status),
      padding: '0.25rem 0.5rem',
      borderRadius: '6px',
      fontSize: '0.75rem',
      fontWeight: '500',
      textTransform: 'capitalize'
    }}>
      {status}
    </span>
  )
}


