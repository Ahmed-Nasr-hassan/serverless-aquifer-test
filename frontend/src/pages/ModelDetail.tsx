import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'
import { RadialDiscretizationSection, VerticalDiscretizationSection, PumpingWellSection, InitialBoundaryConditionsSection, StressPeriodsSection } from '../components/ModelConfiguration'

interface Model {
  id: string
  name: string
  description: string
  model_type: 'aquifer_test' | 'conceptual' | 'solute_transport' | 'seawater_intrusion' | 'stochastic'
  configuration: any
  status: 'active' | 'inactive' | 'running' | 'error'
  created_at: string
  updated_at?: string
  user_id: string
}

const MODEL_TYPE_LABELS = {
  aquifer_test: 'Aquifer Test Analysis',
  conceptual: 'Conceptual Model',
  solute_transport: 'Solute Transport Model',
  seawater_intrusion: 'Seawater Intrusion Model',
  stochastic: 'Stochastic Model'
}

const MODEL_TYPE_ICONS = {
  aquifer_test: '🔬',
  conceptual: '🧠',
  solute_transport: '🌊',
  seawater_intrusion: '🌊',
  stochastic: '🎲'
}

export default function ModelDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const [model, setModel] = useState<Model | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }

    if (!id) {
      setError('Model ID is required')
      setLoading(false)
      return
    }

    const fetchModel = async () => {
      try {
        const response = await axios.get(`/api/v1/models/${id}`)
        setModel(response.data)
      } catch (err: any) {
        console.error('Failed to fetch model:', err)
        setError(err.response?.data?.detail || 'Failed to fetch model')
      } finally {
        setLoading(false)
      }
    }

    fetchModel()
  }, [id, isAuthenticated, navigate])

  if (!isAuthenticated) {
    return null
  }

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '400px',
        color: 'var(--text-muted)'
      }}>
        Loading model details...
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '400px',
        color: 'var(--error)',
        textAlign: 'center'
      }}>
        <div>
          <h3>Error loading model</h3>
          <p>{error}</p>
          <button 
            onClick={() => navigate('/models')}
            style={{
              background: 'var(--blue-500)',
              color: 'white',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              cursor: 'pointer',
              marginTop: '1rem'
            }}
          >
            Back to Models
          </button>
        </div>
      </div>
    )
  }

  if (!model) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '400px',
        color: 'var(--text-muted)'
      }}>
        Model not found
      </div>
    )
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const renderConfigurationSection = (title: string, data: any, level = 0) => {
    if (!data) return null

    const indentStyle = { marginLeft: `${level * 1}rem` }

    if (typeof data === 'object' && !Array.isArray(data)) {
      return (
        <div key={title} style={indentStyle}>
          <h4 style={{ 
            color: 'var(--text-primary)', 
            margin: '1rem 0 0.5rem 0',
            fontSize: level === 0 ? '1.1rem' : '1rem',
            fontWeight: level === 0 ? '600' : '500'
          }}>
            {title}
          </h4>
          {Object.entries(data).map(([key, value]) => 
            renderConfigurationSection(key, value, level + 1)
          )}
        </div>
      )
    } else if (Array.isArray(data)) {
      return (
        <div key={title} style={indentStyle}>
          <h4 style={{ 
            color: 'var(--text-primary)', 
            margin: '1rem 0 0.5rem 0',
            fontSize: level === 0 ? '1.1rem' : '1rem',
            fontWeight: level === 0 ? '600' : '500'
          }}>
            {title} ({data.length} items)
          </h4>
          {data.map((item, index) => (
            <div key={index} style={{ marginLeft: '1rem', marginBottom: '0.5rem' }}>
              {typeof item === 'object' ? 
                Object.entries(item).map(([key, value]) => 
                  renderConfigurationSection(key, value, level + 2)
                ) :
                <div style={{ color: 'var(--text-muted)' }}>{String(item)}</div>
              }
            </div>
          ))}
        </div>
      )
    } else {
      return (
        <div key={title} style={{ ...indentStyle, marginBottom: '0.25rem' }}>
          <span style={{ color: 'var(--text-primary)', fontWeight: '500' }}>{title}: </span>
          <span style={{ color: 'var(--text-muted)' }}>{String(data)}</span>
        </div>
      )
    }
  }

  return (
    <div style={{ padding: '2rem', color: 'var(--text-primary)' }}>
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
          <button
            onClick={() => navigate('/models')}
            style={{
              background: 'none',
              border: '1px solid var(--border-primary)',
              borderRadius: '6px',
              padding: '0.5rem',
              cursor: 'pointer',
              marginRight: '1rem',
              color: 'var(--text-primary)'
            }}
          >
            ← Back
          </button>
          <div style={{ fontSize: '1.5rem', marginRight: '0.5rem' }}>
            {MODEL_TYPE_ICONS[model.model_type]}
          </div>
          <h1 style={{ margin: 0, fontSize: '2rem', fontWeight: '700' }}>
            {model.name}
          </h1>
        </div>
        
        <div style={{ 
          background: 'var(--bg-card)', 
          border: '1px solid var(--border-primary)', 
          borderRadius: '12px', 
          padding: '1.5rem',
          marginBottom: '1rem'
        }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Type</div>
              <div style={{ fontWeight: '600' }}>{MODEL_TYPE_LABELS[model.model_type]}</div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Status</div>
              <div style={{ 
                fontWeight: '600',
                color: model.status === 'active' ? 'var(--success)' : 
                       model.status === 'error' ? 'var(--error)' : 'var(--warning)'
              }}>
                {model.status.charAt(0).toUpperCase() + model.status.slice(1)}
              </div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Created</div>
              <div style={{ fontWeight: '600' }}>{formatDate(model.created_at)}</div>
            </div>
            {model.updated_at && (
              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Updated</div>
                <div style={{ fontWeight: '600' }}>{formatDate(model.updated_at)}</div>
              </div>
            )}
          </div>
          
          {model.description && (
            <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-primary)' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Description</div>
              <div style={{ color: 'var(--text-primary)' }}>{model.description}</div>
            </div>
          )}
        </div>
      </div>

      {/* Configuration Details */}
      {model.configuration && (
        <div style={{ 
          background: 'var(--bg-card)', 
          border: '1px solid var(--border-primary)', 
          borderRadius: '12px', 
          padding: '1.5rem'
        }}>
          <h2 style={{ 
            margin: '0 0 1.5rem 0', 
            fontSize: '1.5rem', 
            fontWeight: '600',
            color: 'var(--text-primary)'
          }}>
            Model Configuration
          </h2>
          
          <div style={{ 
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
            gap: '1.5rem'
          }}>
            {model.configuration.model_inputs?.radial_discretization && (
              <RadialDiscretizationSection 
                data={model.configuration.model_inputs.radial_discretization}
                editable={false}
              />
            )}
            
            {model.configuration.model_inputs?.vertical_discretization && (
              <VerticalDiscretizationSection 
                data={model.configuration.model_inputs.vertical_discretization}
                editable={false}
              />
            )}

            {model.configuration.model_inputs?.pumping_well && (
              <PumpingWellSection 
                data={model.configuration.model_inputs.pumping_well}
                editable={false}
              />
            )}

                    {model.configuration.model_inputs?.initial_boundary_conditions && (
                      <InitialBoundaryConditionsSection 
                        data={model.configuration.model_inputs.initial_boundary_conditions}
                        editable={false}
                      />
                    )}

                    {model.configuration.model_inputs?.stress_periods && (
                      <StressPeriodsSection 
                        data={model.configuration.model_inputs.stress_periods}
                        editable={false}
                      />
                    )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div style={{ 
        marginTop: '2rem', 
        display: 'flex', 
        gap: '1rem',
        flexWrap: 'wrap'
      }}>
        <button
          onClick={() => navigate(`/models/${model.id}/edit`)}
          style={{
            background: 'var(--blue-500)',
            color: 'white',
            border: 'none',
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: '600'
          }}
        >
          Edit Model
        </button>
        
        <button
          onClick={() => navigate(`/simulations?model=${model.id}`)}
          style={{
            background: 'var(--success)',
            color: 'white',
            border: 'none',
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: '600'
          }}
        >
          Run Simulation
        </button>
        
        <button
          onClick={async () => {
            if (window.confirm('Are you sure you want to delete this model? This action cannot be undone.')) {
              try {
                await axios.delete(`/api/v1/models/${model.id}`)
                navigate('/models')
              } catch (err: any) {
                console.error('Failed to delete model:', err)
                alert(err.response?.data?.detail || 'Failed to delete model')
              }
            }
          }}
          style={{
            background: 'var(--error)',
            color: 'white',
            border: 'none',
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: '600'
          }}
        >
          Delete Model
        </button>
      </div>
    </div>
  )
}