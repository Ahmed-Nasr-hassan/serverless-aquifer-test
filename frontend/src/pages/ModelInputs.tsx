import { useEffect, useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

type ModelInput = {
  id: number
  user_id: string
  model_id: string
  created_at: string
}

export default function ModelInputs() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [items, setItems] = useState<ModelInput[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this model input?')) return
    
    try {
      await axios.delete(`/api/v1/model-inputs/${id}`)
      setItems(items.filter(item => item.id !== id))
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to delete model input')
    }
  }

  useEffect(() => {
    if (!isAuthenticated) return

    const run = async () => {
      try {
        setLoading(true)
        setError(null)
        const res = await axios.get('/api/v1/model-inputs/')
        setItems(Array.isArray(res.data) ? res.data : res.data.items || [])
      } catch (e: any) {
        setError(e?.response?.data?.detail || e?.message || 'Failed to load model inputs')
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
            Please log in to view model inputs
          </h3>
          <p style={{ color: 'var(--text-disabled)', margin: 0 }}>
            Authentication required to access model input data
          </p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <h1 style={{ 
            margin: 0, 
            color: 'var(--text-primary)',
            fontSize: '2rem',
            fontWeight: '700'
          }}>
            Model Inputs
          </h1>
          <button 
            onClick={() => navigate('/model-inputs/create')}
            style={{
              background: 'var(--blue-500)',
              color: 'white',
              border: 'none',
              padding: '0.75rem 1.5rem',
              borderRadius: '8px',
              fontSize: '0.875rem',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            + Create Model Input
          </button>
        </div>
        <p style={{ 
          color: 'var(--text-muted)', 
          margin: 0,
          fontSize: '1rem'
        }}>
          Manage your aquifer model input data and configurations
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
          <div style={{ color: 'var(--text-muted)' }}>Loading model inputs...</div>
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
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📋</div>
              <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-secondary)' }}>
                No model inputs found
              </h3>
              <p style={{ margin: 0 }}>
                Upload your first model input to get started
              </p>
            </div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr style={{ background: 'var(--bg-panel-accent)' }}>
                          <Th>ID</Th>
                          <Th>User ID</Th>
                          <Th>Model ID</Th>
                          <Th>Created</Th>
                          <Th>Actions</Th>
                        </tr>
                      </thead>
              <tbody>
                        {items.map(mi => (
                          <tr key={mi.id} style={{ borderTop: '1px solid var(--border-primary)' }}>
                            <Td>{mi.id}</Td>
                            <Td style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                              {mi.user_id}
                            </Td>
                            <Td style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                              {mi.model_id}
                            </Td>
                            <Td style={{ color: 'var(--text-muted)' }}>
                              {new Date(mi.created_at).toLocaleString()}
                            </Td>
                            <Td>
                              <div style={{ display: 'flex', gap: '0.5rem' }}>
                                <button
                                  onClick={() => navigate(`/model-inputs/edit/${mi.id}`)}
                                  style={{
                                    background: 'var(--blue-500)',
                                    color: 'white',
                                    border: 'none',
                                    padding: '0.25rem 0.5rem',
                                    borderRadius: '4px',
                                    fontSize: '0.75rem',
                                    cursor: 'pointer'
                                  }}
                                >
                                  Edit
                                </button>
                                <button
                                  onClick={() => handleDelete(mi.id)}
                                  style={{
                                    background: 'var(--error)',
                                    color: 'white',
                                    border: 'none',
                                    padding: '0.25rem 0.5rem',
                                    borderRadius: '4px',
                                    fontSize: '0.75rem',
                                    cursor: 'pointer'
                                  }}
                                >
                                  Delete
                                </button>
                              </div>
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


