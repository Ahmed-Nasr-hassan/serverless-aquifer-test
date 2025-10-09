import { useEffect, useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

type Model = {
  id: number
  name: string
  description: string
  status: 'active' | 'inactive' | 'running' | 'error'
  lastRun?: string
  createdAt: string
  modelType: 'aquifer' | 'well' | 'optimization'
}

export default function Models() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [models, setModels] = useState<Model[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newModel, setNewModel] = useState({
    name: '',
    description: '',
    modelType: 'aquifer' as 'aquifer' | 'well' | 'optimization'
  })
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    if (!isAuthenticated) return

    const fetchModels = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // First try to load from localStorage
        const savedModels = localStorage.getItem('aquifer-models')
        if (savedModels) {
          const parsedModels = JSON.parse(savedModels)
          setModels(parsedModels)
          setLoading(false)
          return
        }
        
        // If no saved models, create default mock data
        const mockModels: Model[] = [
          {
            id: 1,
            name: 'Aquifer Model Alpha',
            description: 'Primary aquifer simulation model for groundwater flow analysis',
            status: 'active',
            lastRun: '2024-01-15T10:30:00Z',
            createdAt: '2024-01-10T09:00:00Z',
            modelType: 'aquifer'
          },
          {
            id: 2,
            name: 'Well Configuration Beta',
            description: 'Multi-well pumping test configuration and analysis',
            status: 'running',
            lastRun: '2024-01-15T14:20:00Z',
            createdAt: '2024-01-12T11:15:00Z',
            modelType: 'well'
          },
          {
            id: 3,
            name: 'Optimization Model Gamma',
            description: 'Parameter optimization for hydraulic conductivity estimation',
            status: 'inactive',
            lastRun: '2024-01-14T16:45:00Z',
            createdAt: '2024-01-08T14:30:00Z',
            modelType: 'optimization'
          }
        ]
        
        // Save mock data to localStorage
        localStorage.setItem('aquifer-models', JSON.stringify(mockModels))
        setModels(mockModels)
      } catch (e: any) {
        setError(e?.response?.data?.detail || e?.message || 'Failed to load models')
      } finally {
        setLoading(false)
      }
    }

    fetchModels()
  }, [isAuthenticated])

  // Save models to localStorage whenever models state changes
  useEffect(() => {
    if (models.length > 0) {
      localStorage.setItem('aquifer-models', JSON.stringify(models))
    }
  }, [models])

  const handleCreateModel = async () => {
    if (!newModel.name.trim() || !newModel.description.trim()) {
      setError('Please fill in all required fields')
      return
    }

    try {
      setCreating(true)
      setError(null)
      
      // Generate unique ID based on existing models
      const existingIds = models.map(m => m.id)
      const newId = existingIds.length > 0 ? Math.max(...existingIds) + 1 : 1
      
      // Create new model with proper ID and timestamp
      const createdModel: Model = {
        id: newId,
        name: newModel.name.trim(),
        description: newModel.description.trim(),
        status: 'active',
        createdAt: new Date().toISOString(),
        modelType: newModel.modelType
      }
      
      // Add to models list (this will trigger localStorage save via useEffect)
      const updatedModels = [...models, createdModel]
      setModels(updatedModels)
      
      // Clear form and close modal
      setNewModel({ name: '', description: '', modelType: 'aquifer' })
      setShowCreateModal(false)
      
      // Navigate to the new model
      navigate(`/models/${createdModel.id}`)
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to create model')
    } finally {
      setCreating(false)
    }
  }

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
            Please log in to view models
          </h3>
          <p style={{ color: 'var(--text-disabled)', margin: 0 }}>
            Authentication required to access models
          </p>
        </div>
      </div>
    )
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'var(--success)'
      case 'running':
        return 'var(--info)'
      case 'inactive':
        return 'var(--text-muted)'
      case 'error':
        return 'var(--error)'
      default:
        return 'var(--text-muted)'
    }
  }

  const getModelIcon = (modelType: string) => {
    switch (modelType) {
      case 'aquifer':
        return '🌊'
      case 'well':
        return '🏗️'
      case 'optimization':
        return '🎯'
      default:
        return '📊'
    }
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
            Models
          </h1>
          <button 
            onClick={() => setShowCreateModal(true)}
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
            + Create Model
          </button>
        </div>
        <p style={{ 
          color: 'var(--text-muted)', 
          margin: 0,
          fontSize: '1rem'
        }}>
          Manage your aquifer simulation models and configurations
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
          <div style={{ color: 'var(--text-muted)' }}>Loading models...</div>
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
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
          gap: '1.5rem'
        }}>
          {models.length === 0 ? (
            <div style={{
              gridColumn: '1 / -1',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '300px',
              background: 'var(--bg-card)',
              borderRadius: '12px',
              border: '1px solid var(--border-primary)'
            }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📊</div>
                <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-secondary)' }}>
                  No models found
                </h3>
                <p style={{ margin: 0, color: 'var(--text-muted)' }}>
                  Create your first model to get started
                </p>
              </div>
            </div>
          ) : (
            models.map(model => (
              <ModelCard 
                key={model.id} 
                model={model} 
                onOpen={() => navigate(`/models/${model.id}`)}
                onDelete={() => {
                  if (confirm('Are you sure you want to delete this model?')) {
                    const updatedModels = models.filter(m => m.id !== model.id)
                    setModels(updatedModels)
                    // localStorage will be updated automatically via useEffect
                  }
                }}
              />
            ))
          )}
        </div>
      )}

      {/* Create Model Modal */}
      {showCreateModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000,
          padding: '1rem'
        }}>
          <div style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-primary)',
            borderRadius: '12px',
            padding: '2rem',
            width: '100%',
            maxWidth: '500px',
            boxShadow: '0 20px 25px rgba(0, 0, 0, 0.1)'
          }}>
            <h2 style={{
              margin: '0 0 1.5rem 0',
              color: 'var(--text-primary)',
              fontSize: '1.5rem',
              fontWeight: '600'
            }}>
              Create New Model
            </h2>

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.5rem',
                color: 'var(--text-secondary)',
                fontSize: '0.875rem',
                fontWeight: '500'
              }}>
                Model Name *
              </label>
              <input
                type="text"
                value={newModel.name}
                onChange={(e) => setNewModel({ ...newModel, name: e.target.value })}
                placeholder="Enter model name"
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
                Description *
              </label>
              <textarea
                value={newModel.description}
                onChange={(e) => setNewModel({ ...newModel, description: e.target.value })}
                placeholder="Enter model description"
                rows={3}
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  borderRadius: '8px',
                  border: '1px solid var(--border-primary)',
                  background: 'var(--bg-tertiary)',
                  color: 'var(--text-primary)',
                  fontSize: '0.875rem',
                  boxSizing: 'border-box',
                  resize: 'vertical'
                }}
              />
            </div>

            <div style={{ marginBottom: '2rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.5rem',
                color: 'var(--text-secondary)',
                fontSize: '0.875rem',
                fontWeight: '500'
              }}>
                Model Type
              </label>
              <select
                value={newModel.modelType}
                onChange={(e) => setNewModel({ ...newModel, modelType: e.target.value as any })}
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
              >
                <option value="aquifer">🌊 Aquifer Model</option>
                <option value="well">🏗️ Well Model</option>
                <option value="optimization">🎯 Optimization Model</option>
              </select>
            </div>

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
              <button
                onClick={() => {
                  setShowCreateModal(false)
                  setNewModel({ name: '', description: '', modelType: 'aquifer' })
                  setError(null)
                }}
                style={{
                  background: 'transparent',
                  color: 'var(--text-secondary)',
                  border: '1px solid var(--border-primary)',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '8px',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleCreateModel}
                disabled={creating}
                style={{
                  background: creating ? 'var(--text-disabled)' : 'var(--blue-500)',
                  color: 'white',
                  border: 'none',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '8px',
                  fontSize: '0.875rem',
                  fontWeight: '600',
                  cursor: creating ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                {creating ? 'Creating...' : 'Create Model'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function ModelCard({ model, onOpen, onDelete }: {
  model: Model
  onOpen: () => void
  onDelete: () => void
}) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'var(--success)'
      case 'running':
        return 'var(--info)'
      case 'inactive':
        return 'var(--text-muted)'
      case 'error':
        return 'var(--error)'
      default:
        return 'var(--text-muted)'
    }
  }

  const getModelIcon = (modelType: string) => {
    switch (modelType) {
      case 'aquifer':
        return '🌊'
      case 'well':
        return '🏗️'
      case 'optimization':
        return '🎯'
      default:
        return '📊'
    }
  }

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-primary)',
      borderRadius: '12px',
      padding: '1.5rem',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)',
      transition: 'all 0.2s ease',
      cursor: 'pointer'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-2px)'
      e.currentTarget.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.1)'
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0)'
      e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.05)'
    }}
    onClick={onOpen}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ fontSize: '1.5rem' }}>
            {getModelIcon(model.modelType)}
          </div>
          <div>
            <h3 style={{ 
              margin: 0, 
              fontSize: '1.125rem', 
              fontWeight: '600',
              color: 'var(--text-primary)'
            }}>
              {model.name}
            </h3>
            <div style={{ 
              fontSize: '0.75rem', 
              color: 'var(--text-muted)',
              textTransform: 'capitalize'
            }}>
              {model.modelType} Model
            </div>
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: getStatusColor(model.status)
          }} />
          <span style={{
            fontSize: '0.75rem',
            color: getStatusColor(model.status),
            textTransform: 'capitalize',
            fontWeight: '500'
          }}>
            {model.status}
          </span>
        </div>
      </div>

      {/* Description */}
      <p style={{
        margin: '0 0 1rem 0',
        fontSize: '0.875rem',
        color: 'var(--text-secondary)',
        lineHeight: '1.5'
      }}>
        {model.description}
      </p>

      {/* Footer */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        paddingTop: '1rem',
        borderTop: '1px solid var(--border-primary)'
      }}>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          {model.lastRun ? (
            <>Last run: {new Date(model.lastRun).toLocaleDateString()}</>
          ) : (
            <>Created: {new Date(model.createdAt).toLocaleDateString()}</>
          )}
        </div>
        
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onOpen()
            }}
            style={{
              background: 'var(--blue-500)',
              color: 'white',
              border: 'none',
              padding: '0.25rem 0.75rem',
              borderRadius: '4px',
              fontSize: '0.75rem',
              cursor: 'pointer'
            }}
          >
            Open
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onDelete()
            }}
            style={{
              background: 'var(--error)',
              color: 'white',
              border: 'none',
              padding: '0.25rem 0.75rem',
              borderRadius: '4px',
              fontSize: '0.75rem',
              cursor: 'pointer'
            }}
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  )
}
