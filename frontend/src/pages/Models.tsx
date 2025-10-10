import { useEffect, useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

// Define the Model type based on the backend schema
type ModelConfiguration = {
  metadata: {
    source_file: string
    sheets: string[]
    conversion_timestamp: string
  }
  data: {
    user_id: string
    model_id: string
    model_inputs: any
    hydraulic_conductivity: any[]
  }
  model_inputs: any
  hydraulic_conductivity: any[]
}

type Model = {
  id: string
  name: string
  description: string
  model_type: 'aquifer_test' | 'conceptual' | 'solute_transport' | 'seawater_intrusion' | 'stochastic'
  configuration: ModelConfiguration | null
  status: 'active' | 'inactive' | 'running' | 'error'
  created_at: string
  updated_at?: string
  user_id: string
}

type ModelCreateData = {
  name: string
  description: string
  model_type: 'aquifer_test' | 'conceptual' | 'solute_transport' | 'seawater_intrusion' | 'stochastic'
  configuration: ModelConfiguration
  status?: string
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
    modelType: 'aquifer_test' as 'aquifer_test' | 'conceptual' | 'solute_transport' | 'seawater_intrusion' | 'stochastic'
  })
  const [creating, setCreating] = useState(false)
  const [editingModel, setEditingModel] = useState<Model | null>(null)
  const [showEditModal, setShowEditModal] = useState(false)
  const [updating, setUpdating] = useState(false)
  const [deleting, setDeleting] = useState<number | null>(null)

  // Fetch models from backend API
  const fetchModels = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await axios.get('/api/v1/models/')
      setModels(response.data)
    } catch (e: any) {
      console.error('Failed to fetch models:', e)
      setError(e?.response?.data?.detail || e?.message || 'Failed to load models')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!isAuthenticated) return
    fetchModels()
  }, [isAuthenticated])

  // Create new model
  const handleCreateModel = async () => {
    if (!newModel.name.trim() || !newModel.description.trim()) {
      setError('Please fill in all required fields')
      return
    }

    try {
      setCreating(true)
      setError(null)
      
      const modelData: ModelCreateData = {
        name: newModel.name.trim(),
        description: newModel.description.trim(),
        model_type: newModel.modelType,
        configuration: {
          metadata: {
            source_file: "Model_Inputs.json",
            sheets: ["Model Inputs", "Hydraulic Conductivity"],
            conversion_timestamp: new Date().toISOString()
          },
          data: {
            user_id: "default-user",
            model_id: `model-${Date.now()}`,
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
          },
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
        },
        status: 'active'
      }
      
      const response = await axios.post('/api/v1/models/', modelData)
      
      // Add new model to list
      setModels(prev => [...prev, response.data])
      
      // Clear form and close modal
      setNewModel({ name: '', description: '', modelType: 'aquifer_test' })
      setShowCreateModal(false)
      
      // Navigate to the new model
      navigate(`/models/${response.data.id}`)
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to create model')
    } finally {
      setCreating(false)
    }
  }

  // Update existing model
  const handleUpdateModel = async () => {
    if (!editingModel || !editingModel.name.trim() || !editingModel.description.trim()) {
      setError('Please fill in all required fields')
      return
    }

    try {
      setUpdating(true)
      setError(null)
      
      const updateData = {
        name: editingModel.name.trim(),
        description: editingModel.description.trim(),
        status: editingModel.status
      }
      
      const response = await axios.put(`/api/v1/models/${editingModel.id}`, updateData)
      
      // Update model in list
      setModels(prev => prev.map(model => 
        model.id === editingModel.id ? response.data : model
      ))
      
      // Close modal
      setShowEditModal(false)
      setEditingModel(null)
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to update model')
    } finally {
      setUpdating(false)
    }
  }

  // Delete model
  const handleDeleteModel = async (modelId: string) => {
    if (!confirm('Are you sure you want to delete this model? This action cannot be undone.')) {
      return
    }

    try {
      setDeleting(modelId)
      setError(null)
      
      await axios.delete(`/api/v1/models/${modelId}`)
      
      // Remove model from list
      setModels(prev => prev.filter(model => model.id !== modelId))
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to delete model')
    } finally {
      setDeleting(null)
    }
  }

  // Open edit modal
  const openEditModal = (model: Model) => {
    setEditingModel(model)
    setShowEditModal(true)
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
      case 'aquifer_test':
        return '🧪'
      case 'conceptual':
        return '🧠'
      case 'solute_transport':
        return '🧬'
      case 'seawater_intrusion':
        return '🌊'
      case 'stochastic':
        return '🎲'
      default:
        return '📊'
    }
  }

  const getModelTypeLabel = (modelType: string) => {
    switch (modelType) {
      case 'aquifer_test':
        return 'Aquifer Test Analysis'
      case 'conceptual':
        return 'Conceptual Model'
      case 'solute_transport':
        return 'Solute Transport Model'
      case 'seawater_intrusion':
        return 'Seawater Intrusion Model'
      case 'stochastic':
        return 'Stochastic Model'
      default:
        return 'Unknown Model'
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
                onEdit={() => openEditModal(model)}
                onDelete={() => handleDeleteModel(model.id)}
                isDeleting={deleting === model.id}
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
                onChange={(e) => {
                  const selectedValue = e.target.value
                  if (selectedValue === 'aquifer_test') {
                    setNewModel({ ...newModel, modelType: selectedValue as any })
                  }
                }}
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
                <option value="aquifer_test">🧪 Aquifer Test Analysis - Ready to Use!</option>
                <option value="conceptual" disabled>🧠 Conceptual Model - Coming Soon! 🚀</option>
                <option value="solute_transport" disabled>🧬 Solute Transport Model - Advanced Features Coming! ⚡</option>
                <option value="seawater_intrusion" disabled>🌊 Seawater Intrusion Model - Coastal Analysis Coming! 🌊</option>
                <option value="stochastic" disabled>🎲 Stochastic Model - Uncertainty Analysis Coming! 🎯</option>
              </select>
            </div>

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
              <button
                onClick={() => {
                  setShowCreateModal(false)
                  setNewModel({ name: '', description: '', modelType: 'aquifer_test' })
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

      {/* Edit Model Modal */}
      {showEditModal && editingModel && (
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
              Edit Model
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
                value={editingModel.name}
                onChange={(e) => setEditingModel({ ...editingModel, name: e.target.value })}
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
                value={editingModel.description}
                onChange={(e) => setEditingModel({ ...editingModel, description: e.target.value })}
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

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.5rem',
                color: 'var(--text-secondary)',
                fontSize: '0.875rem',
                fontWeight: '500'
              }}>
                Status
              </label>
              <select
                value={editingModel.status}
                onChange={(e) => setEditingModel({ ...editingModel, status: e.target.value as any })}
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
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="running">Running</option>
                <option value="error">Error</option>
              </select>
            </div>

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
              <button
                onClick={() => {
                  setShowEditModal(false)
                  setEditingModel(null)
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
                onClick={handleUpdateModel}
                disabled={updating}
                style={{
                  background: updating ? 'var(--text-disabled)' : 'var(--blue-500)',
                  color: 'white',
                  border: 'none',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '8px',
                  fontSize: '0.875rem',
                  fontWeight: '600',
                  cursor: updating ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                {updating ? 'Updating...' : 'Update Model'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function ModelCard({ model, onOpen, onEdit, onDelete, isDeleting }: {
  model: Model
  onOpen: () => void
  onEdit: () => void
  onDelete: () => void
  isDeleting: boolean
}) {
  const isDisabled = model.model_type !== 'aquifer_test'
  
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
      case 'aquifer_test':
        return '🧪'
      case 'conceptual':
        return '🧠'
      case 'solute_transport':
        return '🧬'
      case 'seawater_intrusion':
        return '🌊'
      case 'stochastic':
        return '🎲'
      default:
        return '📊'
    }
  }

  const getModelTypeLabel = (modelType: string) => {
    switch (modelType) {
      case 'aquifer_test':
        return 'Aquifer Test Analysis'
      case 'conceptual':
        return 'Conceptual Model'
      case 'solute_transport':
        return 'Solute Transport Model'
      case 'seawater_intrusion':
        return 'Seawater Intrusion Model'
      case 'stochastic':
        return 'Stochastic Model'
      default:
        return 'Unknown Model'
    }
  }

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-primary)',
      borderRadius: '12px',
      padding: '1.5rem',
      transition: 'all 0.2s ease',
      opacity: isDeleting ? 0.6 : 1,
      cursor: isDisabled ? 'not-allowed' : 'pointer',
      position: 'relative'
    }}
    onClick={isDisabled ? undefined : onOpen}
    >
      {/* Header */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'flex-start',
        marginBottom: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ fontSize: '1.5rem' }}>
            {getModelIcon(model.model_type)}
          </div>
          <div>
            <h3 style={{ 
              margin: '0 0 0.25rem 0', 
              color: 'var(--text-primary)',
              fontSize: '1.125rem',
              fontWeight: '600'
            }}>
              {model.name}
            </h3>
            <div style={{ 
              fontSize: '0.75rem', 
              color: 'var(--text-muted)',
              fontWeight: '500'
            }}>
              {getModelTypeLabel(model.model_type)}
            </div>
          </div>
        </div>
        
        {/* Actions */}
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onEdit()
            }}
            style={{
              background: 'transparent',
              border: '1px solid var(--border-primary)',
              borderRadius: '6px',
              padding: '0.5rem',
              cursor: 'pointer',
              color: 'var(--text-secondary)',
              fontSize: '0.75rem',
              transition: 'all 0.2s ease'
            }}
            title="Edit model"
          >
            ✏️
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onDelete()
            }}
            disabled={isDeleting}
            style={{
              background: 'transparent',
              border: '1px solid var(--border-primary)',
              borderRadius: '6px',
              padding: '0.5rem',
              cursor: isDeleting ? 'not-allowed' : 'pointer',
              color: isDeleting ? 'var(--text-disabled)' : 'var(--error)',
              fontSize: '0.75rem',
              transition: 'all 0.2s ease',
              opacity: isDeleting ? 0.6 : 1
            }}
            title="Delete model"
          >
            {isDeleting ? '⏳' : '🗑️'}
          </button>
        </div>
      </div>

      {/* Description */}
      <p style={{ 
        color: 'var(--text-secondary)', 
        margin: '0 0 1rem 0',
        fontSize: '0.875rem',
        lineHeight: '1.5'
      }}>
        {model.description}
      </p>

      {/* Status and Info */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '1rem'
      }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.5rem' 
        }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: getStatusColor(model.status)
          }} />
          <span style={{ 
            fontSize: '0.75rem', 
            color: 'var(--text-muted)',
            textTransform: 'capitalize'
          }}>
            {model.status}
          </span>
        </div>
        
        <div style={{ 
          fontSize: '0.75rem', 
          color: 'var(--text-muted)' 
        }}>
          {new Date(model.created_at).toLocaleDateString()}
        </div>
      </div>

      {/* Disabled Overlay */}
      {isDisabled && (
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.1)',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backdropFilter: 'blur(2px)'
        }}>
          <div style={{
            background: 'var(--bg-panel)',
            padding: '1rem',
            borderRadius: '8px',
            border: '1px solid var(--border-primary)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>🚧</div>
            <div style={{ 
              fontSize: '0.875rem', 
              color: 'var(--text-muted)',
              fontWeight: '500'
            }}>
              Coming Soon!
            </div>
          </div>
        </div>
      )}
    </div>
  )
}