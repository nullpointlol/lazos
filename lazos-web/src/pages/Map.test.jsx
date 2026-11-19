import { describe, it, expect, vi, beforeEach } from 'vitest'
import { forwardRef } from 'react'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Map from './Map'

vi.mock('react-leaflet', () => ({
  MapContainer: forwardRef(({ children }, ref) => <div ref={ref} data-testid="map-container">{children}</div>),
  TileLayer: () => <div data-testid="tile-layer" />,
  Marker: ({ children }) => <div data-testid="marker">{children}</div>,
  Popup: ({ children }) => <div data-testid="popup">{children}</div>,
  useMap: () => ({ fitBounds: vi.fn(), setView: vi.fn() })
}))

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Locate: () => <div data-testid="icon-locate" />,
  Filter: () => <div data-testid="icon-filter" />,
  X: () => <div data-testid="icon-x" />
}))

describe('Map Page Component', () => {
  const mockData = {
    posts: [
      { id: 1, lat: -34.6, lon: -58.4, animal_type: 'dog', thumbnail_url: 'img1.jpg' }
    ],
    alerts: [
      { id: 2, lat: -34.7, lon: -58.5, animal_type: 'cat', description: 'Gato gris' }
    ]
  }

  beforeEach(() => {
    vi.clearAllMocks()
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockData),
      })
    )
  })

  const renderWithRouter = (component) => {
    return render(<BrowserRouter>{component}</BrowserRouter>)
  }

  it('renders map container and fetches data', async () => {
    renderWithRouter(<Map />)
    
    // Shows loading initially
    expect(screen.getByText('Cargando mapa...')).toBeInTheDocument()
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })
    
    expect(global.fetch.mock.calls[0][0]).toContain('/api/v1/map/points/unified')
    
    // Renders markers
    const markers = await screen.findAllByTestId('marker')
    expect(markers).toHaveLength(2) // 1 post + 1 alert
    
    // Map container exists
    expect(screen.getByTestId('map-container')).toBeInTheDocument()
  })

  it('toggles filters panel', async () => {
    renderWithRouter(<Map />)
    
    const filterBtn = screen.getByTitle('Filtros')
    fireEvent.click(filterBtn)
    
    // Filters panel should open
    expect(screen.getByText('Tipo de animal')).toBeInTheDocument()
    
    // Select filter
    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: 'dog' } })
    
    await waitFor(() => {
      // Second fetch with query params
      expect(global.fetch).toHaveBeenCalledTimes(2)
      expect(global.fetch.mock.calls[1][0]).toContain('animal_type=dog')
    })
  })
})
