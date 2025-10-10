import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'

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

export default function CreateModel() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    model_type: 'aquifer_test' as 'aquifer_test' | 'conceptual' | 'solute_transport' | 'seawater_intrusion' | 'stochastic',
    status: 'active' as 'active' | 'inactive' | 'running' | 'error',
    configuration: {
      model_inputs: {
        radial_discretization: {
          boundary_distance_from_pumping_well: { value: 500, unit: "m" },
          second_column_size: { value: 0.01, unit: "m" },
          column_multiplier: { value: 1.1 }
        },
        vertical_discretization: {
          saturated_top_elevation: { value: -121.84, unit: "m" },
          aquifer_bottom_elevation: { value: -500, unit: "m" },
          screen_top_cell_thickness: { value: 0.01, unit: "m" },
          screen_bottom_cell_thickness: { value: 0.01, unit: "m" },
          refinement_above_screen: { value: 1.6 },
          refinement_below_screen: { value: 1.3 },
          refinement_between_screen: { value: 1.1 }
        },
        pumping_well: {
          well_radius: { value: 0.22, unit: "m" },
          pumping_rate: { value: -141, unit: "m³/hr" },
          screen_top_elevation: { value: -212, unit: "m" },
          screen_bottom_elevation: { value: -378, unit: "m" }
        },
        observation_wells: {
          observation_wells: { value: "OBS-1", unit: "No" },
          observation_well_distance: { value: 53 },
          observation_top_screen_level: { value: -212 },
          observation_bottom_screen_level: { value: -300 }
        },
        initial_boundary_conditions: {
          starting_head: { value: -121.84, unit: "m" },
          specified_head: { value: -121.84, unit: "m" }
        },
        stress_periods: {
          analysis_period: { value: "Pumping + Recovery" },
          pumping_length: { value: 2966, unit: "minutes" },
          recovery_length: { value: 1200, unit: "minutes" },
          number_of_time_steps: { value: 200 },
          time_multiplier: { value: 1.05 },
          time_units: { value: "SECONDS" }
        },
        hydraulic_parameters: {
          hydraulic_conductivity: { value: 0.9073948333333328 },
          vk_hk_ratio: { value: 1 },
          specific_yield: { value: 0.11662639999999996 },
          specific_storage: { value: 3.977036316666669e-07 }
        },
        data_files: {
          observed_data: { value: "observation_data.json" }
        },
        observation_data: {
          observation_wells: {}
        },
        simulation_settings: {
          choose_type_of_simulation: { value: "Calibration" },
          hydraulic_conductivity_flag: { value: "Yes" },
          vk_hk_ratio_flag: { value: "No" },
          specific_yield_flag: { value: "Yes" },
          specific_storage_flag: { value: "Yes" }
        }
      },
      hydraulic_conductivity: [
        {
          soil_material: "Sandstone",
          layer_top_level_m: 0.0,
          layer_bottom_level_m: -350.0,
          hydraulic_conductivity_m_per_day: 0.9073948333333328
        },
        {
          soil_material: "Sand",
          layer_top_level_m: -350.0,
          layer_bottom_level_m: -700.0,
          hydraulic_conductivity_m_per_day: 50
        }
      ]
    }
  })

  React.useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
    }
  }, [isAuthenticated, navigate])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name.trim()) {
      setError('Model name is required')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post('/api/v1/models/', formData)
      navigate(`/models/${response.data.id}`)
    } catch (err: any) {
      console.error('Failed to create model:', err)
      setError(err.response?.data?.detail || 'Failed to create model')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    navigate('/models')
  }

  if (!isAuthenticated) {
    return null
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
            Create New Model
          </h1>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div style={{
          background: 'var(--error-light)',
          border: '1px solid var(--error)',
          borderRadius: '8px',
          padding: '1rem',
          marginBottom: '1.5rem',
          color: 'var(--error)'
        }}>
          {error}
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit}>
        <div style={{ 
          background: 'var(--bg-card)', 
          border: '1px solid var(--border-primary)', 
          borderRadius: '12px', 
          padding: '1.5rem',
          marginBottom: '1.5rem'
        }}>
          <h2 style={{ 
            margin: '0 0 1.5rem 0', 
            fontSize: '1.25rem', 
            fontWeight: '600',
            color: 'var(--text-primary)'
          }}>
            Basic Information
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
            <div>
              <label style={{ 
                display: 'block',
                color: 'var(--text-primary)', 
                fontSize: '0.875rem', 
                fontWeight: '500',
                marginBottom: '0.5rem' 
              }}>
                Model Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Enter model name"
                required
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
                color: 'var(--text-primary)', 
                fontSize: '0.875rem', 
                fontWeight: '500',
                marginBottom: '0.5rem' 
              }}>
                Model Type
              </label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {Object.entries(MODEL_TYPE_LABELS).map(([key, label]) => (
                  <label key={key} style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    cursor: 'pointer',
                    padding: '0.5rem',
                    borderRadius: '6px',
                    background: formData.model_type === key ? 'var(--blue-50)' : 'transparent',
                    border: formData.model_type === key ? '1px solid var(--blue-500)' : '1px solid var(--border-primary)'
                  }}>
                    <input
                      type="radio"
                      name="model_type"
                      value={key}
                      checked={formData.model_type === key}
                      onChange={(e) => setFormData(prev => ({ ...prev, model_type: e.target.value as any }))}
                      style={{ marginRight: '0.5rem' }}
                    />
                    <span style={{ fontSize: '1.25rem', marginRight: '0.5rem' }}>
                      {MODEL_TYPE_ICONS[key as keyof typeof MODEL_TYPE_ICONS]}
                    </span>
                    <span style={{ fontSize: '0.875rem' }}>{label}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          <div style={{ marginTop: '1rem' }}>
            <label style={{ 
              display: 'block',
              color: 'var(--text-primary)', 
              fontSize: '0.875rem', 
              fontWeight: '500',
              marginBottom: '0.5rem' 
            }}>
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Enter model description"
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

        {/* Actions */}
        <div style={{ 
          display: 'flex', 
          gap: '1rem',
          justifyContent: 'flex-end'
        }}>
          <button
            type="button"
            onClick={handleCancel}
            disabled={loading}
            style={{
              background: 'var(--bg-panel)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border-primary)',
              padding: '0.75rem 1.5rem',
              borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: '600',
              opacity: loading ? 0.6 : 1
            }}
          >
            Cancel
          </button>
          
          <button
            type="submit"
            disabled={loading}
            style={{
              background: loading ? 'var(--text-muted)' : 'var(--blue-500)',
              color: 'white',
              border: 'none',
              padding: '0.75rem 1.5rem',
              borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: '600'
            }}
          >
            {loading ? 'Creating...' : 'Create Model'}
          </button>
        </div>
      </form>
    </div>
  )
}
