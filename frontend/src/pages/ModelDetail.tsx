import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

type ModelConfig = {
  // Basic Model Settings
  name: string
  description: string
  modelType: 'aquifer' | 'well' | 'optimization'
  
  // Aquifer Parameters
  aquiferConfig: {
    ztop: number
    specificYield: number
    specificStorage: number
    hydraulicConductivity: Array<{
      layer: number
      top: number
      bottom: number
      k: number
    }>
  }
  
  // Well Parameters
  wellConfig: {
    pumpingRate: number
    wellRadius: number
    screenTop: number
    screenBottom: number
    distanceFromWell: number
  }
  
  // Observation Points
  observationPoints: Array<{
    id: string
    name: string
    distanceFromWell: number
    topScreenLevel: number
    bottomScreenLevel: number
    dataPoints: Array<{
      timeMinutes: number
      waterLevel: number
      drawdown: number
    }>
  }>
  
  // Simulation Settings
  simulationConfig: {
    simulationTimeDays: number
    timeStepDays: number
    runType: 'forward' | 'optimization'
  }
}

export default function ModelDetail() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [config, setConfig] = useState<ModelConfig>({
    name: '',
    description: '',
    modelType: 'aquifer',
    aquiferConfig: {
      ztop: 100.0,
      specificYield: 0.2,
      specificStorage: 0.0001,
      hydraulicConductivity: [
        { layer: 1, top: 100.0, bottom: 80.0, k: 10.0 },
        { layer: 2, top: 80.0, bottom: 60.0, k: 5.0 },
        { layer: 3, top: 60.0, bottom: 40.0, k: 2.0 }
      ]
    },
    wellConfig: {
      pumpingRate: 1000.0,
      wellRadius: 0.1,
      screenTop: 50.0,
      screenBottom: 30.0,
      distanceFromWell: 10.0
    },
    observationPoints: [
      {
        id: 'OBS-1',
        name: 'Observation Well 1',
        distanceFromWell: 53.0,
        topScreenLevel: -212.0,
        bottomScreenLevel: -300.0,
        dataPoints: [
          { timeMinutes: 0, waterLevel: 45.3, drawdown: 0 },
          { timeMinutes: 5, waterLevel: 45.82, drawdown: 0.52 },
          { timeMinutes: 10, waterLevel: 46.32, drawdown: 1.02 }
        ]
      }
    ],
    simulationConfig: {
      simulationTimeDays: 30,
      timeStepDays: 0.1,
      runType: 'forward'
    }
  })
  const [loading, setLoading] = useState(false)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [csvLoading, setCsvLoading] = useState(false)

  useEffect(() => {
    if (!isAuthenticated || !id) return

    // Load model configuration (for now using mock data)
    const loadModel = async () => {
      try {
        setLoading(true)
        // Mock model data - in real app this would come from API
        const mockModel: ModelConfig = {
          name: `Model ${id}`,
          description: 'Aquifer simulation model configuration',
          modelType: 'aquifer',
          aquiferConfig: {
            ztop: 100.0,
            specificYield: 0.2,
            specificStorage: 0.0001,
            hydraulicConductivity: [
              { layer: 1, top: 100.0, bottom: 80.0, k: 10.0 },
              { layer: 2, top: 80.0, bottom: 60.0, k: 5.0 },
              { layer: 3, top: 60.0, bottom: 40.0, k: 2.0 }
            ]
          },
          wellConfig: {
            pumpingRate: 1000.0,
            wellRadius: 0.1,
            screenTop: 50.0,
            screenBottom: 30.0,
            distanceFromWell: 10.0
          },
          simulationConfig: {
            simulationTimeDays: 30,
            timeStepDays: 0.1,
            runType: 'forward'
          }
        }
        setConfig(mockModel)
      } catch (e: any) {
        setError(e?.response?.data?.detail || e?.message || 'Failed to load model')
      } finally {
        setLoading(false)
      }
    }

    loadModel()
  }, [isAuthenticated, id])

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
            Please log in to view model details
          </h3>
          <p style={{ color: 'var(--text-disabled)', margin: 0 }}>
            Authentication required to access model configuration
          </p>
        </div>
      </div>
    )
  }

  const handleRunSimulation = async () => {
    setRunning(true)
    setError(null)
    setSuccess(null)

    try {
      // Create simulation with current configuration
      const simulationData = {
        name: `${config.name} - ${config.simulationConfig.runType} run`,
        description: `Simulation run for ${config.name}`,
        simulation_type: config.simulationConfig.runType === 'optimization' ? 'Optimization' : 'Prediction',
        status: 'running',
        user_id: 'f81d4fae-7dec-11d0-a765-00a0c91e6bf6',
        model_config: config
      }

      const response = await axios.post('/api/v1/simulations/', simulationData)
      
      if (response.status === 201) {
        setSuccess(`Simulation started successfully! Run type: ${config.simulationConfig.runType}`)
        // Redirect to simulations list after a delay
        setTimeout(() => {
          navigate('/simulations')
        }, 2000)
      }
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to start simulation')
    } finally {
      setRunning(false)
    }
  }

  const updateConfig = (section: keyof ModelConfig, field: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }))
  }

  const addHydraulicLayer = () => {
    const newLayer = {
      layer: config.aquiferConfig.hydraulicConductivity.length + 1,
      top: 0,
      bottom: 0,
      k: 1.0
    }
    setConfig(prev => ({
      ...prev,
      aquiferConfig: {
        ...prev.aquiferConfig,
        hydraulicConductivity: [...prev.aquiferConfig.hydraulicConductivity, newLayer]
      }
    }))
  }

  const removeHydraulicLayer = (index: number) => {
    setConfig(prev => ({
      ...prev,
      aquiferConfig: {
        ...prev.aquiferConfig,
        hydraulicConductivity: prev.aquiferConfig.hydraulicConductivity.filter((_, i) => i !== index)
      }
    }))
  }

  const updateHydraulicLayer = (index: number, field: string, value: string) => {
    setConfig(prev => ({
      ...prev,
      aquiferConfig: {
        ...prev.aquiferConfig,
        hydraulicConductivity: prev.aquiferConfig.hydraulicConductivity.map((layer, i) => 
          i === index ? { ...layer, [field]: Number(value) } : layer
        )
      }
    }))
  }

  const addObservationPoint = () => {
    const newPoint = {
      id: `OBS-${(config.observationPoints?.length || 0) + 1}`,
      name: `Observation Well ${(config.observationPoints?.length || 0) + 1}`,
      distanceFromWell: 50.0,
      topScreenLevel: -200.0,
      bottomScreenLevel: -250.0,
      dataPoints: [
        { timeMinutes: 0, waterLevel: 45.0, drawdown: 0 },
        { timeMinutes: 60, waterLevel: 45.5, drawdown: 0.5 }
      ]
    }
    setConfig(prev => ({
      ...prev,
      observationPoints: [...(prev.observationPoints || []), newPoint]
    }))
  }

  const removeObservationPoint = (index: number) => {
    setConfig(prev => ({
      ...prev,
      observationPoints: (prev.observationPoints || []).filter((_, i) => i !== index)
    }))
  }

  const updateObservationPoint = (index: number, field: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      observationPoints: (prev.observationPoints || []).map((point, i) => 
        i === index ? { ...point, [field]: value } : point
      )
    }))
  }

  const addDataPoint = (obsIndex: number) => {
    const newDataPoint = {
      timeMinutes: 0,
      waterLevel: 45.0,
      drawdown: 0
    }
    setConfig(prev => ({
      ...prev,
      observationPoints: (prev.observationPoints || []).map((point, i) => 
        i === obsIndex ? { 
          ...point, 
          dataPoints: [...(point.dataPoints || []), newDataPoint] 
        } : point
      )
    }))
  }

  const removeDataPoint = (obsIndex: number, dataIndex: number) => {
    setConfig(prev => ({
      ...prev,
      observationPoints: (prev.observationPoints || []).map((point, i) => 
        i === obsIndex ? { 
          ...point, 
          dataPoints: (point.dataPoints || []).filter((_, j) => j !== dataIndex) 
        } : point
      )
    }))
  }

  const updateDataPoint = (obsIndex: number, dataIndex: number, field: string, value: string) => {
    setConfig(prev => ({
      ...prev,
      observationPoints: (prev.observationPoints || []).map((point, i) => 
        i === obsIndex ? { 
          ...point, 
          dataPoints: (point.dataPoints || []).map((dp, j) => 
            j === dataIndex ? { ...dp, [field]: Number(value) } : dp
          )
        } : point
      )
    }))
  }

  const parseCSV = (csvText: string): Array<{timeMinutes: number, waterLevel: number, drawdown: number}> => {
    const lines = csvText.split('\n').filter(line => line.trim())
    const data: Array<{timeMinutes: number, waterLevel: number, drawdown: number}> = []
    
    // Skip header row if it exists
    const startIndex = lines[0]?.toLowerCase().includes('time') ? 1 : 0
    
    for (let i = startIndex; i < lines.length; i++) {
      const columns = lines[i].split(',').map(col => col.trim())
      
      if (columns.length >= 3) {
        const timeMinutes = parseFloat(columns[0]) || 0
        const waterLevel = parseFloat(columns[1]) || 0
        const drawdown = parseFloat(columns[2]) || 0
        
        if (!isNaN(timeMinutes) && !isNaN(waterLevel) && !isNaN(drawdown)) {
          data.push({ timeMinutes, waterLevel, drawdown })
        }
      }
    }
    
    return data
  }

  const handleCSVUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.name.toLowerCase().endsWith('.csv')) {
      setError('Please select a CSV file')
      return
    }

    setCsvLoading(true)
    setError(null)

    try {
      const text = await file.text()
      const csvData = parseCSV(text)
      
      if (csvData.length === 0) {
        setError('No valid data found in CSV file')
        return
      }

      // Create a new observation point with the CSV data
      const newPoint = {
        id: `OBS-${(config.observationPoints?.length || 0) + 1}`,
        name: `Observation Well ${(config.observationPoints?.length || 0) + 1} (from CSV)`,
        distanceFromWell: 50.0,
        topScreenLevel: -200.0,
        bottomScreenLevel: -250.0,
        dataPoints: csvData
      }

      setConfig(prev => ({
        ...prev,
        observationPoints: [...(prev.observationPoints || []), newPoint]
      }))

      setSuccess(`Successfully imported ${csvData.length} data points from CSV`)
      setCsvFile(null)
      
      // Clear the file input
      event.target.value = ''
      
    } catch (err) {
      setError('Failed to read CSV file. Please check the file format.')
    } finally {
      setCsvLoading(false)
    }
  }

  const downloadCSVTemplate = () => {
    const csvContent = 'Time (minutes),Water Level (m),Drawdown (m)\n0,45.3,0\n5,45.82,0.52\n10,46.32,1.02\n15,46.47,1.17\n20,46.57,1.27'
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'observation_data_template.csv'
    link.click()
    window.URL.revokeObjectURL(url)
  }

  if (loading) {
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
        <div style={{ color: 'var(--text-muted)' }}>Loading model configuration...</div>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <h1 style={{ 
            margin: 0, 
            color: 'var(--text-primary)',
            fontSize: '2rem',
            fontWeight: '700'
          }}>
            {config.name}
          </h1>
          <button 
            onClick={() => navigate('/models')}
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
            ← Back to Models
          </button>
        </div>
        <p style={{ 
          color: 'var(--text-muted)', 
          margin: 0,
          fontSize: '1rem'
        }}>
          Configure model parameters and run simulations
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '2rem' }}>
        {/* Configuration Panel */}
        <div>
          {/* Basic Settings */}
          <ConfigSection title="Basic Settings">
            <ConfigField 
              label="Model Name"
              value={config.name}
              onChange={(value) => setConfig(prev => ({ ...prev, name: value }))}
              type="text"
            />
            <ConfigField 
              label="Description"
              value={config.description}
              onChange={(value) => setConfig(prev => ({ ...prev, description: value }))}
              type="textarea"
            />
            <ConfigField 
              label="Model Type"
              value={config.modelType}
              onChange={(value) => setConfig(prev => ({ ...prev, modelType: value as any }))}
              type="select"
              options={[
                { value: 'aquifer', label: 'Aquifer Model' },
                { value: 'well', label: 'Well Model' },
                { value: 'optimization', label: 'Optimization Model' }
              ]}
            />
          </ConfigSection>

          {/* Aquifer Configuration */}
          <ConfigSection title="Aquifer Parameters">
            <ConfigField 
              label="Top Elevation (m)"
              value={config.aquiferConfig.ztop}
              onChange={(value) => updateConfig('aquiferConfig', 'ztop', Number(value))}
              type="number"
            />
            <ConfigField 
              label="Specific Yield"
              value={config.aquiferConfig.specificYield}
              onChange={(value) => updateConfig('aquiferConfig', 'specificYield', Number(value))}
              type="number"
              step="0.001"
            />
            <ConfigField 
              label="Specific Storage"
              value={config.aquiferConfig.specificStorage}
              onChange={(value) => updateConfig('aquiferConfig', 'specificStorage', Number(value))}
              type="number"
              step="0.0001"
            />
            
            {/* Hydraulic Conductivity Layers */}
            <div style={{ marginTop: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: '600', color: 'var(--text-primary)' }}>
                  Hydraulic Conductivity Layers
                </h4>
                <button 
                  onClick={addHydraulicLayer}
                  style={{
                    background: 'var(--blue-500)',
                    color: 'white',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '6px',
                    fontSize: '0.75rem',
                    cursor: 'pointer'
                  }}
                >
                  + Add Layer
                </button>
              </div>
              
              <div style={{
                background: 'var(--bg-panel-accent)',
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
                
                {config.aquiferConfig.hydraulicConductivity.map((layer, index) => (
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
                      onChange={(e) => updateHydraulicLayer(index, 'top', e.target.value)}
                      style={{
                        padding: '0.5rem',
                        borderRadius: '4px',
                        border: '1px solid var(--border-primary)',
                        background: 'var(--bg-card)',
                        color: 'var(--text-primary)',
                        fontSize: '0.875rem'
                      }}
                    />
                    <input 
                      type="number"
                      step="0.1"
                      value={layer.bottom}
                      onChange={(e) => updateHydraulicLayer(index, 'bottom', e.target.value)}
                      style={{
                        padding: '0.5rem',
                        borderRadius: '4px',
                        border: '1px solid var(--border-primary)',
                        background: 'var(--bg-card)',
                        color: 'var(--text-primary)',
                        fontSize: '0.875rem'
                      }}
                    />
                    <input 
                      type="number"
                      step="0.1"
                      value={layer.k}
                      onChange={(e) => updateHydraulicLayer(index, 'k', e.target.value)}
                      style={{
                        padding: '0.5rem',
                        borderRadius: '4px',
                        border: '1px solid var(--border-primary)',
                        background: 'var(--bg-card)',
                        color: 'var(--text-primary)',
                        fontSize: '0.875rem'
                      }}
                    />
                    <button 
                      onClick={() => removeHydraulicLayer(index)}
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
          </ConfigSection>

          {/* Well Configuration */}
          <ConfigSection title="Well Parameters">
            <ConfigField 
              label="Pumping Rate (m³/day)"
              value={config.wellConfig.pumpingRate}
              onChange={(value) => updateConfig('wellConfig', 'pumpingRate', Number(value))}
              type="number"
            />
            <ConfigField 
              label="Well Radius (m)"
              value={config.wellConfig.wellRadius}
              onChange={(value) => updateConfig('wellConfig', 'wellRadius', Number(value))}
              type="number"
              step="0.01"
            />
            <ConfigField 
              label="Screen Top (m)"
              value={config.wellConfig.screenTop}
              onChange={(value) => updateConfig('wellConfig', 'screenTop', Number(value))}
              type="number"
            />
            <ConfigField 
              label="Screen Bottom (m)"
              value={config.wellConfig.screenBottom}
              onChange={(value) => updateConfig('wellConfig', 'screenBottom', Number(value))}
              type="number"
            />
            <ConfigField 
              label="Distance from Well (m)"
              value={config.wellConfig.distanceFromWell}
              onChange={(value) => updateConfig('wellConfig', 'distanceFromWell', Number(value))}
              type="number"
            />
          </ConfigSection>

          {/* Observation Points */}
          <ConfigSection title="Observation Points">
            <div style={{ marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: '600', color: 'var(--text-primary)' }}>
                  Observation Wells
                </h4>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button 
                    onClick={downloadCSVTemplate}
                    style={{
                      background: 'var(--info)',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      cursor: 'pointer'
                    }}
                    title="Download CSV template"
                  >
                    📥 Download Template
                  </button>
                  <label style={{
                    background: csvLoading ? 'var(--text-disabled)' : 'var(--success)',
                    color: 'white',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '6px',
                    fontSize: '0.75rem',
                    cursor: csvLoading ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.25rem',
                    opacity: csvLoading ? 0.7 : 1
                  }}>
                    {csvLoading ? '⏳ Processing...' : '📤 Upload CSV'}
                    <input
                      type="file"
                      accept=".csv"
                      onChange={handleCSVUpload}
                      style={{ display: 'none' }}
                      disabled={csvLoading}
                    />
                  </label>
                  <button 
                    onClick={addObservationPoint}
                    style={{
                      background: 'var(--blue-500)',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      cursor: 'pointer'
                    }}
                  >
                    + Add Manually
                  </button>
                </div>
              </div>

              {config.observationPoints && config.observationPoints.length > 0 ? (
                config.observationPoints.map((point, obsIndex) => (
                <div key={obsIndex} style={{
                  background: 'var(--bg-panel-accent)',
                  border: '1px solid var(--border-primary)',
                  borderRadius: '8px',
                  padding: '1rem',
                  marginBottom: '1rem'
                }}>
                  {/* Observation Point Header */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h5 style={{ margin: 0, fontSize: '0.875rem', fontWeight: '600', color: 'var(--text-primary)' }}>
                      {point.name} ({point.id})
                    </h5>
                    <button 
                      onClick={() => removeObservationPoint(obsIndex)}
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

                  {/* Observation Point Configuration */}
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
                    gap: '1rem',
                    marginBottom: '1rem'
                  }}>
                    <ConfigField 
                      label="Well ID"
                      value={point.id}
                      onChange={(value) => updateObservationPoint(obsIndex, 'id', value)}
                      type="text"
                    />
                    <ConfigField 
                      label="Name"
                      value={point.name}
                      onChange={(value) => updateObservationPoint(obsIndex, 'name', value)}
                      type="text"
                    />
                    <ConfigField 
                      label="Distance (m)"
                      value={point.distanceFromWell}
                      onChange={(value) => updateObservationPoint(obsIndex, 'distanceFromWell', Number(value))}
                      type="number"
                    />
                    <ConfigField 
                      label="Top Screen (m)"
                      value={point.topScreenLevel}
                      onChange={(value) => updateObservationPoint(obsIndex, 'topScreenLevel', Number(value))}
                      type="number"
                    />
                    <ConfigField 
                      label="Bottom Screen (m)"
                      value={point.bottomScreenLevel}
                      onChange={(value) => updateObservationPoint(obsIndex, 'bottomScreenLevel', Number(value))}
                      type="number"
                    />
                  </div>

                  {/* Data Points */}
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <h6 style={{ margin: 0, fontSize: '0.75rem', fontWeight: '600', color: 'var(--text-secondary)' }}>
                        Time Series Data
                      </h6>
                      <button 
                        onClick={() => addDataPoint(obsIndex)}
                        style={{
                          background: 'var(--success)',
                          color: 'white',
                          border: 'none',
                          padding: '0.25rem 0.5rem',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          cursor: 'pointer'
                        }}
                      >
                        + Add Data Point
                      </button>
                    </div>

                    <div style={{
                      background: 'var(--bg-card)',
                      border: '1px solid var(--border-primary)',
                      borderRadius: '6px',
                      overflow: 'hidden',
                      maxHeight: '200px',
                      overflowY: 'auto'
                    }}>
                      <div style={{
                        background: 'var(--bg-panel-accent)',
                        padding: '0.5rem 0.75rem',
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr 1fr auto',
                        gap: '0.75rem',
                        fontSize: '0.75rem',
                        fontWeight: '600',
                        color: 'var(--text-primary)',
                        position: 'sticky',
                        top: 0
                      }}>
                        <div>Time (min)</div>
                        <div>Water Level (m)</div>
                        <div>Drawdown (m)</div>
                        <div>Action</div>
                      </div>
                      
                      {point.dataPoints?.map((dataPoint, dataIndex) => (
                        <div key={dataIndex} style={{
                          padding: '0.5rem 0.75rem',
                          display: 'grid',
                          gridTemplateColumns: '1fr 1fr 1fr auto',
                          gap: '0.75rem',
                          alignItems: 'center',
                          borderTop: '1px solid var(--border-primary)'
                        }}>
                          <input 
                            type="number"
                            step="0.1"
                            value={dataPoint.timeMinutes}
                            onChange={(e) => updateDataPoint(obsIndex, dataIndex, 'timeMinutes', e.target.value)}
                            style={{
                              padding: '0.25rem 0.5rem',
                              borderRadius: '4px',
                              border: '1px solid var(--border-primary)',
                              background: 'var(--bg-card)',
                              color: 'var(--text-primary)',
                              fontSize: '0.75rem'
                            }}
                          />
                          <input 
                            type="number"
                            step="0.01"
                            value={dataPoint.waterLevel}
                            onChange={(e) => updateDataPoint(obsIndex, dataIndex, 'waterLevel', e.target.value)}
                            style={{
                              padding: '0.25rem 0.5rem',
                              borderRadius: '4px',
                              border: '1px solid var(--border-primary)',
                              background: 'var(--bg-card)',
                              color: 'var(--text-primary)',
                              fontSize: '0.75rem'
                            }}
                          />
                          <input 
                            type="number"
                            step="0.01"
                            value={dataPoint.drawdown}
                            onChange={(e) => updateDataPoint(obsIndex, dataIndex, 'drawdown', e.target.value)}
                            style={{
                              padding: '0.25rem 0.5rem',
                              borderRadius: '4px',
                              border: '1px solid var(--border-primary)',
                              background: 'var(--bg-card)',
                              color: 'var(--text-primary)',
                              fontSize: '0.75rem'
                            }}
                          />
                          <button 
                            onClick={() => removeDataPoint(obsIndex, dataIndex)}
                            style={{
                              background: 'var(--error)',
                              color: 'white',
                              border: 'none',
                              padding: '0.125rem 0.25rem',
                              borderRadius: '3px',
                              fontSize: '0.625rem',
                              cursor: 'pointer'
                            }}
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                ))
              ) : (
                <div style={{
                  padding: '2rem',
                  textAlign: 'center',
                  color: 'var(--text-muted)',
                  background: 'var(--bg-panel-accent)',
                  border: '1px solid var(--border-primary)',
                  borderRadius: '8px'
                }}>
                  <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📊</div>
                  <p style={{ margin: 0 }}>No observation points configured</p>
                  <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.875rem' }}>
                    Add observation points to monitor groundwater levels
                  </p>
                </div>
              )}
              
              {/* CSV Format Help */}
              <div style={{
                marginTop: '1rem',
                padding: '1rem',
                background: 'var(--bg-panel-accent)',
                border: '1px solid var(--border-primary)',
                borderRadius: '8px',
                fontSize: '0.875rem'
              }}>
                <h5 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-primary)', fontSize: '0.875rem' }}>
                  📋 CSV Format Requirements
                </h5>
                <div style={{ color: 'var(--text-secondary)', lineHeight: '1.4' }}>
                  <p style={{ margin: '0 0 0.5rem 0' }}>
                    <strong>Required columns:</strong> Time (minutes), Water Level (m), Drawdown (m)
                  </p>
                  <p style={{ margin: '0 0 0.5rem 0' }}>
                    <strong>Format:</strong> Comma-separated values, first row can be headers
                  </p>
                  <p style={{ margin: 0 }}>
                    <strong>Example:</strong> 0,45.3,0 | 5,45.82,0.52 | 10,46.32,1.02
                  </p>
                </div>
              </div>
            </div>
          </ConfigSection>
        </div>

        {/* Simulation Panel */}
        <div>
          <div style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-primary)',
            borderRadius: '12px',
            padding: '1.5rem',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)',
            position: 'sticky',
            top: '1rem'
          }}>
            <h3 style={{ 
              margin: '0 0 1rem 0', 
              color: 'var(--text-primary)',
              fontSize: '1.25rem',
              fontWeight: '600'
            }}>
              Run Simulation
            </h3>

            <ConfigField 
              label="Simulation Time (days)"
              value={config.simulationConfig.simulationTimeDays}
              onChange={(value) => updateConfig('simulationConfig', 'simulationTimeDays', Number(value))}
              type="number"
            />
            
            <ConfigField 
              label="Time Step (days)"
              value={config.simulationConfig.timeStepDays}
              onChange={(value) => updateConfig('simulationConfig', 'timeStepDays', Number(value))}
              type="number"
              step="0.01"
            />

            <ConfigField 
              label="Run Type"
              value={config.simulationConfig.runType}
              onChange={(value) => updateConfig('simulationConfig', 'runType', value)}
              type="select"
              options={[
                { value: 'forward', label: 'Forward Run' },
                { value: 'optimization', label: 'Optimization' }
              ]}
            />

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

            {success && (
              <div style={{ 
                padding: '0.75rem 1rem',
                background: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.2)',
                borderRadius: '8px',
                color: 'var(--success)',
                fontSize: '0.875rem',
                marginBottom: '1rem'
              }}>
                {success}
              </div>
            )}

            <button 
              onClick={handleRunSimulation}
              disabled={running}
              style={{
                width: '100%',
                background: running ? 'var(--text-disabled)' : 'var(--blue-500)',
                color: 'white',
                border: 'none',
                padding: '1rem',
                borderRadius: '8px',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: running ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                marginBottom: '1rem'
              }}
            >
              {running ? 'Starting Simulation...' : '🚀 Run Simulation'}
            </button>

            <div style={{ 
              fontSize: '0.75rem', 
              color: 'var(--text-muted)',
              textAlign: 'center'
            }}>
              Simulation will be queued and processed
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function ConfigSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-primary)',
      borderRadius: '12px',
      padding: '1.5rem',
      marginBottom: '1.5rem',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)'
    }}>
      <h3 style={{ 
        margin: '0 0 1rem 0', 
        color: 'var(--text-primary)',
        fontSize: '1.25rem',
        fontWeight: '600'
      }}>
        {title}
      </h3>
      {children}
    </div>
  )
}

function ConfigField({ 
  label, 
  value, 
  onChange, 
  type, 
  step, 
  options 
}: { 
  label: string
  value: any
  onChange: (value: any) => void
  type: 'text' | 'number' | 'textarea' | 'select'
  step?: string
  options?: Array<{ value: string; label: string }>
}) {
  return (
    <div style={{ marginBottom: '1rem' }}>
      <label style={{ 
        display: 'block', 
        marginBottom: '0.5rem', 
        color: 'var(--text-secondary)',
        fontSize: '0.875rem',
        fontWeight: '500'
      }}>
        {label}
      </label>
      
      {type === 'textarea' ? (
        <textarea 
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={3}
          style={{
            width: '100%',
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            border: '1px solid var(--border-primary)',
            background: 'var(--bg-card)',
            color: 'var(--text-primary)',
            fontSize: '0.875rem',
            boxSizing: 'border-box',
            resize: 'vertical'
          }}
        />
      ) : type === 'select' ? (
        <select 
          value={value}
          onChange={(e) => onChange(e.target.value)}
          style={{
            width: '100%',
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            border: '1px solid var(--border-primary)',
            background: 'var(--bg-card)',
            color: 'var(--text-primary)',
            fontSize: '0.875rem',
            boxSizing: 'border-box'
          }}
        >
          {options?.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : (
        <input 
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          step={step}
          style={{
            width: '100%',
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            border: '1px solid var(--border-primary)',
            background: 'var(--bg-card)',
            color: 'var(--text-primary)',
            fontSize: '0.875rem',
            boxSizing: 'border-box'
          }}
        />
      )}
    </div>
  )
}
