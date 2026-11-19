import { describe, test, expect, vi } from 'vitest'
import { validateText, containsContactInfo, sanitizeText } from './validateText'

describe('validateText Utilities', () => {
  // Test validateText function rules
  describe('validateText()', () => {
    test('should approve standard valid descriptions', () => {
      const result = validateText('Se busca perrito caniche blanco extraviado por la zona de Palermo de manera urgente.')
      expect(result.valid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    test('should enforce minimum length rule (10 chars)', () => {
      const result = validateText('Perrito')
      expect(result.valid).toBe(false)
      expect(result.errors).toContain('La descripción debe tener al menos 10 caracteres')
    })

    test('should reject descriptions without letters', () => {
      const result = validateText('🐈🐶🐾💔😢🚗🚗')
      expect(result.valid).toBe(false)
      expect(result.errors).toContain('La descripción debe contener texto, no solo emojis o símbolos')
    })

    test('should detect repetitious spam words', () => {
      const result = validateText('perdido perdido perdido perdido perdido perdido perdido perdido')
      expect(result.valid).toBe(false)
      expect(result.errors).toContain('El texto parece ser spam (demasiadas palabras repetidas)')
    })

    test('should detect excessive capitalization', () => {
      const result = validateText('SE BUSCA URGENTE POR FAVOR AYUDA MI MASCOTA CANICHE SE PERDIO')
      expect(result.valid).toBe(false)
      expect(result.errors).toContain('Evitá usar MAYÚSCULAS en exceso')
    })

    test('should reject basic offensive words', () => {
      const result = validateText('Este es un post estúpido boludo de mierda')
      expect(result.valid).toBe(false)
      expect(result.errors).toContain('La descripción contiene lenguaje inapropiado')
    })

    test('should reject phone numbers embedded directly in descriptions', () => {
      const result = validateText('Gatito negro encontrado cerca de Plaza Italia por favor llamar al 11-2345-6789 urgente')
      expect(result.valid).toBe(false)
      expect(result.errors).toContain('No incluyas números de teléfono en la descripción. Usá el campo de contacto')
    })
  })

  // Test containsContactInfo helper
  describe('containsContactInfo()', () => {
    test('should return true for phone numbers', () => {
      expect(containsContactInfo('Llamame al 11-2345-6789')).toBe(true)
    })

    test('should return true for emails', () => {
      expect(containsContactInfo('escribir a test@example.com')).toBe(true)
    })

    test('should return true for social accounts', () => {
      expect(containsContactInfo('instagram @perritos_perdidos')).toBe(true)
    })

    test('should return false for descriptions without contact details', () => {
      expect(containsContactInfo('Un hermoso caniche blanco jugando solo en la plaza de la esquina')).toBe(false)
    })
  })

  // Test sanitizeText function
  describe('sanitizeText()', () => {
    test('should strip script tags and basic HTML tags', () => {
      // Mock global document if running in standard node env during simple unit testing
      if (typeof global.document === 'undefined') {
        global.document = {
          createElement: () => ({
            set innerHTML(val) { this.value = val },
            value: ''
          })
        }
      }
      
      const rawText = '<p>Buscamos a <b>Firulais</b></p><script>alert("hack")</script>'
      const sanitized = sanitizeText(rawText)
      
      expect(sanitized).not.toContain('<script>')
      expect(sanitized).not.toContain('<p>')
    })
  })
})
