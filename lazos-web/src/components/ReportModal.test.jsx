import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import ReportModal from './ReportModal'

describe('ReportModal Component', () => {
  const mockOnClose = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      })
    )
  })

  it('does not render when isOpen is false', () => {
    const { container } = render(
      <ReportModal isOpen={false} onClose={mockOnClose} postId={1} />
    )
    expect(container.firstChild).toBeNull()
  })

  it('renders correctly when isOpen is true', () => {
    render(
      <ReportModal isOpen={true} onClose={mockOnClose} postId={1} />
    )
    expect(screen.getByText('Reportar publicación')).toBeInTheDocument()
    expect(screen.getByText('Razón del reporte *')).toBeInTheDocument()
    expect(screen.getByText('Spam')).toBeInTheDocument()
  })

  it('disables submit button initially', () => {
    render(
      <ReportModal isOpen={true} onClose={mockOnClose} postId={1} />
    )
    const submitBtn = screen.getByRole('button', { name: /Enviar reporte/i })
    expect(submitBtn).toBeDisabled()
  })

  it('enables submit button after selecting a reason and submits data correctly', async () => {
    render(
      <ReportModal isOpen={true} onClose={mockOnClose} postId={1} />
    )
    
    // Select reason
    const spamRadio = screen.getByLabelText('Spam')
    fireEvent.click(spamRadio)
    
    const submitBtn = screen.getByRole('button', { name: /Enviar reporte/i })
    expect(submitBtn).toBeEnabled()
    
    // Add description
    const descInput = screen.getByPlaceholderText(/Proporciona más detalles/i)
    fireEvent.change(descInput, { target: { value: 'Es un anuncio' } })
    
    // Submit
    fireEvent.click(submitBtn)
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    const fetchCall = global.fetch.mock.calls[0]
    expect(fetchCall[0]).toContain('/api/v1/reports')
    expect(JSON.parse(fetchCall[1].body)).toEqual({
      post_id: 1,
      reason: 'spam',
      description: 'Es un anuncio'
    })
    
    // Shows success state
    expect(await screen.findByText('¡Gracias por reportar!')).toBeInTheDocument()
  })

  it('calls onClose when cancel is clicked', () => {
    render(
      <ReportModal isOpen={true} onClose={mockOnClose} postId={1} />
    )
    
    fireEvent.click(screen.getByRole('button', { name: /Cancelar/i }))
    expect(mockOnClose).toHaveBeenCalled()
  })
})
