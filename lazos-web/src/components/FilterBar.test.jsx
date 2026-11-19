import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import FilterBar from './FilterBar'

describe('FilterBar Component', () => {
  const mockAvailableFilters = {
    provincias: [{ value: 'Buenos Aires', count: 10 }],
    localidades: [{ value: 'La Plata', count: 5 }],
    animal_types: [{ value: 'dog', count: 7 }],
    sizes: [{ value: 'medium', count: 8 }],
    sexes: [{ value: 'male', count: 6 }]
  }

  const mockOnFiltersChange = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders correctly with closed state', () => {
    render(
      <FilterBar 
        filters={{}} 
        onFiltersChange={mockOnFiltersChange} 
        availableFilters={mockAvailableFilters} 
        totalResults={10} 
      />
    )
    
    expect(screen.getByText('Filtros')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument() // totalResults
    expect(screen.getByText('publicaciones encontradas')).toBeInTheDocument()
  })

  it('expands when clicking filters button and shows options', () => {
    render(
      <FilterBar 
        filters={{}} 
        onFiltersChange={mockOnFiltersChange} 
        availableFilters={mockAvailableFilters} 
        totalResults={10} 
      />
    )
    
    const toggleBtn = screen.getByRole('button', { name: /Filtros/i })
    fireEvent.click(toggleBtn)
    
    expect(screen.getByText('Provincia')).toBeInTheDocument()
    expect(screen.getByText('Fecha')).toBeInTheDocument()
    expect(screen.getByText('Perro (7)')).toBeInTheDocument()
  })

  it('calls onFiltersChange when a filter is clicked', () => {
    render(
      <FilterBar 
        filters={{}} 
        onFiltersChange={mockOnFiltersChange} 
        availableFilters={mockAvailableFilters} 
        totalResults={10} 
      />
    )
    
    // Open filters
    fireEvent.click(screen.getByRole('button', { name: /Filtros/i }))
    
    // Click on dog filter
    fireEvent.click(screen.getByText('Perro (7)'))
    
    expect(mockOnFiltersChange).toHaveBeenCalledWith({ animal_type: 'dog' })
  })

  it('renders active filter chips and allows clearing them', () => {
    render(
      <FilterBar 
        filters={{ animal_type: 'dog' }} 
        onFiltersChange={mockOnFiltersChange} 
        availableFilters={mockAvailableFilters} 
        totalResults={10} 
      />
    )
    
    // Chip should be visible
    expect(screen.getByText('Perro')).toBeInTheDocument()
    
    // Clear all filters button
    const clearBtn = screen.getByText('Limpiar filtros')
    fireEvent.click(clearBtn)
    
    expect(mockOnFiltersChange).toHaveBeenCalledWith({})
  })
})
