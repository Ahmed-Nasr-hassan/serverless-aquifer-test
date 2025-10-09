import { useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function CreateModelInput() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    user_id: 'f81d4fae-7dec-11d0-a765-00a0c91e6bf6',
    model_id: 'a55d4fea-8wq2-6ds3-a765-00a5c91e1bf2',
    description: '',
    model_inputs: {
      run_type: 'Calibration',
      ztop: 100.0,
      pumping_rate_m3_per_day: 1000.0,
      specific_yield: 0.2,
      specific_storage: 0.0001,
      simulation_time_days: 30,
      time_step_days: 0.1
    },
    hydraulic_conductivity: [
      { layer: 1, top: 100.0, bottom: 80.0, k: 10.0 },
      { layer: 2, top: 80.0, bottom: 60.0, k: 5.0 },
      { layer: 3, top: 60.0, bottom: 40.0, k: 2.0 }
    ]
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

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
            Please log in to create model inputs
          </h3>
          <p style={{ color: 'var(--text-disabled)', margin: 0 }}>
            Authentication required to create model inputs
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
      const response = await axios.post('/api/v1/model-inputs/', formData)
      
      if (response.status === 201) {
        navigate('/model-inputs')
      }
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to create model input')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    
    if (name.startsWith('model_inputs.')) {
      const field = name.split('.')[1]
      setFormData(prev => ({
        ...prev,
        model_inputs: {
          ...prev.model_inputs,
          [field]: isNaN(Number(value)) ? value : Number(value)
        }
      }))
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }))
    }
  }

  const addLayer = () => {
    const newLayer = {
      layer: formData.hydraulic_conductivity.length + 1,
      top: 0,
      bottom: 0,
      k: 1.0
    }
    setFormData(prev => ({
      ...prev,
      hydraulic_conductivity: [...prev.hydraulic_conductivity, newLayer]
    }))
  }

  const removeLayer = (index: number) => {
    setFormData(prev => ({
      ...prev,
      hydraulic_conductivity: prev.hydraulic_conductivity.filter((_, i) => i !== index)
    }))
  }

  const updateLayer = (index: number, field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      hydraulic_conductivity: prev.hydraulic_conductivity.map((layer, i) => 
        i === index ? { ...layer, [field]: Number(value) } : layer
      )
    }))
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
          Create Model Input
        </h1>
        <p style={{ 
          color: 'var(--text-muted)', 
          margin: 0,
          fontSize: '1rem'
        }}>
          Configure aquifer model parameters and hydraulic conductivity
        </p>
      </div>

      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-primary)',
        borderRadius: '12px',
        padding: '2rem',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        maxWidth: '800px'
      }}>
        <form onSubmit={handleSubmit}>
          {/* Basic Info */}
          <div style={{ marginBottom: '2rem' }}>
            <h3 style={{ 
              margin: '0 0 1rem 0', 
              color: 'var(--text-primary)',
              fontSize: '1.25rem',
              fontWeight: '600'
            }}>
              Basic Information
            </h3>
            
            <div style={{ marginBottom: '1rem' }}>
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
                rows={2}
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
                placeholder="Describe the model configuration"
              />
            </div>
          </div>

          {/* Model Parameters */}
          <div style={{ marginBottom: '2rem' }}>
            <h3 style={{ 
              margin: '0 0 1rem 0', 
              color: 'var(--text-primary)',
              fontSize: '1.25rem',
              fontWeight: '600'
            }}>
              Model Parameters
            </h3>
            
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '1rem' 
            }}>
              <div>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '0.5rem', 
                  color: 'var(--text-secondary)',
                  fontSize: '0.875rem',
                  fontWeight: '500'
                }}>
                  Run Type
                </label>
                <select 
                  name="model_inputs.run_type"
                  value={formData.model_inputs.run_type}
                  onChange={handleChange}
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
                  <option value="Calibration">Calibration</option>
                  <option value="Prediction">Prediction</option>
                  <option value="Sensitivity">Sensitivity</option>
                </select>
              </div>

              <div>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '0.5rem', 
                  color: 'var(--text-secondary)',
                  fontSize: '0.875rem',
                  fontWeight: '500'
                }}>
                  Top Elevation (m)
                </label>
                <input 
                  name="model_inputs.ztop"
                  type="number"
                  step="0.1"
                  value={formData.model_inputs.ztop}
                  onChange={handleChange}
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

              <div>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '0.5rem', 
                  color: 'var(--text-secondary)',
                  fontSize: '0.875rem',
                  fontWeight: '500'
                }}>
                  Pumping Rate (m³/day)
                </label>
                <input 
                  name="model_inputs.pumping_rate_m3_per_day"
                  type="number"
                  step="0.1"
                  value={formData.model_inputs.pumping_rate_m3_per_day}
                  onChange={handleChange}
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

              <div>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '0.5rem', 
                  color: 'var(--text-secondary)',
                  fontSize: '0.875rem',
                  fontWeight: '500'
                }}>
                  Specific Yield
                </label>
                <input 
                  name="model_inputs.specific_yield"
                  type="number"
                  step="0.001"
                  value={formData.model_inputs.specific_yield}
                  onChange={handleChange}
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
            </div>
          </div>

          {/* Hydraulic Conductivity Layers */}
          <div style={{ marginBottom: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ 
                margin: 0, 
                color: 'var(--text-primary)',
                fontSize: '1.25rem',
                fontWeight: '600'
              }}>
                Hydraulic Conductivity Layers
              </h3>
              <button 
                type="button"
                onClick={addLayer}
                style={{
                  background: 'var(--blue-600)',
                  color: 'white',
                  border: 'none',
                  padding: '0.5rem 1rem',
                  borderRadius: '6px',
                  fontSize: '0.75rem',
                  fontWeight: '500',
                  cursor: 'pointer'
                }}
              >
                + Add Layer
              </button>
            </div>

            <div style={{
              background: 'var(--bg-panel)',
              border: '1px solid var(--border-primary)',
              borderRadius: '8px',
              overflow: 'hidden'
            }}>
              <div style={{
                background: 'var(--bg-panel-accent)',
                padding: '0.75rem 1rem',
                display: 'grid',
                gridTemplateColumns: '1fr 1fr 1fr 1fr auto',
                gap: '1rem',
                fontSize: '0.75rem',
                fontWeight: '600',
                color: 'var(--text-primary)'
              }}>
                <div>Layer</div>
                <div>Top (m)</div>
                <div>Bottom (m)</div>
                <div>K (m/day)</div>
                <div>Action</div>
              </div>
              
              {formData.hydraulic_conductivity.map((layer, index) => (
                <div key={index} style={{
                  padding: '0.75rem 1rem',
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr 1fr 1fr auto',
                  gap: '1rem',
                  alignItems: 'center',
                  borderTop: '1px solid var(--border-primary)'
                }}>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                    {layer.layer}
                  </div>
                  <input 
                    type="number"
                    step="0.1"
                    value={layer.top}
                    onChange={(e) => updateLayer(index, 'top', e.target.value)}
                    style={{
                      padding: '0.5rem',
                      borderRadius: '4px',
                      border: '1px solid var(--border-primary)',
                      background: 'var(--bg-tertiary)',
                      color: 'var(--text-primary)',
                      fontSize: '0.875rem'
                    }}
                  />
                  <input 
                    type="number"
                    step="0.1"
                    value={layer.bottom}
                    onChange={(e) => updateLayer(index, 'bottom', e.target.value)}
                    style={{
                      padding: '0.5rem',
                      borderRadius: '4px',
                      border: '1px solid var(--border-primary)',
                      background: 'var(--bg-tertiary)',
                      color: 'var(--text-primary)',
                      fontSize: '0.875rem'
                    }}
                  />
                  <input 
                    type="number"
                    step="0.1"
                    value={layer.k}
                    onChange={(e) => updateLayer(index, 'k', e.target.value)}
                    style={{
                      padding: '0.5rem',
                      borderRadius: '4px',
                      border: '1px solid var(--border-primary)',
                      background: 'var(--bg-tertiary)',
                      color: 'var(--text-primary)',
                      fontSize: '0.875rem'
                    }}
                  />
                  <button 
                    type="button"
                    onClick={() => removeLayer(index)}
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
                    Remove
                  </button>
                </div>
              ))}
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
              {loading ? 'Creating...' : 'Create Model Input'}
            </button>
            
            <button 
              type="button"
              onClick={() => navigate('/model-inputs')}
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
