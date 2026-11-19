import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select } from '@/components/ui/select'
import { Camera, MapPin, Loader2, X, AlertTriangle } from 'lucide-react'
import { useContentValidation } from '@/hooks/useContentValidation'
import { validateText, sanitizeText } from '@/utils/validateText'
import { API_URL, GEOREF_API_URL, NOMINATIM_API_URL } from '@/config/api'

export default function NewPost() {
  const navigate = useNavigate()
  const fileInputRef = useRef(null)
  const { validateImages, loading: validatingContent } = useContentValidation()

  // Provincias state (cargado desde JSON)
  const [provincias, setProvincias] = useState([])
  const [loadingProvincias, setLoadingProvincias] = useState(true)

  // Form state
  const [formData, setFormData] = useState({
    images: [],  // Array de File objects
    animalType: 'dog',
    sex: 'unknown',
    size: 'medium',
    sightingDate: new Date().toISOString().split('T')[0],
    description: '',
    contactMethod: '',
  })

  // Location state
  const [location, setLocation] = useState(null) // { latitude, longitude, name }
  const [loadingLocation, setLoadingLocation] = useState(false)
  const [locationMode, setLocationMode] = useState(null) // 'gps' | 'manual'
  const [manualAddress, setManualAddress] = useState({
    street: '',
    number: '',
    city: '',
    state: '', // Se setea cuando se cargan las provincias
  })
  const [citySuggestions, setCitySuggestions] = useState([])
  const [showCitySuggestions, setShowCitySuggestions] = useState(false)
  const [citySearchTerm, setCitySearchTerm] = useState('')
  const [loadingCities, setLoadingCities] = useState(false)

  // UI state
  const [imagePreviews, setImagePreviews] = useState([])  // Array de preview URLs
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const errorRef = useRef(null)
  const [analyzingImage, setAnalyzingImage] = useState(false)
  const [ocrError, setOcrError] = useState(null) // New state for OCR specific errors

  // Constants
  const MAX_IMAGES = 3

  // Estado para detectar cambios sin guardar
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  // Detectar cuando hay cambios en el formulario
  useEffect(() => {
    const hasChanges =
      formData.images.length > 0 ||
      formData.description.trim() !== '' ||
      location !== null ||
      formData.contactMethod.trim() !== ''

    setHasUnsavedChanges(hasChanges)
  }, [formData.images.length, formData.description, location, formData.contactMethod])

  // Advertir al cerrar ventana/tab si hay cambios sin guardar
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (hasUnsavedChanges) {
        e.preventDefault()
        e.returnValue = ''
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
    }
  }, [hasUnsavedChanges])

  // Debug: Log error state changes
  useEffect(() => {
    if (error && errorRef.current) {
      errorRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, [error])

  // Cargar provincias desde JSON al montar el componente
  useEffect(() => {
    fetch('/data/provincias.json')
      .then(res => res.json())
      .then(data => {
        const provs = (data.provincias || []).sort((a, b) => a.nombre.localeCompare(b.nombre))
        setProvincias(provs)
        // Setear Buenos Aires por defecto si existe
        const buenosAires = provs.find(p => p.nombre === 'Buenos Aires')
        if (buenosAires && !manualAddress.state) {
          setManualAddress(prev => ({ ...prev, state: buenosAires.nombre }))
        }
        setLoadingProvincias(false)
      })
      .catch(err => {
        console.error('[Provincias] Error cargando JSON:', err)
        setLoadingProvincias(false)
      })
  }, [])

  // Handle image selection
  const handleImageChange = (e) => {
    const files = Array.from(e.target.files || [])

    if (files.length === 0) return

    // Validar que no exceda el máximo
    if (formData.images.length + files.length > MAX_IMAGES) {
      setError(`Máximo ${MAX_IMAGES} imágenes permitidas`)
      return
    }

    // Validar cada archivo
    const validFiles = []
    for (const file of files) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError(`${file.name} no es una imagen válida`)
        continue
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError(`${file.name} supera los 10MB`)
        continue
      }

      validFiles.push(file)
    }

    if (validFiles.length === 0) return

    // Agregar archivos válidos
    setFormData({ ...formData, images: [...formData.images, ...validFiles] })

    // Create previews
    validFiles.forEach((file) => {
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreviews((prev) => [...prev, reader.result])
      }
      reader.readAsDataURL(file)
    })

    setError(null)

    // Reset input para permitir seleccionar el mismo archivo de nuevo
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }

    // Analizar la primera imagen automáticamente con IA si no hay imágenes previas
    if (formData.images.length === 0 && validFiles.length > 0) {
      analyzeFirstImage(validFiles[0])
    }
  }

  const analyzeFirstImage = async (file) => {
    setAnalyzingImage(true)
    setError(null)
    try {
      const form = new FormData()
      form.append('image', file)

      const response = await fetch(`${API_URL}/api/v1/posts/analyze-image`, {
        method: 'POST',
        body: form,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "No se pudo analizar la imagen de manera automática.")
      }

      const result = await response.json()

      // Set OCR error if present, otherwise clear it
      if (result.error) {
        setOcrError(result.error)
        // Do NOT auto-fill description if there's an OCR error
        setFormData(prev => ({
          ...prev,
          animalType: result.animal_type || prev.animalType,
          sex: result.sex || prev.sex,
          size: result.size || prev.size,
          contactMethod: result.contact_method || prev.contactMethod,
          sightingDate: result.sighting_date || prev.sightingDate,
          // description is intentionally NOT updated here if there's an error
        }))
      } else {
        setOcrError(null)
        // Map response to Frontend form fields, including description
        setFormData(prev => {
          const parts = [];
          if (result.extracted_text) parts.push(result.extracted_text);
          if (result.image_interpretation) parts.push(result.image_interpretation);
          const combinedDescription = parts.join('\n\n');
          
          return {
            ...prev,
            animalType: result.animal_type || prev.animalType,
            sex: result.sex || prev.sex,
            size: result.size || prev.size,
            contactMethod: result.contact_method || prev.contactMethod,
            sightingDate: result.sighting_date || prev.sightingDate,
            description: combinedDescription || prev.description,
          };
        })

        // If location name is found, pre-fill manual location
        if (result.location_name) {
          setManualAddress(prev => ({
            ...prev,
            street: result.location_name
          }))
          setLocationMode("manual")
        }
      }
    } catch (err) {
      console.error("Error in OCR/Analysis:", err)
      setOcrError(err.message || "Error desconocido al analizar la imagen.")
      // Ensure description is not filled with error messages
      setFormData(prev => ({ ...prev, description: prev.description }))
    } finally {
      setAnalyzingImage(false)
    }
  }

  // Remove specific image
  const removeImage = (index) => {
    setFormData({
      ...formData,
      images: formData.images.filter((_, i) => i !== index),
    })
    setImagePreviews(imagePreviews.filter((_, i) => i !== index))
  }

  // Load cities for the selected province from local Georef data
  useEffect(() => {
    const { state } = manualAddress

    if (!state) {
      setCitySuggestions([])
      return
    }

    setLoadingCities(true)

    // Cargar localidades desde JSON local completo de Argentina
    fetch('/data/localidades.json')
      .then(res => res.json())
      .then(data => {
        let localidades = []

        // Soportar dos estructuras:
        // 1. Agrupado por provincia: { "Buenos Aires": [...], "Córdoba": [...] }
        // 2. Array plano: { "localidades": [...] } donde cada item tiene "provincia"

        if (data[state]) {
          // Estructura agrupada por provincia
          localidades = data[state]
        } else if (data.localidades) {
          // Estructura plana, filtrar por provincia
          localidades = data.localidades.filter(loc =>
            loc.provincia && loc.provincia.nombre === state
          )
        }

        // Ordenar alfabéticamente
        localidades.sort((a, b) => a.nombre.localeCompare(b.nombre))
        setCitySuggestions(localidades)
        setLoadingCities(false)
      })
      .catch(err => {
        console.error('[Localidades] Error cargando JSON local:', err)
        console.error('[Localidades] Intentar con API Georef como fallback')
        setCitySuggestions([])
        setLoadingCities(false)
      })
  }, [manualAddress.state])

  // Filter cities based on search term
  const filteredCities = citySearchTerm.length === 0
    ? citySuggestions.slice(0, 20) // Show first 20 when no search
    : citySuggestions
        .filter(loc =>
          loc.nombre.toLowerCase().includes(citySearchTerm.toLowerCase())
        )
        .slice(0, 20) // Max 20 results

  // Get user location
  const getLocation = () => {
    if (!navigator.geolocation) {
      setError('Tu navegador no soporta geolocalización')
      setLocationMode('manual')
      return
    }

    setLoadingLocation(true)
    setError(null)

    const handleSuccess = async (position) => {
      const { latitude, longitude } = position.coords

      // Reverse geocoding with Nominatim (OpenStreetMap)
      try {
        const response = await fetch(
          `${NOMINATIM_API_URL}/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=18&addressdetails=1`,
          {
            headers: {
              'Accept-Language': 'es-AR,es',
            },
          }
        )

        const data = await response.json()

        // Build location name
        const address = data.address || {}
        const parts = []

        if (address.road) parts.push(address.road)
        if (address.neighbourhood || address.suburb) {
          parts.push(address.neighbourhood || address.suburb)
        }
        if (address.city || address.town) {
          parts.push(address.city || address.town)
        }

        const locationName = parts.join(', ') || data.display_name

        setLocation({
          latitude,
          longitude,
          name: locationName,
        })
        setLocationMode('gps')
      } catch (err) {
        console.error('Error reverse geocoding:', err)
        // Use coordinates even if reverse geocoding fails
        setLocation({
          latitude,
          longitude,
          name: `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`,
        })
        setLocationMode('gps')
      }

      setLoadingLocation(false)
    }

    // First attempt with high accuracy
    navigator.geolocation.getCurrentPosition(
      handleSuccess,
      (error) => {
        console.warn('First geolocation attempt failed (code:', error.code, '):', error.message)
        
        // If timeout (code 3) or position unavailable (code 2), retry with low accuracy
        if (error.code === 3 || error.code === 2) {
          console.log('Retrying geolocation with enableHighAccuracy: false...')
          navigator.geolocation.getCurrentPosition(
            handleSuccess,
            (fallbackError) => {
              console.error('Fallback geolocation failed:', fallbackError)
              setError('No se pudo obtener la ubicación automáticamente. Por favor, ingrésala manualmente.')
              setLoadingLocation(false)
              setLocationMode('manual')
            },
            {
              enableHighAccuracy: false,
              timeout: 15000,
              maximumAge: 60000,
            }
          )
        } else {
          // Permission denied or other error, fallback to manual mode directly
          setLoadingLocation(false)
          setLocationMode('manual')
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    )
  }

  // Geocode manual address using API Georef
  const geocodeManualAddress = async () => {
    const { street, number, city, state } = manualAddress

    // Validate all required fields
    if (!street || !number || !city || !state) {
      setError('Debes completar todos los campos: Calle, Altura, Localidad y Provincia')
      return
    }

    setLoadingLocation(true)
    setError(null)

    try {
      // Usar API Georef para geocoding preciso
      const direccion = `${street} ${number}`
      const url = `${GEOREF_API_URL}/direcciones?direccion=${encodeURIComponent(direccion)}&localidad=${encodeURIComponent(city)}&provincia=${encodeURIComponent(state)}&max=1`

      const response = await fetch(url)

      if (!response.ok) {
        console.error('[Georef] HTTP Error:', response.status)
        const errorMsg = `Error de conexión (${response.status}). Intentá de nuevo.`
        setError(errorMsg)
        setLoadingLocation(false)
        return
      }

      const data = await response.json()

      if (data.direcciones && data.direcciones.length > 0) {
        const result = data.direcciones[0]
        const ubicacion = result.ubicacion

        // Construir nombre de ubicación con datos normalizados de Georef
        const calleNormalizada = result.calle?.nombre || street
        const alturaNormalizada = result.altura?.valor || number
        const locationName = `${calleNormalizada} ${alturaNormalizada}, ${city}, ${state}`

        setLocation({
          latitude: parseFloat(ubicacion.lat),
          longitude: parseFloat(ubicacion.lon),
          name: locationName,
        })
        setLocationMode('manual')
      } else {
        const errorMsg = 'No se pudo encontrar la dirección exacta. Verifica que la calle, altura y localidad sean correctos.'
        setError(errorMsg)
      }
    } catch (err) {
      console.error('[Georef] Caught exception:', err)
      const errorMsg = 'Error al buscar la dirección. Verifica tu conexión.'
      setError(errorMsg)
    } finally {
      setLoadingLocation(false)
    }
  }

  // Handle form submit
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    // Validation
    if (formData.images.length === 0) {
      setError('Debes seleccionar al menos una imagen')
      return
    }

    if (!location) {
      setError('Debes obtener tu ubicación')
      return
    }
    setLoading(true)

    try {
      // 1. Validar texto
      const textValidation = validateText(formData.description)
      if (!textValidation.valid) {
        setError(textValidation.errors.join('. '))
        setLoading(false)
        return
      }

      // 2. Validar imágenes con IA
      const imageValidation = await validateImages(formData.images)

      if (!imageValidation.safe) {
        // Imagen rechazada por contenido inapropiado (NSFW)
        setError(imageValidation.reason)
        setLoading(false)
        return
      }

      // Solo requiere aprobación si la validación tiene baja confianza
      let pendingApproval = false
      if (imageValidation.confidence && imageValidation.confidence < 0.8) {
        pendingApproval = true
      } else {
      }
      // Create FormData
      const formDataToSend = new FormData()
      // Agregar todas las imágenes con el mismo campo "images"
      formData.images.forEach((image) => {
        formDataToSend.append('images', image)
      })
      formDataToSend.append('latitude', location.latitude)
      formDataToSend.append('longitude', location.longitude)
      formDataToSend.append('size', formData.size)
      formDataToSend.append('animal_type', formData.animalType)
      formDataToSend.append('sex', formData.sex)
      formDataToSend.append('sighting_date', formData.sightingDate)

      // Agregar pending_approval si es necesario
      if (pendingApproval) {
        formDataToSend.append('pending_approval', 'true')
      }

      if (formData.description) {
        // Sanitizar texto antes de enviar
        const sanitized = sanitizeText(formData.description)
        formDataToSend.append('description', sanitized)
      }

      if (location.name) {
        formDataToSend.append('location_name', location.name)
      }

      if (formData.contactMethod) {
        formDataToSend.append('contact_method', formData.contactMethod)
      }

      // Submit to API
      const response = await fetch(`${API_URL}/api/v1/posts`, {
        method: 'POST',
        body: formDataToSend,
      })

      if (!response.ok) {
        const errorData = await response.json()
        console.error('❌ [FRONTEND] Error response:', errorData)
        throw new Error(errorData.detail || 'Error al crear la publicación')
      }

      const result = await response.json()

      // Si está pendiente de aprobación, mostrar mensaje diferente
      if (pendingApproval) {
        alert('Tu publicación está en revisión y será visible pronto. Gracias por tu paciencia.')
      }

      // Limpiar flag de cambios sin guardar antes de navegar
      setHasUnsavedChanges(false)

      // Redirect to home
      navigate('/')
    } catch (err) {
      console.error('❌ [FRONTEND] Error creating post:', err)
      setError(err.message || 'Error al crear la publicación')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-6 max-w-2xl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">Nuevo avistamiento</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Reporta una mascota que viste en la calle
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Image Upload - Multiple Images */}
        <div>
          <Label htmlFor="images" className="text-base">
            Fotos <span className="text-red-500">*</span>
            <span className="text-sm text-muted-foreground ml-2">
              ({formData.images.length}/{MAX_IMAGES})
            </span>
          </Label>

          <div className="mt-2 space-y-3">
            {/* Grid de previews */}
            {imagePreviews.length > 0 && (
              <div className="grid grid-cols-2 gap-3">
                {imagePreviews.map((preview, index) => (
                  <div key={index} className="relative aspect-square">
                    <img
                      src={preview}
                      alt={`Preview ${index + 1}`}
                      className="w-full h-full rounded-lg object-cover bg-muted"
                    />
                    <Button
                      type="button"
                      variant="destructive"
                      size="icon"
                      className="absolute top-2 right-2 h-8 w-8"
                      onClick={() => removeImage(index)}
                    >
                      <X size={16} />
                    </Button>
                    {index === 0 && (
                      <div className="absolute bottom-2 left-2 bg-blue-500 text-white text-xs px-2 py-1 rounded">
                        Principal
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Botón para agregar más imágenes */}
            {formData.images.length < MAX_IMAGES && (
              <div>
                <input
                  ref={fileInputRef}
                  type="file"
                  id="images"
                  accept="image/*"
                  multiple
                  onChange={handleImageChange}
                  className="hidden"
                />
                <Button
                  type="button"
                  variant="outline"
                  className={`w-full border-2 border-dashed ${
                    formData.images.length === 0 ? 'h-40' : 'h-20'
                  }`}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <div className="flex flex-col items-center gap-2">
                    <Camera size={formData.images.length === 0 ? 32 : 24} className="text-muted-foreground" />
                    <span className="text-sm">
                      {formData.images.length === 0
                        ? 'Tomar foto o elegir de galería'
                        : `Agregar otra foto (máx. ${MAX_IMAGES})`}
                    </span>
                  </div>
                </Button>
              </div>
            )}
          </div>
        </div>

        {analyzingImage && (
          <div className="flex items-center gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg animate-pulse">
            <Loader2 className="h-5 w-5 text-blue-500 animate-spin flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-blue-950">Analizando imagen con IA</p>
              <p className="text-xs text-blue-700">
                Extrayendo texto y autocompletando el formulario en español de forma automática...
              </p>
            </div>
          </div>
        )}

        {/* Debug UI for OCR errors (development only) */}
        {ocrError && import.meta.env.DEV && (
          <div className="mt-2 p-3 text-sm text-red-700 bg-red-50 border border-red-200 rounded-md">
            <strong className="font-semibold">Error en Análisis de Imagen (DEBUG):</strong>
            <p className="mt-1 text-xs whitespace-pre-wrap">{
              // Truncate long errors for readability
              ocrError.length > 500 ? ocrError.substring(0, 500) + 
              "\n... (error truncado, ver consola para más detalles)" : ocrError
            }</p>
          </div>
        )}

        {/* Location */}
        <div>
          <Label className="text-base">
            Ubicación <span className="text-red-500">*</span>
          </Label>
          <div className="mt-2 space-y-3">
            {!locationMode && !location && (
              <div className="space-y-2">
                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  onClick={getLocation}
                  disabled={loadingLocation}
                >
                  {loadingLocation ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Obteniendo ubicación...
                    </>
                  ) : (
                    <>
                      <MapPin className="mr-2 h-4 w-4" />
                      Usar mi ubicación actual
                    </>
                  )}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  className="w-full"
                  onClick={() => setLocationMode('manual')}
                >
                  Ingresar dirección manualmente
                </Button>
              </div>
            )}

            {locationMode === 'manual' && !location && (
              <div className="space-y-3 p-4 bg-muted rounded-lg border">
                <p className="text-sm text-muted-foreground">Ingresa la dirección del avistamiento</p>
                <div className="grid grid-cols-2 gap-3">
                  <div className="col-span-2 sm:col-span-1">
                    <Label htmlFor="street" className="text-sm">Calle *</Label>
                    <Input
                      id="street"
                      value={manualAddress.street}
                      onChange={(e) => setManualAddress({ ...manualAddress, street: e.target.value })}
                      placeholder="Av. Santa Fe"
                      className="mt-1"
                    />
                  </div>
                  <div className="col-span-2 sm:col-span-1">
                    <Label htmlFor="number" className="text-sm">Altura aproximada *</Label>
                    <Input
                      id="number"
                      type="text"
                      inputMode="numeric"
                      pattern="[0-9]*"
                      value={manualAddress.number}
                      onChange={(e) => {
                        const value = e.target.value.replace(/[^0-9]/g, '')
                        setManualAddress({ ...manualAddress, number: value })
                      }}
                      placeholder="1234"
                      className="mt-1"
                    />
                  </div>
                  <div className="col-span-2 sm:col-span-1">
                    <Label htmlFor="city" className="text-sm">Localidad *</Label>
                    <div className="relative mt-1">
                      <button
                        type="button"
                        onClick={() => setShowCitySuggestions(!showCitySuggestions)}
                        className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        <span className={manualAddress.city ? 'text-foreground' : 'text-muted-foreground'}>
                          {manualAddress.city || 'Seleccionar localidad...'}
                        </span>
                        <svg
                          className="h-4 w-4 opacity-50"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>

                      {showCitySuggestions && (
                        <div className="absolute z-10 w-full mt-1 bg-card border border-border rounded-md shadow-lg">
                          {/* Search input inside dropdown */}
                          <div className="p-2 border-b border-border">
                            <Input
                              placeholder="Buscar localidad..."
                              value={citySearchTerm}
                              onChange={(e) => setCitySearchTerm(e.target.value)}
                              autoFocus
                              className="h-8"
                            />
                          </div>

                          {/* Cities list */}
                          <div className="max-h-60 overflow-y-auto">
                            {loadingCities ? (
                              <div className="px-3 py-4 text-sm text-center text-muted-foreground">
                                Cargando localidades...
                              </div>
                            ) : filteredCities.length > 0 ? (
                              filteredCities.map((loc, index) => (
                                <button
                                  key={loc.id || index}
                                  type="button"
                                  className={`w-full text-left px-3 py-2 hover:bg-muted text-sm ${
                                    manualAddress.city === loc.nombre ? 'bg-primary/10 font-medium' : ''
                                  }`}
                                  onClick={() => {
                                    setManualAddress({ ...manualAddress, city: loc.nombre })
                                    setCitySearchTerm('')
                                    setShowCitySuggestions(false)
                                  }}
                                >
                                  <div className="font-medium">{loc.nombre}</div>
                                  {loc.departamento && loc.departamento.nombre && loc.departamento.nombre !== loc.nombre && (
                                    <div className="text-xs text-muted-foreground">
                                      Partido de {loc.departamento.nombre}
                                    </div>
                                  )}
                                </button>
                              ))
                            ) : (
                              <div className="px-3 py-4 text-sm text-center text-muted-foreground">
                                {citySearchTerm ? 'No se encontraron localidades' : 'No hay localidades disponibles'}
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Click outside to close */}
                      {showCitySuggestions && (
                        <div
                          className="fixed inset-0 z-0"
                          onClick={() => {
                            setShowCitySuggestions(false)
                            setCitySearchTerm('')
                          }}
                        />
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {manualAddress.city ? (
                        <span className="text-green-600">✓ Seleccionado: {manualAddress.city}</span>
                      ) : (
                        'Click para abrir el desplegable'
                      )}
                    </p>
                  </div>
                  <div className="col-span-2 sm:col-span-1">
                    <Label htmlFor="state" className="text-sm">Provincia *</Label>
                    <Select
                      id="state"
                      value={manualAddress.state}
                      onChange={(e) => setManualAddress({ ...manualAddress, state: e.target.value })}
                      className="mt-1"
                      disabled={loadingProvincias}
                    >
                      {loadingProvincias ? (
                        <option>Cargando provincias...</option>
                      ) : (
                        <>
                          <option value="">Seleccionar provincia</option>
                          {provincias.map((prov) => (
                            <option key={prov.id} value={prov.nombre}>
                              {prov.nombre}
                            </option>
                          ))}
                        </>
                      )}
                    </Select>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    className="flex-1"
                    onClick={() => {
                      setLocationMode(null)
                      setManualAddress({ street: '', number: '', city: '', state: 'Buenos Aires' })
                      setCitySearchTerm('')
                      setShowCitySuggestions(false)
                    }}
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="button"
                    className="flex-1"
                    onClick={geocodeManualAddress}
                    disabled={
                      loadingLocation ||
                      !manualAddress.street ||
                      !manualAddress.number ||
                      !manualAddress.city ||
                      !manualAddress.state
                    }
                  >
                    {loadingLocation ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Buscando...
                      </>
                    ) : (
                      'Confirmar ubicación'
                    )}
                  </Button>
                </div>
              </div>
            )}

            {location && (
              <div className="flex items-start gap-2 p-3 bg-green-50 border border-green-200 rounded-md">
                <MapPin className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-green-900">
                    Ubicación obtenida
                  </p>
                  <p className="text-sm text-green-700 break-words">
                    {location.name}
                  </p>
                  <Button
                    type="button"
                    variant="link"
                    className="h-auto p-0 text-xs text-green-600"
                    onClick={() => {
                      setLocation(null)
                      setLocationMode(null)
                      setManualAddress({ street: '', number: '', city: '', state: 'Buenos Aires' })
                      setCitySearchTerm('')
                      setShowCitySuggestions(false)
                    }}
                  >
                    Cambiar ubicación
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Animal Type */}
        <div>
          <Label className="text-base">Tipo de animal</Label>
          <div className="mt-2 grid grid-cols-3 gap-2">
            {[
              { value: 'dog', label: '🐕 Perro' },
              { value: 'cat', label: '🐈 Gato' },
              { value: 'other', label: 'Otro' },
            ].map((option) => (
              <Button
                key={option.value}
                type="button"
                variant={formData.animalType === option.value ? 'default' : 'outline'}
                onClick={() => setFormData({ ...formData, animalType: option.value })}
              >
                {option.label}
              </Button>
            ))}
          </div>
        </div>

        {/* Sex */}
        <div>
          <Label className="text-base">Sexo</Label>
          <div className="mt-2 grid grid-cols-3 gap-2">
            {[
              { value: 'male', label: '♂ Macho' },
              { value: 'female', label: '♀ Hembra' },
              { value: 'unknown', label: 'No sé' },
            ].map((option) => (
              <Button
                key={option.value}
                type="button"
                variant={formData.sex === option.value ? 'default' : 'outline'}
                onClick={() => setFormData({ ...formData, sex: option.value })}
              >
                {option.label}
              </Button>
            ))}
          </div>
        </div>

        {/* Size */}
        <div>
          <Label className="text-base">
            Tamaño <span className="text-red-500">*</span>
          </Label>
          <div className="mt-2 grid grid-cols-3 gap-2">
            {[
              { value: 'small', label: 'Chico' },
              { value: 'medium', label: 'Mediano' },
              { value: 'large', label: 'Grande' },
            ].map((option) => (
              <Button
                key={option.value}
                type="button"
                variant={formData.size === option.value ? 'default' : 'outline'}
                onClick={() => setFormData({ ...formData, size: option.value })}
              >
                {option.label}
              </Button>
            ))}
          </div>
        </div>

        {/* Sighting Date */}
        <div>
          <Label htmlFor="sightingDate" className="text-base">
            Fecha del avistamiento
          </Label>
          <Input
            type="date"
            id="sightingDate"
            value={formData.sightingDate}
            max={new Date().toISOString().split('T')[0]}
            onChange={(e) =>
              setFormData({ ...formData, sightingDate: e.target.value })
            }
            className="mt-2"
          />
        </div>

        {/* Description */}
        <div>
          <Label htmlFor="description" className="text-base">
            Descripción
          </Label>
          <Textarea
            id="description"
            placeholder="Ej: Perro marrón con collar rojo, parecía asustado..."
            value={formData.description}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
            maxLength={1000}
            className="mt-2"
            rows={4}
          />
          <p className="text-xs text-muted-foreground mt-1">
            {formData.description.length}/1000 caracteres
          </p>
        </div>

        {/* Contact */}
        <div>
          <Label htmlFor="contact" className="text-base">
            Contacto (opcional)
          </Label>
          <Input
            type="text"
            id="contact"
            placeholder="Email, teléfono o Instagram"
            value={formData.contactMethod}
            onChange={(e) =>
              setFormData({ ...formData, contactMethod: e.target.value })
            }
            className="mt-2"
          />
          <p className="text-xs text-muted-foreground mt-1">
            No compartimos tu información personal
          </p>
        </div>

        {/* Error message */}
        {error && (
          <div
            ref={errorRef}
            className="bg-red-50 border border-red-200 rounded-md p-3"
          >
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Submit buttons */}
        <div className="flex gap-3 pt-4">
          <Button
            type="button"
            variant="outline"
            className="flex-1"
            onClick={() => navigate('/')}
            disabled={loading}
          >
            Cancelar
          </Button>
          <Button type="submit" className="flex-1" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Publicando...
              </>
            ) : (
              'Publicar'
            )}
          </Button>
        </div>
      </form>
    </div>
  )
}
