import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function CreateSimulation() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [model, setModel] = useState<any>(null)
  const [loadingModel, setLoadingModel] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    simulation_type: 'Forward Run', // Use the value from simulation_settings
    status: 'pending',
    model_id: '',
    simulation_settings: {
      "Choose Type of Simulation": {
        "value": "Forward Run"
      },
      "Hydraulic Conductivity Flag": {
        "value": "Yes"
      },
      "Vk/Hk Ratio Flag": {
        "value": "No"
      },
      "Specific Yield (Sy) Flag": {
        "value": "Yes"
      },
      "Specific Storage (Ss) Flag": {
        "value": "Yes"
      }
    }
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load model if model_id is provided in URL
  useEffect(() => {
    const modelId = searchParams.get('model')
    if (modelId && isAuthenticated) {
      setLoadingModel(true)
      axios.get(`/api/v1/models/${modelId}`)
        .then(response => {
          setModel(response.data)
          setFormData(prev => ({
            ...prev,
            model_id: modelId,
            name: `Simulation for ${response.data.name}`,
            description: `Simulation based on model: ${response.data.name}`
          }))
        })
        .catch(err => {
          console.error('Failed to load model:', err)
          setError('Failed to load model information')
        })
        .finally(() => {
          setLoadingModel(false)
        })
    }
  }, [searchParams, isAuthenticated])

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
            Please log in to create simulations
          </h3>
          <p style={{ color: 'var(--text-disabled)', margin: 0 }}>
            Authentication required to create simulations
          </p>
        </div>
      </div>
    )
  }

  if (loadingModel) {
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
            Loading model information...
          </h3>
          <p style={{ color: 'var(--text-disabled)', margin: 0 }}>
            Please wait while we fetch the model details
          </p>
        </div>
      </div>
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post('/api/v1/simulations/', {
        ...formData,
        user_id: 'f81d4fae-7dec-11d0-a765-00a0c91e6bf6' // Demo user ID
      })
      
      if (response.status === 201) {
        navigate('/simulations')
      }
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to create simulation')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const handleSimulationSettingChange = (setting: string, value: string) => {
    setFormData(prev => {
      const newSettings = {
        ...prev.simulation_settings,
        [setting]: {
          value: value
        }
      }
      
      // Update simulation_type based on "Choose Type of Simulation" setting
      let newSimulationType = prev.simulation_type
      if (setting === "Choose Type of Simulation") {
        newSimulationType = value
      }
      
      return {
        ...prev,
        simulation_type: newSimulationType,
        simulation_settings: newSettings
      }
    })
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
          Create Simulation
        </h1>
        <p style={{ 
          color: 'var(--text-muted)', 
          margin: 0,
          fontSize: '1rem'
        }}>
          Start a new aquifer simulation
        </p>
      </div>

      {/* Model Information Section */}
      {model && (
        <div style={{
          background: 'var(--bg-panel)',
          border: '1px solid var(--border-primary)',
          borderRadius: '12px',
          padding: '1.5rem',
          marginBottom: '1.5rem',
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
        }}>
          <h3 style={{ 
            margin: '0 0 1rem 0', 
            color: 'var(--text-primary)',
            fontSize: '1.125rem',
            fontWeight: '600'
          }}>
            📊 Model Information
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Model Name</div>
              <div style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{model.name}</div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Model Type</div>
              <div style={{ fontWeight: '600', color: 'var(--text-primary)' }}>
                {model.model_type === 'aquifer_test' ? '🔬 Aquifer Test Analysis' : model.model_type}
              </div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Status</div>
              <div style={{ 
                fontWeight: '600',
                color: model.status === 'active' ? 'var(--success)' : 'var(--warning)'
              }}>
                {model.status.charAt(0).toUpperCase() + model.status.slice(1)}
              </div>
            </div>
          </div>
          {model.description && (
            <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-primary)' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Description</div>
              <div style={{ color: 'var(--text-primary)', fontSize: '0.875rem' }}>{model.description}</div>
            </div>
          )}
        </div>
      )}

      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-primary)',
        borderRadius: '12px',
        padding: '2rem',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        maxWidth: '600px'
      }}>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '0.5rem', 
              color: 'var(--text-secondary)',
              fontSize: '0.875rem',
              fontWeight: '500'
            }}>
              Simulation Name *
            </label>
            <input 
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
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
              placeholder="Enter simulation name"
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
              Description
            </label>
            <textarea 
              name="description"
              value={formData.description}
              onChange={handleChange}
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
              placeholder="Describe the simulation purpose and parameters"
            />
          </div>

          {/* Simulation Settings Section */}
          <div style={{ 
            marginBottom: '1.5rem',
            padding: '1.5rem',
            background: 'var(--bg-panel)',
            border: '1px solid var(--border-primary)',
            borderRadius: '8px'
          }}>
            <h3 style={{ 
              margin: '0 0 1rem 0', 
              color: 'var(--text-primary)',
              fontSize: '1.125rem',
              fontWeight: '600'
            }}>
              Simulation Settings
            </h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
              {/* Choose Type of Simulation */}
              <div>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '0.5rem', 
                  color: 'var(--text-secondary)',
                  fontSize: '0.875rem',
                  fontWeight: '500'
                }}>
                  Choose Type of Simulation *
                </label>
                <select 
                  value={formData.simulation_settings["Choose Type of Simulation"]?.value || "Forward Run"}
                  onChange={(e) => handleSimulationSettingChange('Choose Type of Simulation', e.target.value)}
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
                  <option value="Forward Run">Forward Run</option>
                  <option value="Optimization">Optimization</option>
                </select>
              </div>

              {/* Hydraulic Conductivity Flag */}
              <div>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '0.5rem', 
                  color: 'var(--text-secondary)',
                  fontSize: '0.875rem',
                  fontWeight: '500'
                }}>
                  Hydraulic Conductivity Flag *
                </label>
                <select 
                  value={formData.simulation_settings["Hydraulic Conductivity Flag"]?.value || "Yes"}
                  onChange={(e) => handleSimulationSettingChange('Hydraulic Conductivity Flag', e.target.value)}
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
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>

              {/* Vk/Hk Ratio Flag */}
              <div>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '0.5rem', 
                  color: 'var(--text-secondary)',
                  fontSize: '0.875rem',
                  fontWeight: '500'
                }}>
                  Vk/Hk Ratio Flag *
                </label>
                <select 
                  value={formData.simulation_settings["Vk/Hk Ratio Flag"]?.value || "No"}
                  onChange={(e) => handleSimulationSettingChange('Vk/Hk Ratio Flag', e.target.value)}
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
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>

              {/* Specific Yield Flag */}
              <div>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '0.5rem', 
                  color: 'var(--text-secondary)',
                  fontSize: '0.875rem',
                  fontWeight: '500'
                }}>
                  Specific Yield (Sy) Flag *
                </label>
                <select 
                  value={formData.simulation_settings["Specific Yield (Sy) Flag"]?.value || "Yes"}
                  onChange={(e) => handleSimulationSettingChange('Specific Yield (Sy) Flag', e.target.value)}
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
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>

              {/* Specific Storage Flag */}
              <div>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '0.5rem', 
                  color: 'var(--text-secondary)',
                  fontSize: '0.875rem',
                  fontWeight: '500'
                }}>
                  Specific Storage (Ss) Flag *
                </label>
                <select 
                  value={formData.simulation_settings["Specific Storage (Ss) Flag"]?.value || "Yes"}
                  onChange={(e) => handleSimulationSettingChange('Specific Storage (Ss) Flag', e.target.value)}
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
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
            </div>
          </div>

          {error && (
            <div style={{ 
              padding: '0.75rem 1rem',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.2)',
              borderRadius: '8px',
              color: 'var(--error)',
              fontSize: '0.875rem',
              marginBottom: '1rem'
            }}>
              {error}
            </div>
          )}

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button 
              type="submit"
              disabled={loading}
              style={{
                background: loading ? 'var(--text-disabled)' : 'var(--blue-600)',
                color: 'white',
                border: 'none',
                padding: '0.875rem 1.5rem',
                borderRadius: '8px',
                fontSize: '0.875rem',
                fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              {loading ? 'Creating...' : 'Create Simulation'}
            </button>
            
            <button 
              type="button"
              onClick={() => navigate('/simulations')}
              style={{
                background: 'transparent',
                color: 'var(--text-secondary)',
                border: '1px solid var(--border-primary)',
                padding: '0.875rem 1.5rem',
                borderRadius: '8px',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
