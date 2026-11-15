// Dirección base donde se encuentra nuestro backend desarrollado con FastAPI.
const API_URL = 'http://127.0.0.1:8000'

// Nombres visibles de los campos que FastAPI puede rechazar.
const nombresCampo: Record<string, string> = {
  equipo_id: 'Equipo',
  tecnico_id: 'Técnico',
  tipo_mantenimiento: 'Tipo de mantenimiento',
  problema_detectado: 'Problema detectado',
  solucion_aplicada: 'Solución aplicada',
  tiempo_empleado_min: 'Tiempo empleado',
  observaciones: 'Observaciones',
  nombre: 'Nombre',
  nombre_host: 'Nombre del servidor',
  direccion_ip: 'Dirección IP',
  sistema_operativo: 'Sistema operativo',
  estado_actual: 'Estado',
  sucursal_id: 'Sucursal',
  servidor_id: 'Servidor',
  modulo: 'Módulo',
  accion: 'Acción',
  descripcion: 'Descripción',
}

interface ErrorValidacion {
  loc?: Array<string | number>
  msg?: string
}

// Traduce los mensajes habituales de validación de FastAPI.
function traducirMensaje(mensaje: string): string {
  const texto = mensaje.trim()

  if (/field required/i.test(texto)) {
    return 'Este campo es obligatorio.'
  }

  if (/greater than 0/i.test(texto)) {
    return 'Debe ser mayor que cero.'
  }

  if (/greater than or equal to 0/i.test(texto)) {
    return 'No puede ser un valor negativo.'
  }

  if (/valid integer/i.test(texto)) {
    return 'Debe ser un número entero.'
  }

  return texto
}

// Convierte un error individual de la lista `detail` en una frase.
function describirElemento(elemento: unknown): string {
  if (typeof elemento === 'string') {
    return elemento.trim()
  }

  if (!elemento || typeof elemento !== 'object') {
    return ''
  }

  const error = elemento as ErrorValidacion
  const mensaje = traducirMensaje(error.msg ?? 'El dato enviado no es válido.')
  const campo = (error.loc ?? [])
    .filter((parte) => parte !== 'body' && parte !== 'query' && parte !== 'path')
    .map((parte) => nombresCampo[String(parte)] ?? String(parte))
    .join('.')

  return campo ? `${campo}: ${mensaje}` : mensaje
}

// Lee `detail` cuando viene como texto o como lista de errores 422.
function describirDetalle(detalle: unknown): string {
  if (typeof detalle === 'string') {
    return detalle.trim()
  }

  if (Array.isArray(detalle)) {
    return detalle
      .map((elemento) => describirElemento(elemento))
      .filter((texto) => texto !== '')
      .join(' ')
  }

  return describirElemento(detalle)
}

// Obtiene un mensaje legible a partir de una respuesta fallida.
async function leerMensajeError(
  respuesta: Response,
  accion: string,
): Promise<string> {
  const cuerpo = await respuesta.json().catch(() => null)
  const detalle =
    cuerpo && typeof cuerpo === 'object' && 'detail' in cuerpo
      ? (cuerpo as { detail: unknown }).detail
      : null
  const texto = describirDetalle(detalle)

  if (texto) {
    return texto
  }

  return `No se pudo ${accion}. El servidor respondió con el código ${respuesta.status}.`
}

// Función para realizar peticiones GET al backend.
// Se utiliza para consultar información del sistema.
export async function obtenerDatos<T>(endpoint: string): Promise<T> {
  const respuesta = await fetch(`${API_URL}${endpoint}`)

  if (!respuesta.ok) {
    throw new Error(await leerMensajeError(respuesta, 'consultar la información'))
  }

  return await respuesta.json() as T
}

// Función para enviar información al backend mediante POST.
export async function enviarDatos<T, R>(
  endpoint: string,
  datos: T,
): Promise<R> {
  const respuesta = await fetch(`${API_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(datos),
  })

  if (!respuesta.ok) {
    throw new Error(await leerMensajeError(respuesta, 'enviar la información'))
  }

  return await respuesta.json() as R
}

// Función para actualizar información mediante PUT.
export async function actualizarDatos<T, R>(
  endpoint: string,
  datos: T,
): Promise<R> {
  const respuesta = await fetch(`${API_URL}${endpoint}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(datos),
  })

  if (!respuesta.ok) {
    throw new Error(await leerMensajeError(respuesta, 'actualizar la información'))
  }

  return await respuesta.json() as R
}

// Función para eliminar información mediante DELETE.
export async function eliminarDatos<R>(endpoint: string): Promise<R> {
  const respuesta = await fetch(`${API_URL}${endpoint}`, {
    method: 'DELETE',
  })

  if (!respuesta.ok) {
    throw new Error(await leerMensajeError(respuesta, 'eliminar la información'))
  }

  return await respuesta.json() as R
}
