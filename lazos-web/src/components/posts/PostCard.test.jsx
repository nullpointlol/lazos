import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import PostCard from './PostCard'

// Mock react-router-dom navigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate
  }
})

describe('PostCard Component', () => {
  const mockPost = {
    id: 1,
    animal_type: 'dog',
    size: 'medium',
    sex: 'male',
    description: 'Perrito perdido en la plaza.',
    location_name: 'Plaza San Martin',
    sighting_date: new Date().toISOString(),
    thumbnail_url: 'http://example.com/image.jpg',
    image_count: 1
  }

  const renderWithRouter = (component) => {
    return render(<BrowserRouter>{component}</BrowserRouter>)
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders post details correctly', () => {
    renderWithRouter(<PostCard post={mockPost} />)
    
    expect(screen.getByText('Perro')).toBeInTheDocument()
    expect(screen.getByText('· Mediano')).toBeInTheDocument()
    expect(screen.getByText('Plaza San Martin')).toBeInTheDocument()
    expect(screen.getByText('Perrito perdido en la plaza.')).toBeInTheDocument()
    expect(screen.getByRole('img')).toHaveAttribute('src', mockPost.thumbnail_url)
  })

  it('calls onClick when card is clicked', () => {
    const handleClick = vi.fn()
    renderWithRouter(<PostCard post={mockPost} onClick={handleClick} />)
    
    // Click on the text 'Perro' to trigger card click
    fireEvent.click(screen.getByText('Perro'))
    
    expect(handleClick).toHaveBeenCalledWith(mockPost)
    expect(mockNavigate).toHaveBeenCalledWith('/post/1')
  })

  it('truncates long descriptions and toggles read more', () => {
    const longPost = {
      ...mockPost,
      description: 'A'.repeat(100) // over 80 chars
    }
    renderWithRouter(<PostCard post={longPost} />)
    
    const readMoreBtn = screen.getByText('Leer más')
    expect(readMoreBtn).toBeInTheDocument()
    
    fireEvent.click(readMoreBtn)
    expect(screen.getByText('Leer menos')).toBeInTheDocument()
  })
})
