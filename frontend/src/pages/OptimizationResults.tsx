import { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'

type OptimizationResult = {
  id: number
  name: string
  created_at: string
}

export default function OptimizationResults() {
  const { isAuthenticated } = useAuth()
  const [items, setItems] = useState<OptimizationResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated) return

    const run = async () => {
      try {
        setLoading(true)
        setError(null)
        const res = await axios.get('/api/v1/optimization-results/')
        setItems(Array.isArray(res.data) ? res.data : res.data.items || [])
      } catch (e: any) {
        setError(e?.response?.data?.detail || e?.message || 'Failed to load optimization results')
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
            Please log in to view optimization results
          </h3>
          <p style={{ color: 'var(--text-disabled)', margin: 0 }}>
            Authentication required to access optimization data
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
          Optimization Results
        </h1>
        <p style={{ 
          color: 'var(--text-muted)', 
          margin: 0,
          fontSize: '1rem'
        }}>
          View parameter optimization results and performance metrics
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
          <div style={{ color: 'var(--text-muted)' }}>Loading optimization results...</div>
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
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎯</div>
              <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-secondary)' }}>
                No optimization results found
              </h3>
              <p style={{ margin: 0 }}>
                Run your first optimization to get started
              </p>
            </div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: 'var(--bg-panel-accent)' }}>
                  <Th>ID</Th>
                  <Th>Name</Th>
                  <Th>Created</Th>
                </tr>
              </thead>
              <tbody>
                {items.map(result => (
                  <tr key={result.id} style={{ borderTop: '1px solid var(--border-primary)' }}>
                    <Td>{result.id}</Td>
                    <Td style={{ fontWeight: '500', color: 'var(--text-primary)' }}>
                      {result.name}
                    </Td>
                    <Td style={{ color: 'var(--text-muted)' }}>
                      {new Date(result.created_at).toLocaleString()}
                    </Td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-primary)',
        borderRadius: '12px',
        padding: '1.5rem',
        marginTop: '2rem',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
      }}>
        <h3 style={{ 
          margin: '0 0 1rem 0', 
          color: 'var(--text-primary)',
          fontSize: '1.25rem',
          fontWeight: '600'
        }}>
          Optimization Features
        </h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '1rem' 
        }}>
          <FeatureCard 
            title="Parameter Estimation" 
            description="Calibrate model parameters"
            icon="🔧"
          />
          <FeatureCard 
            title="Performance Metrics" 
            description="RMSE and convergence analysis"
            icon="📊"
          />
          <FeatureCard 
            title="Sensitivity Analysis" 
            description="Parameter sensitivity studies"
            icon="🎛️"
          />
        </div>
      </div>
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

function FeatureCard({ title, description, icon }: {
  title: string
  description: string
  icon: string
}) {
  return (
    <div style={{
      background: 'var(--bg-panel)',
      border: '1px solid var(--border-primary)',
      borderRadius: '8px',
      padding: '1rem',
      textAlign: 'center'
    }}>
      <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{icon}</div>
      <div style={{ 
        color: 'var(--text-primary)', 
        fontSize: '0.875rem', 
        fontWeight: '600',
        marginBottom: '0.25rem'
      }}>
        {title}
      </div>
      <div style={{ 
        color: 'var(--text-muted)', 
        fontSize: '0.75rem' 
      }}>
        {description}
      </div>
    </div>
  )
}
