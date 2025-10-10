import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'
import { RadialDiscretizationSection, VerticalDiscretizationSection, PumpingWellSection, InitialBoundaryConditionsSection, StressPeriodsSection, HydraulicParametersSection, HydraulicConductivitySection } from '../components/ModelConfiguration'

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

export default function EditModel() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const [model, setModel] = useState<Model | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    status: 'active' as 'active' | 'inactive' | 'running' | 'error',
    configuration: {} as any
  })

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
        const modelData = response.data
        setModel(modelData)
        setFormData({
          name: modelData.name,
          description: modelData.description || '',
          status: modelData.status,
          configuration: modelData.configuration || {}
        })
      } catch (err: any) {
        console.error('Failed to fetch model:', err)
        setError(err.response?.data?.detail || 'Failed to fetch model')
      } finally {
        setLoading(false)
      }
    }

    fetchModel()
  }, [id, isAuthenticated, navigate])

  const handleSave = async () => {
    if (!model) return

    setSaving(true)
    try {
      await axios.put(`/api/v1/models/${model.id}`, formData)
      navigate(`/models/${model.id}`)
    } catch (err: any) {
      console.error('Failed to update model:', err)
      setError(err.response?.data?.detail || 'Failed to update model')
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    if (model) {
      navigate(`/models/${model.id}`)
    } else {
      navigate('/models')
    }
  }

  const updateConfiguration = (path: string[], value: any) => {
    const newConfig = { ...formData.configuration }
    let current = newConfig
    
    // Navigate to the nested object
    for (let i = 0; i < path.length - 1; i++) {
      if (!current[path[i]]) {
        current[path[i]] = {}
      }
      current = current[path[i]]
    }
    
    // Set the final value
    current[path[path.length - 1]] = value
    
    setFormData(prev => ({
      ...prev,
      configuration: newConfig
    }))
  }

  const updateDiscretizationField = (section: string, field: string, value: number | string) => {
    const newConfig = { ...formData.configuration }
    if (!newConfig.model_inputs) {
      newConfig.model_inputs = {}
    }
    if (!newConfig.model_inputs[section]) {
      newConfig.model_inputs[section] = {}
    }
    if (!newConfig.model_inputs[section][field]) {
      newConfig.model_inputs[section][field] = {}
    }
    
    newConfig.model_inputs[section][field].value = value
    
    setFormData(prev => ({
      ...prev,
      configuration: newConfig
    }))
  }

  const renderConfigurationField = (key: string, value: any, path: string[] = []) => {
    const currentPath = [...path, key]
    const fieldId = currentPath.join('.')

    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      return (
        <div key={key} style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ 
            color: 'var(--text-primary)', 
            marginBottom: '1rem',
            fontSize: '1.1rem',
            fontWeight: '600',
            borderBottom: '1px solid var(--border-primary)',
            paddingBottom: '0.5rem'
          }}>
            {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </h3>
          <div style={{ marginLeft: '1rem' }}>
            {Object.entries(value).map(([subKey, subValue]) => 
              renderConfigurationField(subKey, subValue, currentPath)
            )}
          </div>
        </div>
      )
    } else if (Array.isArray(value)) {
      return (
        <div key={key} style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ 
            color: 'var(--text-primary)', 
            marginBottom: '1rem',
            fontSize: '1.1rem',
            fontWeight: '600',
            borderBottom: '1px solid var(--border-primary)',
            paddingBottom: '0.5rem'
          }}>
            {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} ({value.length} items)
          </h3>
          <div style={{ marginLeft: '1rem' }}>
            {value.map((item, index) => (
              <div key={index} style={{ 
                marginBottom: '1rem',
                padding: '1rem',
                background: 'var(--bg-panel)',
                border: '1px solid var(--border-primary)',
                borderRadius: '8px'
              }}>
                <h4 style={{ 
                  color: 'var(--text-primary)', 
                  marginBottom: '0.5rem',
                  fontSize: '0.9rem',
                  fontWeight: '500'
                }}>
                  Item {index + 1}
                </h4>
                {typeof item === 'object' && item !== null ? 
                  Object.entries(item).map(([subKey, subValue]) => 
                    renderConfigurationField(subKey, subValue, [...currentPath, index.toString()])
                  ) :
                  <input
                    type="text"
                    value={String(item)}
                    onChange={(e) => updateConfiguration([...currentPath, index.toString()], e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      border: '1px solid var(--border-primary)',
                      borderRadius: '4px',
                      background: 'var(--bg-card)',
                      color: 'var(--text-primary)'
                    }}
                  />
                }
              </div>
            ))}
          </div>
        </div>
      )
    } else {
      // Handle primitive values
      const isNumeric = typeof value === 'number' || (typeof value === 'string' && !isNaN(Number(value)) && value !== '')
      
      return (
        <div key={key} style={{ marginBottom: '1rem' }}>
          <label style={{ 
            display: 'block',
            color: 'var(--text-primary)', 
            fontSize: '0.875rem',
            fontWeight: '500',
            marginBottom: '0.25rem'
          }}>
            {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </label>
          <input
            type={isNumeric ? 'number' : 'text'}
            value={String(value)}
            onChange={(e) => {
              const newValue = isNumeric ? Number(e.target.value) : e.target.value
              updateConfiguration(currentPath, newValue)
            }}
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid var(--border-primary)',
              borderRadius: '6px',
              background: 'var(--bg-card)',
              color: 'var(--text-primary)',
              fontSize: '0.875rem'
            }}
          />
        </div>
      )
    }
  }

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
        Loading model...
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

  return (
    <div style={{ padding: '2rem', color: 'var(--text-primary)' }}>
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
          <button
            onClick={handleCancel}
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
            ← Cancel
          </button>
          <h1 style={{ margin: 0, fontSize: '2rem', fontWeight: '700' }}>
            Edit Model: {model.name}
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
              <label style={{ 
                display: 'block',
                color: 'var(--text-muted)', 
                fontSize: '0.875rem', 
                marginBottom: '0.25rem' 
              }}>
                Model Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid var(--border-primary)',
                  borderRadius: '6px',
                  background: 'var(--bg-card)',
                  color: 'var(--text-primary)',
                  fontSize: '0.875rem'
                }}
              />
            </div>
            <div>
              <label style={{ 
                display: 'block',
                color: 'var(--text-muted)', 
                fontSize: '0.875rem', 
                marginBottom: '0.25rem' 
              }}>
                Status
              </label>
              <select
                value={formData.status}
                onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as any }))}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid var(--border-primary)',
                  borderRadius: '6px',
                  background: 'var(--bg-card)',
                  color: 'var(--text-primary)',
                  fontSize: '0.875rem'
                }}
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="running">Running</option>
                <option value="error">Error</option>
              </select>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Type</div>
              <div style={{ fontWeight: '600' }}>{MODEL_TYPE_LABELS[model.model_type]}</div>
            </div>
          </div>
          
          <div style={{ marginTop: '1rem' }}>
            <label style={{ 
              display: 'block',
              color: 'var(--text-muted)', 
              fontSize: '0.875rem', 
              marginBottom: '0.25rem' 
            }}>
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              rows={3}
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid var(--border-primary)',
                borderRadius: '6px',
                background: 'var(--bg-card)',
                color: 'var(--text-primary)',
                fontSize: '0.875rem',
                resize: 'vertical'
              }}
            />
          </div>
        </div>
      </div>

      {/* Configuration Editor */}
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
          {formData.configuration.model_inputs?.radial_discretization && (
            <RadialDiscretizationSection 
              data={formData.configuration.model_inputs.radial_discretization}
              editable={true}
              onChange={(field, value) => updateDiscretizationField('radial_discretization', field, value)}
            />
          )}
          
          {formData.configuration.model_inputs?.vertical_discretization && (
            <VerticalDiscretizationSection 
              data={formData.configuration.model_inputs.vertical_discretization}
              editable={true}
              onChange={(field, value) => updateDiscretizationField('vertical_discretization', field, value)}
            />
          )}

          {formData.configuration.model_inputs?.pumping_well && (
            <PumpingWellSection 
              data={formData.configuration.model_inputs.pumping_well}
              editable={true}
              onChange={(field, value) => updateDiscretizationField('pumping_well', field, value)}
            />
          )}

                    {formData.configuration.model_inputs?.initial_boundary_conditions && (
                      <InitialBoundaryConditionsSection 
                        data={formData.configuration.model_inputs.initial_boundary_conditions}
                        editable={true}
                        onChange={(field, value) => updateDiscretizationField('initial_boundary_conditions', field, value)}
                      />
                    )}

                    {formData.configuration.model_inputs?.stress_periods && (
                      <StressPeriodsSection 
                        data={formData.configuration.model_inputs.stress_periods}
                        editable={true}
                        onChange={(field, value) => updateDiscretizationField('stress_periods', field, value)}
                      />
                    )}

                    {formData.configuration.model_inputs?.hydraulic_parameters && (
                      <HydraulicParametersSection 
                        data={formData.configuration.model_inputs.hydraulic_parameters}
                        editable={true}
                        onChange={(field, value) => updateDiscretizationField('hydraulic_parameters', field, value)}
                      />
                    )}

                    {formData.configuration.hydraulic_conductivity && (
                      <HydraulicConductivitySection 
                        data={formData.configuration.hydraulic_conductivity}
                        editable={true}
                        onChange={(layers) => {
                          setFormData(prev => {
                            if (!prev) return null
                            return {
                              ...prev,
                              configuration: {
                                ...prev.configuration,
                                hydraulic_conductivity: layers
                              }
                            }
                          })
                        }}
                      />
                    )}
        </div>
      </div>

      {/* Actions */}
      <div style={{ 
        marginTop: '2rem', 
        display: 'flex', 
        gap: '1rem',
        justifyContent: 'flex-end'
      }}>
        <button
          onClick={handleCancel}
          disabled={saving}
          style={{
            background: 'var(--bg-panel)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-primary)',
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            cursor: saving ? 'not-allowed' : 'pointer',
            fontWeight: '600',
            opacity: saving ? 0.6 : 1
          }}
        >
          Cancel
        </button>
        
        <button
          onClick={handleSave}
          disabled={saving}
          style={{
            background: saving ? 'var(--text-muted)' : 'var(--blue-500)',
            color: 'white',
            border: 'none',
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            cursor: saving ? 'not-allowed' : 'pointer',
            fontWeight: '600'
          }}
        >
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </div>
  )
}
