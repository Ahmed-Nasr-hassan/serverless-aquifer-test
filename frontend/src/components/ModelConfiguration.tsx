import React from 'react'

interface ParameterFieldProps {
  label: string
  value: number | string
  unit?: string
  onChange?: (value: number | string) => void
  editable?: boolean
  type?: 'number' | 'text' | 'select'
  options?: string[]
  fieldEditable?: boolean // Allow individual field to override section editable setting
}

export function ParameterField({ 
  label, 
  value, 
  unit, 
  onChange, 
  editable = false, 
  type = 'number',
  options = [],
  fieldEditable
}: ParameterFieldProps) {
  const isNumeric = typeof value === 'number' || (typeof value === 'string' && !isNaN(Number(value)) && value !== '')
  const isEditable = fieldEditable !== undefined ? fieldEditable : editable

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '0.25rem',
      minWidth: '200px'
    }}>
      <label style={{
        fontSize: '0.875rem',
        fontWeight: '500',
        color: 'var(--text-primary)',
        marginBottom: '0.25rem'
      }}>
        {label}
      </label>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem'
      }}>
        {isEditable ? (
          type === 'select' ? (
            <select
              value={value}
              onChange={(e) => onChange?.(e.target.value)}
              style={{
                flex: 1,
                padding: '0.5rem',
                border: '1px solid var(--border-primary)',
                borderRadius: '6px',
                background: 'var(--bg-card)',
                color: 'var(--text-primary)',
                fontSize: '0.875rem',
                minWidth: '120px'
              }}
            >
              {options.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          ) : (
            <input
              type={isNumeric ? 'number' : 'text'}
              value={value}
              onChange={(e) => onChange?.(isNumeric ? Number(e.target.value) : e.target.value)}
              style={{
                flex: 1,
                padding: '0.5rem',
                border: '1px solid var(--border-primary)',
                borderRadius: '6px',
                background: 'var(--bg-card)',
                color: 'var(--text-primary)',
                fontSize: '0.875rem',
                minWidth: '80px'
              }}
            />
          )
        ) : (
          <span style={{
            padding: '0.5rem',
            background: 'var(--bg-panel)',
            border: '1px solid var(--border-primary)',
            borderRadius: '6px',
            color: 'var(--text-primary)',
            fontSize: '0.875rem',
            minWidth: '80px',
            textAlign: 'center'
          }}>
            {value}
          </span>
        )}
        {unit && (
          <span style={{
            fontSize: '0.75rem',
            color: 'var(--text-muted)',
            fontWeight: '500',
            minWidth: '30px'
          }}>
            {unit}
          </span>
        )}
      </div>
    </div>
  )
}

interface SectionCardProps {
  title: string
  icon: string
  children: React.ReactNode
  editable?: boolean
  onEdit?: () => void
}

export function SectionCard({ title, icon, children, editable = false, onEdit }: SectionCardProps) {
  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-primary)',
      borderRadius: '12px',
      padding: '1.5rem',
      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
      transition: 'all 0.2s ease'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '1.5rem',
        paddingBottom: '1rem',
        borderBottom: '1px solid var(--border-primary)'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem'
        }}>
          <div style={{
            fontSize: '1.5rem',
            width: '2rem',
            height: '2rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--blue-50)',
            borderRadius: '8px',
            color: 'var(--blue-600)'
          }}>
            {icon}
          </div>
          <h3 style={{
            margin: 0,
            fontSize: '1.25rem',
            fontWeight: '600',
            color: 'var(--text-primary)'
          }}>
            {title}
          </h3>
        </div>
        {editable && onEdit && (
          <button
            onClick={onEdit}
            style={{
              background: 'var(--blue-500)',
              color: 'white',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              fontSize: '0.875rem',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--blue-600)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'var(--blue-500)'
            }}
          >
            Edit
          </button>
        )}
      </div>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '1.5rem'
      }}>
        {children}
      </div>
    </div>
  )
}

interface DiscretizationSectionProps {
  data: any
  editable?: boolean
  onChange?: (field: string, value: number) => void
}

export function RadialDiscretizationSection({ data, editable = false, onChange }: DiscretizationSectionProps) {
  const fields = [
    {
      key: 'boundary_distance_from_pumping_well',
      label: 'Boundary distance from pumping well',
      value: data?.boundary_distance_from_pumping_well?.value || 500,
      unit: data?.boundary_distance_from_pumping_well?.unit || 'm'
    },
    {
      key: 'second_column_size',
      label: '2nd Column Size',
      value: data?.second_column_size?.value || 0.01,
      unit: data?.second_column_size?.unit || 'm'
    },
    {
      key: 'column_multiplier',
      label: 'Column Multiplier',
      value: data?.column_multiplier?.value || 1.1,
      unit: undefined
    }
  ]

  return (
    <SectionCard 
      title="Radial Discretization" 
      icon="📏"
      editable={editable}
    >
      {fields.map(field => (
        <ParameterField
          key={field.key}
          label={field.label}
          value={field.value}
          unit={field.unit}
          editable={editable}
          onChange={(value) => onChange?.(field.key, value)}
        />
      ))}
    </SectionCard>
  )
}

export function VerticalDiscretizationSection({ data, editable = false, onChange }: DiscretizationSectionProps) {
  const fields = [
    {
      key: 'saturated_top_elevation',
      label: 'Saturated top elevation',
      value: data?.saturated_top_elevation?.value || -121.84,
      unit: data?.saturated_top_elevation?.unit || 'm'
    },
    {
      key: 'aquifer_bottom_elevation',
      label: 'Aquifer bottom elevation',
      value: data?.aquifer_bottom_elevation?.value || -500,
      unit: data?.aquifer_bottom_elevation?.unit || 'm'
    },
    {
      key: 'screen_top_cell_thickness',
      label: 'Screen top - Cell thickness',
      value: data?.screen_top_cell_thickness?.value || 0.01,
      unit: data?.screen_top_cell_thickness?.unit || 'm'
    },
    {
      key: 'screen_bottom_cell_thickness',
      label: 'Screen bottom- Cell thickness',
      value: data?.screen_bottom_cell_thickness?.value || 0.01,
      unit: data?.screen_bottom_cell_thickness?.unit || 'm'
    },
    {
      key: 'refinement_above_screen',
      label: 'Refinment above screen',
      value: data?.refinement_above_screen?.value || 1.6,
      unit: undefined
    },
    {
      key: 'refinement_below_screen',
      label: 'Refinment below screen',
      value: data?.refinement_below_screen?.value || 1.3,
      unit: undefined
    },
    {
      key: 'refinement_between_screen',
      label: 'Refinment between screen',
      value: data?.refinement_between_screen?.value || 1.1,
      unit: undefined
    }
  ]

  return (
    <SectionCard 
      title="Vertical Discretization" 
      icon="📐"
      editable={editable}
    >
      {fields.map(field => (
        <ParameterField
          key={field.key}
          label={field.label}
          value={field.value}
          unit={field.unit}
          editable={editable}
          onChange={(value) => onChange?.(field.key, value)}
        />
      ))}
    </SectionCard>
  )
}

export function PumpingWellSection({ data, editable = false, onChange }: DiscretizationSectionProps) {
  const fields = [
    {
      key: 'well_radius',
      label: 'Well Radius',
      value: data?.well_radius?.value || 0.22,
      unit: data?.well_radius?.unit || 'm'
    },
    {
      key: 'pumping_rate',
      label: 'Q',
      value: data?.pumping_rate?.value || -141,
      unit: data?.pumping_rate?.unit || 'm³/hr'
    },
    {
      key: 'screen_top_elevation',
      label: 'Screen Top Elevation',
      value: data?.screen_top_elevation?.value || -212,
      unit: data?.screen_top_elevation?.unit || 'm'
    },
    {
      key: 'screen_bottom_elevation',
      label: 'Screen Bottom Elevation',
      value: data?.screen_bottom_elevation?.value || -378,
      unit: data?.screen_bottom_elevation?.unit || 'm'
    }
  ]

  return (
    <SectionCard 
      title="Pumping Well" 
      icon="🕳️"
      editable={editable}
    >
      {fields.map(field => (
        <ParameterField
          key={field.key}
          label={field.label}
          value={field.value}
          unit={field.unit}
          editable={editable}
          onChange={(value) => onChange?.(field.key, value)}
        />
      ))}
    </SectionCard>
  )
}

export function InitialBoundaryConditionsSection({ data, editable = false, onChange }: DiscretizationSectionProps) {
  const fields = [
    {
      key: 'starting_head',
      label: 'Starting Head',
      value: data?.starting_head?.value || -121.84,
      unit: data?.starting_head?.unit || 'm'
    },
    {
      key: 'specified_head',
      label: 'Specified Head',
      value: data?.specified_head?.value || -121.84,
      unit: data?.specified_head?.unit || 'm'
    }
  ]

  return (
    <SectionCard 
      title="Initial Boundary Conditions" 
      icon="🌊"
      editable={editable}
    >
      {fields.map(field => (
        <ParameterField
          key={field.key}
          label={field.label}
          value={field.value}
          unit={field.unit}
          editable={editable}
          onChange={(value) => onChange?.(field.key, value)}
        />
      ))}
    </SectionCard>
  )
}

export function StressPeriodsSection({ data, editable = false, onChange }: DiscretizationSectionProps) {
  const analysisPeriod = data?.analysis_period?.value || 'Pumping + Recovery'
  
  const allFields = [
    {
      key: 'analysis_period',
      label: 'Analysis Period',
      value: analysisPeriod,
      unit: undefined,
      type: 'select' as const,
      options: ['Pumping + Recovery', 'Pumping Only', 'Recovery Only'],
      show: true // Always show this field
    },
    {
      key: 'pumping_length',
      label: 'Pumping length',
      value: data?.pumping_length?.value || 2966,
      unit: data?.pumping_length?.unit || 'minutes',
      type: 'number' as const,
      show: analysisPeriod === 'Pumping + Recovery' || analysisPeriod === 'Pumping Only'
    },
    {
      key: 'recovery_length',
      label: 'Recovery length',
      value: data?.recovery_length?.value || 1200,
      unit: data?.recovery_length?.unit || 'minutes',
      type: 'number' as const,
      show: analysisPeriod === 'Pumping + Recovery' || analysisPeriod === 'Recovery Only'
    },
    {
      key: 'number_of_time_steps',
      label: 'Number of time steps',
      value: data?.number_of_time_steps?.value || 200,
      unit: undefined,
      type: 'number' as const,
      show: true // Always show this field
    },
    {
      key: 'time_multiplier',
      label: 'Time Multiplier',
      value: data?.time_multiplier?.value || 1.05,
      unit: undefined,
      type: 'number' as const,
      show: true // Always show this field
    },
    {
      key: 'time_units',
      label: 'Time Units',
      value: data?.time_units?.value || 'SECONDS',
      unit: undefined,
      type: 'text' as const,
      show: true, // Always show this field
      editable: false // Make this field read-only
    }
  ]

  // Filter fields based on analysis period
  const visibleFields = allFields.filter(field => field.show)

  return (
    <SectionCard 
      title="Stress Periods" 
      icon="⏱️"
      editable={editable}
    >
      {visibleFields.map(field => (
        <ParameterField
          key={field.key}
          label={field.label}
          value={field.value}
          unit={field.unit}
          editable={editable}
          type={field.type}
          options={field.options}
          fieldEditable={field.editable}
          onChange={(value) => onChange?.(field.key, value)}
        />
      ))}
    </SectionCard>
  )
}
