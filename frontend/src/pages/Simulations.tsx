import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

interface Simulation {
  id: string
  name: string
  description: string
  simulation_type: string
  status: string
  created_at: string
  updated_at?: string
  completed_at?: string
  simulation_settings?: any
  results?: any
}

export default function Simulations() {
  const { isAuthenticated } = useAuth()
  const [simulations, setSimulations] = useState<Simulation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedSimulation, setSelectedSimulation] = useState<Simulation | null>(null)

  // Resolve CSS variables to concrete colors for Chart.js and keep in sync with theme
  const getCssVar = (name: string) =>
    getComputedStyle(document.documentElement).getPropertyValue(name).trim() || undefined

  const readTheme = () => ({
    textPrimary: getCssVar('--text-primary') || '#111827', // fallback dark text for light mode
    textMuted: getCssVar('--text-muted') || '#6b7280',
    borderPrimary: getCssVar('--border-primary') || 'rgba(0,0,0,0.1)'
  })

  const [theme, setTheme] = useState(readTheme())

  useEffect(() => {
    // Update on system theme changes
    const mql = window.matchMedia('(prefers-color-scheme: dark)')
    const handleMql = () => setTheme(readTheme())
    if (mql.addEventListener) {
      mql.addEventListener('change', handleMql)
    } else {
      // Safari
      // @ts-ignore
      mql.addListener(handleMql)
    }

    // Update when document element attributes/classes change (app-level theme toggle)
    const mo = new MutationObserver(() => setTheme(readTheme()))
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme', 'style'] })

    // Initial sync in case CSS vars load after first render
    const id = window.setTimeout(() => setTheme(readTheme()), 0)

    return () => {
      if (mql.removeEventListener) {
        mql.removeEventListener('change', handleMql)
      } else {
        // @ts-ignore
        mql.removeListener(handleMql)
      }
      mo.disconnect()
      window.clearTimeout(id)
    }
  }, [])

  useEffect(() => {
    if (!isAuthenticated) return

    const fetchSimulations = async () => {
      try {
        console.log('Fetching simulations...')
        const response = await axios.get('/api/v1/simulations/')
        console.log('Simulations response:', response.data)
        setSimulations(response.data)
        if (response.data.length > 0) {
          setSelectedSimulation(response.data[0])
        }
      } catch (e: any) {
        console.error('Error fetching simulations:', e)
        setError(e?.response?.data?.detail || e?.message || 'Failed to load simulations')
      } finally {
        setLoading(false)
      }
    }

    fetchSimulations()
  }, [isAuthenticated])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return '#10b981'
      case 'running': return '#f59e0b'
      case 'pending': return '#6b7280'
      case 'failed': return '#ef4444'
      default: return '#6b7280'
    }
  }

  const LoadingSpinner = () => (
    <div style={{
      display: 'inline-block',
      width: '16px',
      height: '16px',
      border: '2px solid rgba(255, 255, 255, 0.3)',
      borderRadius: '50%',
      borderTopColor: '#ffffff',
      animation: 'spin 1s ease-in-out infinite'
    }} />
  )

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return '✅'
      case 'running': return <LoadingSpinner />
      case 'pending': return <LoadingSpinner />
      case 'failed': return '❌'
      default: return '❓'
    }
  }

  const createDrawdownChart = (wellData: any, wellId: string) => {
    try {
      if (!wellData?.simulation_results || !wellData?.interpolation_results) {
        return {
          labels: [],
          datasets: []
        }
      }

      const observedTimes = wellData.simulation_results.observed_time_seconds.map((t: number) => t / 60) // Convert to minutes
      const observedDrawdown = wellData.simulation_results.observed_drawdown_meters
      const simulatedDrawdown = wellData.simulation_results.simulated_drawdown_meters
      const interpolatedTimes = wellData.interpolation_results.interpolated_times.map((t: number) => t / 60)
      const interpolatedObserved = wellData.interpolation_results.interpolated_observed_drawdown
      const interpolatedSimulated = wellData.interpolation_results.interpolated_simulated_drawdown

      return {
        labels: [...observedTimes, ...interpolatedTimes].sort((a, b) => a - b),
        datasets: [
          {
            label: 'Observed Drawdown',
            data: [...observedDrawdown, ...interpolatedObserved],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 3,
            pointRadius: 5,
            pointHoverRadius: 8,
            pointBackgroundColor: '#3b82f6',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            tension: 0.1,
          },
          {
            label: 'Simulated Drawdown',
            data: [...simulatedDrawdown, ...interpolatedSimulated],
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            borderWidth: 3,
            pointRadius: 5,
            pointHoverRadius: 8,
            pointBackgroundColor: '#ef4444',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            tension: 0.1,
          }
        ]
      }
    } catch (error) {
      console.error(`Error creating drawdown chart for ${wellId}:`, error)
      return {
        labels: [],
        datasets: []
      }
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
            Please log in to view simulations
          </h3>
          <p style={{ color: 'var(--text-disabled)', margin: 0 }}>
            Authentication required to access simulation data
          </p>
        </div>
      </div>
    )
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
        <div style={{ textAlign: 'center' }}>
          <h3 style={{ color: 'var(--text-muted)', margin: '0 0 1rem 0' }}>
            Loading simulations...
          </h3>
          <p style={{ color: 'var(--text-disabled)', margin: 0 }}>
            Please wait while we fetch your simulation data
          </p>
        </div>
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
        background: 'var(--bg-card)',
        borderRadius: '12px',
        border: '1px solid var(--border-primary)'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h3 style={{ color: '#ef4444', margin: '0 0 1rem 0' }}>
            Error Loading Simulations
          </h3>
          <p style={{ color: 'var(--text-disabled)', margin: 0 }}>
            {error}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div style={{ padding: '2rem', color: 'var(--text-primary)' }}>
      {/* CSS Animation for Loading Spinner */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
      
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ margin: '0 0 0.5rem 0', fontSize: '2rem', fontWeight: 'bold' }}>
          Simulation Results Dashboard
        </h1>
        <p style={{ color: 'var(--text-muted)', margin: 0 }}>
          Beautiful visualizations and analysis of your simulation data
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
        {/* Simulation List */}
        <div style={{
          background: 'var(--bg-card)',
          borderRadius: '12px',
          border: '1px solid var(--border-primary)',
          padding: '1.5rem',
          height: 'fit-content'
        }}>
          <h2 style={{ margin: '0 0 1rem 0', fontSize: '1.25rem', fontWeight: '600' }}>
            Simulations ({simulations.length})
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {simulations.map((sim) => (
              <div
                key={sim.id}
                onClick={() => setSelectedSimulation(sim)}
                style={{
                  padding: '1rem',
                  borderRadius: '8px',
                  border: '1px solid var(--border-primary)',
                  background: 'var(--bg-secondary)',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  boxShadow: selectedSimulation?.id === sim.id 
                    ? '0 0 0 3px #3b82f6, 0 0 15px rgba(59, 130, 246, 0.6), 0 0 30px rgba(59, 130, 246, 0.4), 0 0 45px rgba(59, 130, 246, 0.2)' 
                    : 'none',
                  transform: selectedSimulation?.id === sim.id ? 'scale(1.02)' : 'scale(1)',
                }}
                onMouseEnter={(e) => {
                  if (selectedSimulation?.id !== sim.id) {
                    e.currentTarget.style.boxShadow = '0 0 0 2px #3b82f6, 0 0 8px rgba(59, 130, 246, 0.4)'
                    e.currentTarget.style.transform = 'scale(1.01)'
                  }
                }}
                onMouseLeave={(e) => {
                  if (selectedSimulation?.id !== sim.id) {
                    e.currentTarget.style.boxShadow = 'none'
                    e.currentTarget.style.transform = 'scale(1)'
                  }
                }}
              >
                <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem', fontWeight: '600' }}>
                  {sim.name}
                </h3>
                <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                  {sim.description}
                </p>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{
                    padding: '0.25rem 0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.75rem',
                    fontWeight: '500',
                    background: getStatusColor(sim.status),
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.25rem'
                  }}>
                    {getStatusIcon(sim.status)} {sim.status}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-disabled)' }}>
                    {formatDate(sim.created_at)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Simulation Visualizations */}
        {selectedSimulation && (
          <div style={{
            background: 'var(--bg-card)',
            borderRadius: '12px',
            border: '1px solid var(--border-primary)',
            padding: '1.5rem'
          }}>
            <div style={{ marginBottom: '2rem' }}>
              <h2 style={{ margin: '0 0 0.5rem 0', fontSize: '1.5rem', fontWeight: '600' }}>
                {selectedSimulation.name}
              </h2>
              <p style={{ margin: '0 0 1rem 0', color: 'var(--text-muted)' }}>
                {selectedSimulation.description}
              </p>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <span style={{
                  padding: '0.5rem 1rem',
                  borderRadius: '6px',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  background: getStatusColor(selectedSimulation.status),
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}>
                  {getStatusIcon(selectedSimulation.status)} {selectedSimulation.status}
                </span>
                <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                  {selectedSimulation.simulation_type}
                </span>
              </div>
            </div>

            {/* Summary Cards */}
            {selectedSimulation.results?.summary && (
              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.25rem', fontWeight: '600' }}>
                  Simulation Summary
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                  <div style={{
                    padding: '1.5rem',
                    borderRadius: '12px',
                    background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
                    color: 'white',
                    textAlign: 'center'
                  }}>
                    <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', opacity: 0.9 }}>
                      Radius of Influence
                    </h4>
                    <p style={{ margin: 0, fontSize: '1.5rem', fontWeight: 'bold' }}>
                      {selectedSimulation.results.summary.radius_of_influence_meters?.toFixed(2)} m
                    </p>
                  </div>
                  
                  <div style={{
                    padding: '1.5rem',
                    borderRadius: '12px',
                    background: 'linear-gradient(135deg, #10b981, #059669)',
                    color: 'white',
                    textAlign: 'center'
                  }}>
                    <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', opacity: 0.9 }}>
                      Wells Analyzed
                    </h4>
                    <p style={{ margin: 0, fontSize: '1.5rem', fontWeight: 'bold' }}>
                      {selectedSimulation.results.summary.total_wells_analyzed}
                    </p>
                  </div>
                  
                  {selectedSimulation.results?.metadata && (
                    <>
                      <div style={{
                        padding: '1.5rem',
                        borderRadius: '12px',
                        background: 'linear-gradient(135deg, #f59e0b, #d97706)',
                        color: 'white',
                        textAlign: 'center'
                      }}>
                        <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', opacity: 0.9 }}>
                          Duration
                        </h4>
                        <p style={{ margin: 0, fontSize: '1.5rem', fontWeight: 'bold' }}>
                          {formatDuration(selectedSimulation.results.metadata.pumping_length_seconds)}
                        </p>
                      </div>
                      
                      <div style={{
                        padding: '1.5rem',
                        borderRadius: '12px',
                        background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
                        color: 'white',
                        textAlign: 'center'
                      }}>
                        <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', opacity: 0.9 }}>
                          Time Steps
                        </h4>
                        <p style={{ margin: 0, fontSize: '1.5rem', fontWeight: 'bold' }}>
                          {selectedSimulation.results.metadata.total_simulation_time_steps}
                        </p>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Drawdown Analysis Charts */}
            {selectedSimulation.results?.wells && (
              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.25rem', fontWeight: '600' }}>
                  Drawdown Analysis
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem' }}>
                  {Object.entries(selectedSimulation.results.wells).map(([wellId, wellData]) => {
                    const chartData = createDrawdownChart(wellData, wellId)
                    return (
                      <div key={wellId} style={{
                        padding: '1.5rem',
                        borderRadius: '12px',
                        background: 'var(--bg-secondary)',
                        border: '1px solid var(--border-primary)'
                      }}>
                        <h4 style={{ margin: '0 0 1rem 0', fontSize: '1rem', fontWeight: '600' }}>
                          {wellId} - RMSE: {wellData.interpolation_results.rmse.toFixed(4)}
                        </h4>
                        <div style={{ height: '300px' }}>
                          <Line
                            data={chartData}
                            options={{
                              responsive: true,
                              maintainAspectRatio: false,
                              plugins: {
                                title: {
                                  display: true,
                                  text: `Drawdown vs Time - ${wellId}`,
                                  color: theme.textPrimary,
                                  font: { size: 14, weight: 'bold' }
                                },
                                legend: {
                                  labels: {
                                    color: theme.textPrimary,
                                    usePointStyle: true,
                                    padding: 20
                                  }
                                },
                                tooltip: {
                                  backgroundColor: 'rgba(0, 0, 0, 0.8)',
                                  titleColor: 'white',
                                  bodyColor: 'white',
                                  borderColor: theme.borderPrimary,
                                  borderWidth: 1
                                }
                              },
                              scales: {
                                x: {
                                  title: {
                                    display: true,
                                    text: 'Time (minutes)',
                                    color: theme.textPrimary,
                                    font: { weight: 'bold' }
                                  },
                                  ticks: {
                                    color: theme.textMuted
                                  },
                                  grid: {
                                    color: theme.borderPrimary,
                                    drawBorder: false
                                  }
                                },
                                y: {
                                  title: {
                                    display: true,
                                    text: 'Drawdown (meters)',
                                    color: theme.textPrimary,
                                    font: { weight: 'bold' }
                                  },
                                  ticks: {
                                    color: theme.textMuted
                                  },
                                  grid: {
                                    color: theme.borderPrimary,
                                    drawBorder: false
                                  }
                                }
                              },
                              interaction: {
                                intersect: false,
                                mode: 'index'
                              }
                            }}
                          />
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}


            {/* Optimization Results */}
            {selectedSimulation.results?.optimization_results && (
              <div>
                <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.25rem', fontWeight: '600' }}>
                  Optimization Results
                </h3>
                
                <div style={{ marginBottom: '1.5rem' }}>
                  <h4 style={{ margin: '0 0 1rem 0', fontSize: '1rem', fontWeight: '600' }}>
                    Optimal Parameter Values
                  </h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
                    {/* Specific Yield Card */}
                    <div style={{
                      padding: '1.5rem',
                      borderRadius: '12px',
                      background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
                      color: 'white',
                      textAlign: 'center'
                    }}>
                      <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', opacity: 0.9 }}>
                        Specific Yield
                      </h4>
                      <p style={{ margin: 0, fontSize: '1.5rem', fontWeight: 'bold' }}>
                        {selectedSimulation.results.optimization_results.optimal_values.specific_yield.toFixed(6)}
                      </p>
                    </div>
                    
                    {/* Specific Storage Card */}
                    <div style={{
                      padding: '1.5rem',
                      borderRadius: '12px',
                      background: 'linear-gradient(135deg, #10b981, #059669)',
                      color: 'white',
                      textAlign: 'center'
                    }}>
                      <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', opacity: 0.9 }}>
                        Specific Storage
                      </h4>
                      <p style={{ margin: 0, fontSize: '1.5rem', fontWeight: 'bold' }}>
                        {(selectedSimulation.results.optimization_results.optimal_values.specific_storage * 1e6).toFixed(2)} × 10⁻⁶
                      </p>
                    </div>
                    
                    {/* Hydraulic Conductivity Cards */}
                    {selectedSimulation.results.optimization_results.optimal_values.hk_profile && 
                     Object.entries(selectedSimulation.results.optimization_results.optimal_values.hk_profile).map(([layer, value], index) => {
                      // Convert technical layer names to user-friendly names
                      const getLayerDisplayName = (layerName: string) => {
                        if (layerName.includes('layer_0.0m_to_-350.0m')) {
                          return 'Layer 1 (0m to -350m)'
                        } else if (layerName.includes('layer_-350.0m_to_-700.0m')) {
                          return 'Layer 2 (-350m to -700m)'
                        } else if (layerName.includes('hk_layer_1')) {
                          return 'Layer 1'
                        } else if (layerName.includes('hk_layer_2')) {
                          return 'Layer 2'
                        } else if (layerName.includes('hk_layer_3')) {
                          return 'Layer 3'
                        } else if (layerName.includes('hk_layer_4')) {
                          return 'Layer 4'
                        } else {
                          // Fallback: clean up the layer name
                          return layerName.replace('layer_', 'Layer ').replace('hk_', '').replace('_', ' ')
                        }
                      }
                      
                      return (
                        <div key={layer} style={{
                          padding: '1.5rem',
                          borderRadius: '12px',
                          background: `linear-gradient(135deg, hsl(${200 + index * 40}, 70%, 50%), hsl(${200 + index * 40}, 70%, 30%))`,
                          color: 'white',
                          textAlign: 'center'
                        }}>
                          <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', opacity: 0.9 }}>
                            Hydraulic Conductivity
                          </h4>
                          <p style={{ margin: '0 0 0.25rem 0', fontSize: '0.75rem', opacity: 0.8 }}>
                            {getLayerDisplayName(layer)}
                          </p>
                          <p style={{ margin: 0, fontSize: '1.5rem', fontWeight: 'bold' }}>
                            {Number(value).toFixed(3)} m/day
                          </p>
                        </div>
                      )
                    })}
                  </div>
                </div>
                
                {/* Parameters Optimized Info */}
                <div style={{
                  padding: '1rem',
                  borderRadius: '8px',
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-primary)'
                }}>
                  <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', fontWeight: '600' }}>
                    Parameters Optimized
                  </h4>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {selectedSimulation.results.optimization_results.parameters_optimized.map((param: string, index: number) => {
                      // Convert technical parameter names to user-friendly names
                      const getParameterDisplayName = (paramName: string) => {
                        if (paramName === 'hk_layer_1') return 'Layer 1 K'
                        if (paramName === 'hk_layer_2') return 'Layer 2 K'
                        if (paramName === 'hk_layer_3') return 'Layer 3 K'
                        if (paramName === 'hk_layer_4') return 'Layer 4 K'
                        if (paramName === 'sy') return 'Specific Yield'
                        if (paramName === 'ss') return 'Specific Storage'
                        return paramName // Fallback to original name
                      }
                      
                      return (
                        <span key={param} style={{
                          padding: '0.25rem 0.75rem',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          fontWeight: '500',
                          background: `hsl(${200 + index * 40}, 70%, 90%)`,
                          color: `hsl(${200 + index * 40}, 70%, 20%)`,
                          border: `1px solid hsl(${200 + index * 40}, 70%, 70%)`
                        }}>
                          {getParameterDisplayName(param)}
                        </span>
                      )
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}