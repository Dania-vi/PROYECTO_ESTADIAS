
<script setup lang="ts">
// Importamos las funciones necesarias de Vue.
import { ref, computed, onMounted } from 'vue'

// Importamos las funciones para consultar y enviar información al backend.
import { obtenerDatos, enviarDatos } from '../services/api'

// Estructura de un respaldo recibido desde el backend.
interface Respaldo {
  id: number
  equipo_id: number
  servidor_id: number | null
  fecha_hora: string
  tipo_respaldo: string | null
  tamanio_mb: number | null
  resultado: string | null
  dispositivo_externo: string | null
  ruta_destino: string | null
  detalles_error: string | null
}

// Estructura básica de los equipos registrados.
interface Equipo {
  id: number
  nombre?: string
  nombre_equipo?: string
}

// Estructura básica de los servidores registrados.
interface Servidor {
  id: number
  nombre?: string
  nombre_host?: string
}

// Información necesaria para registrar un respaldo.
interface RespaldoFormulario {
  equipo_id: string
  servidor_id: string
  tipo_respaldo: string
  tamanio_mb: string
  resultado: string
  dispositivo_externo: string
  ruta_destino: string
  detalles_error: string
}

// Listas principales del módulo.
const respaldos = ref<Respaldo[]>([])
const equipos = ref<Equipo[]>([])
const servidores = ref<Servidor[]>([])

// Estados de carga y mensajes.
const cargando = ref(false)
const guardando = ref(false)
const mostrarFormulario = ref(false)
const mensajeExito = ref('')
const mensajeError = ref('')

// Texto de búsqueda y filtro por resultado.
const busqueda = ref('')
const filtroResultado = ref('Todos')

// Datos iniciales del formulario.
const formulario = ref<RespaldoFormulario>({
  equipo_id: '',
  servidor_id: '',
  tipo_respaldo: 'Completo',
  tamanio_mb: '',
  resultado: 'Exitoso',
  dispositivo_externo: '',
  ruta_destino: '',
  detalles_error: '',
})

// Consulta los respaldos, equipos y servidores registrados.
async function cargarInformacion() {
  cargando.value = true
  mensajeError.value = ''

  try {
    const [datosRespaldos, datosEquipos, datosServidores] =
      await Promise.all([
        obtenerDatos<Respaldo[]>('/api/respaldos/'),
        obtenerDatos<Equipo[]>('/api/equipos/'),
        obtenerDatos<Servidor[]>('/api/servidores/'),
      ])

    respaldos.value = datosRespaldos
    equipos.value = datosEquipos
    servidores.value = datosServidores

  } catch (error) {
    mensajeError.value =
      error instanceof Error
        ? error.message
        : 'No se pudo cargar la información de respaldos.'

  } finally {
    cargando.value = false
  }
}

// Calculamos el total de respaldos registrados.
const totalRespaldos = computed(() => respaldos.value.length)

// Contamos los respaldos exitosos.
const respaldosExitosos = computed(() =>
  respaldos.value.filter(
    (respaldo) => respaldo.resultado?.toLowerCase() === 'exitoso',
  ).length,
)

// Contamos los respaldos fallidos.
const respaldosFallidos = computed(() =>
  respaldos.value.filter(
    (respaldo) => respaldo.resultado?.toLowerCase() === 'fallido',
  ).length,
)

// Obtenemos el respaldo más reciente.
const ultimoRespaldo = computed(() => {
  if (respaldos.value.length === 0) return null

  return [...respaldos.value].sort(
    (a, b) =>
      new Date(b.fecha_hora).getTime() -
      new Date(a.fecha_hora).getTime(),
  )[0]
})

// Filtramos los respaldos según el texto y el resultado seleccionado.
const respaldosFiltrados = computed(() => {
  return respaldos.value.filter((respaldo) => {
    const equipo = obtenerNombreEquipo(respaldo.equipo_id)
    const servidor = obtenerNombreServidor(respaldo.servidor_id)

    const texto = busqueda.value.toLowerCase()

    const coincideBusqueda =
      equipo.toLowerCase().includes(texto) ||
      servidor.toLowerCase().includes(texto) ||
      (respaldo.tipo_respaldo ?? '').toLowerCase().includes(texto) ||
      (respaldo.dispositivo_externo ?? '').toLowerCase().includes(texto)

    const coincideResultado =
      filtroResultado.value === 'Todos' ||
      respaldo.resultado?.toLowerCase() ===
        filtroResultado.value.toLowerCase()

    return coincideBusqueda && coincideResultado
  })
})

// Buscamos el nombre del equipo a partir de su identificador.
function obtenerNombreEquipo(id: number): string {
  const equipo = equipos.value.find((item) => item.id === id)

  return equipo?.nombre ?? equipo?.nombre_equipo ?? `Equipo ${id}`
}

// Buscamos el nombre del servidor a partir de su identificador.
function obtenerNombreServidor(id: number | null): string {
  if (id === null) return 'No especificado'

  const servidor = servidores.value.find((item) => item.id === id)

  return servidor?.nombre ?? servidor?.nombre_host ?? `Servidor ${id}`
}

// Damos formato legible a la fecha del respaldo.
function formatearFecha(fecha: string): string {
  if (!fecha) return 'No disponible'

  const valor = new Date(fecha)

  if (Number.isNaN(valor.getTime())) return fecha

  return valor.toLocaleString('es-MX', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Limpiamos el formulario para iniciar un registro nuevo.
function limpiarFormulario() {
  formulario.value = {
    equipo_id: '',
    servidor_id: '',
    tipo_respaldo: 'Completo',
    tamanio_mb: '',
    resultado: 'Exitoso',
    dispositivo_externo: '',
    ruta_destino: '',
    detalles_error: '',
  }
}

// Abrimos el formulario de registro.
function abrirFormulario() {
  limpiarFormulario()
  mensajeError.value = ''
  mensajeExito.value = ''
  mostrarFormulario.value = true
}

// Cerramos el formulario.
function cerrarFormulario() {
  mostrarFormulario.value = false
  limpiarFormulario()
}

// Enviamos el registro de respaldo al backend.
async function guardarRespaldo() {
  mensajeError.value = ''
  mensajeExito.value = ''

  // Validamos que se haya seleccionado un equipo.
  if (!formulario.value.equipo_id) {
    mensajeError.value = 'Debes seleccionar un equipo.'
    return
  }

  // Si el respaldo falló, solicitamos una descripción del error.
  if (
    formulario.value.resultado === 'Fallido' &&
    !formulario.value.detalles_error.trim()
  ) {
    mensajeError.value =
      'Debes indicar los detalles del error del respaldo.'
    return
  }

  // Convertimos los valores del formulario al formato esperado por la API.
  const datos = {
    equipo_id: Number(formulario.value.equipo_id),
    servidor_id: formulario.value.servidor_id
      ? Number(formulario.value.servidor_id)
      : null,
    tipo_respaldo: formulario.value.tipo_respaldo || null,
    // Convertimos el tamaño a texto para validar si el campo está vacío.
    tamanio_mb: String(formulario.value.tamanio_mb ?? '').trim() !== ''
  ? Number(formulario.value.tamanio_mb)
  : null,
    resultado: formulario.value.resultado,
    dispositivo_externo:
      formulario.value.dispositivo_externo.trim() || null,
    ruta_destino: formulario.value.ruta_destino.trim() || null,
    detalles_error: formulario.value.detalles_error.trim() || null,
  }

  // Validamos que el tamaño no sea negativo.
  if (datos.tamanio_mb !== null && (
    !Number.isFinite(datos.tamanio_mb) || datos.tamanio_mb < 0
  )) {
    mensajeError.value = 'El tamaño debe ser un número válido igual o mayor a cero.'
    return
  }

  guardando.value = true

  try {
    // Enviamos el nuevo registro al backend.
    await enviarDatos<typeof datos, Respaldo>(
      '/api/respaldos/',
      datos,
    )

    mensajeExito.value = 'El respaldo se registró correctamente.'

    // Actualizamos la tabla con la información más reciente.
    await cargarInformacion()

    // Cerramos el formulario después de guardar.
    cerrarFormulario()

  } catch (error) {
    mensajeError.value =
      error instanceof Error
        ? error.message
        : 'No se pudo registrar el respaldo.'

  } finally {
    guardando.value = false
  }
}

// Cargamos la información cuando se abre la vista.
onMounted(() => {
  cargarInformacion()
})
</script>

<template>
  <div class="respaldos">

    <!-- Encabezado del módulo -->
    <div class="page-header">
      <div>
        <h1>Respaldos</h1>
        <p>Consulta y registro de operaciones de respaldo.</p>
      </div>

      <div class="header-actions">
        <button class="btn-refresh" @click="cargarInformacion">
          ↻ Actualizar
        </button>

        <button class="btn-primary" @click="abrirFormulario">
          + Registrar respaldo
        </button>
      </div>
    </div>

    <!-- Tarjetas de resumen -->
    <section class="summary-grid">

      <article class="summary-card">
        <span class="summary-icon blue">💾</span>
        <div>
          <p>Total de respaldos</p>
          <h2>{{ totalRespaldos }}</h2>
        </div>
      </article>

      <article class="summary-card">
        <span class="summary-icon green">✓</span>
        <div>
          <p>Respaldos exitosos</p>
          <h2>{{ respaldosExitosos }}</h2>
        </div>
      </article>

      <article class="summary-card">
        <span class="summary-icon red">✕</span>
        <div>
          <p>Respaldos fallidos</p>
          <h2>{{ respaldosFallidos }}</h2>
        </div>
      </article>

      <article class="summary-card">
        <span class="summary-icon purple">🕒</span>
        <div>
          <p>Último respaldo</p>
          <h2 class="last-backup">
            {{
              ultimoRespaldo
                ? formatearFecha(ultimoRespaldo.fecha_hora)
                : 'Sin registros'
            }}
          </h2>
        </div>
      </article>

    </section>

    <!-- Formulario para registrar una operación -->
    <section v-if="mostrarFormulario" class="form-card">

      <div class="section-header">
        <div>
          <h2>Registrar respaldo</h2>
          <p>Ingresa la información de la operación realizada.</p>
        </div>

        <button class="btn-close" @click="cerrarFormulario">
          ✕
        </button>
      </div>

      <form @submit.prevent="guardarRespaldo">

        <div class="form-grid">

          <div class="form-group">
            <label for="equipo">Equipo *</label>
            <select
              id="equipo"
              v-model="formulario.equipo_id"
              required
            >
              <option value="" disabled>Selecciona un equipo</option>
              <option
                v-for="equipo in equipos"
                :key="equipo.id"
                :value="String(equipo.id)"
              >
                {{ equipo.nombre ?? equipo.nombre_equipo ?? `Equipo ${equipo.id}` }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="servidor">Servidor</label>
            <select id="servidor" v-model="formulario.servidor_id">
              <option value="">No especificado</option>
              <option
                v-for="servidor in servidores"
                :key="servidor.id"
                :value="String(servidor.id)"
              >
                {{ servidor.nombre ?? servidor.nombre_host ?? `Servidor ${servidor.id}` }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="tipo">Tipo de respaldo</label>
            <select id="tipo" v-model="formulario.tipo_respaldo">
              <option value="Completo">Completo</option>
              <option value="Incremental">Incremental</option>
              <option value="Diferencial">Diferencial</option>
              <option value="Manual">Manual</option>
            </select>
          </div>

          <div class="form-group">
            <label for="resultado">Resultado *</label>
            <select
              id="resultado"
              v-model="formulario.resultado"
              required
            >
              <option value="Exitoso">Exitoso</option>
              <option value="Fallido">Fallido</option>
            </select>
          </div>

          <div class="form-group">
            <label for="tamano">Tamaño (MB)</label>
            <input
              id="tamano"
              v-model="formulario.tamanio_mb"
              type="number"
              min="0"
              step="0.01"
              placeholder="Ej. 250.50"
            />
          </div>

          <div class="form-group">
            <label for="dispositivo">Dispositivo externo</label>
            <input
              id="dispositivo"
              v-model="formulario.dispositivo_externo"
              type="text"
              maxlength="100"
              placeholder="Ej. Disco externo 1 TB"
            />
          </div>

          <div class="form-group full-width">
            <label for="ruta">Ruta de destino</label>
            <input
              id="ruta"
              v-model="formulario.ruta_destino"
              type="text"
              maxlength="255"
              placeholder="Ej. E:\Respaldos\Servidor01"
            />
          </div>

          <div class="form-group full-width">
            <label for="detalles">Detalles del error u observaciones</label>
            <textarea
              id="detalles"
              v-model="formulario.detalles_error"
              rows="3"
              placeholder="Describe el error o agrega alguna observación..."
            ></textarea>
          </div>

        </div>

        <div v-if="mensajeError" class="message error">
          {{ mensajeError }}
        </div>

        <div class="form-actions">
          <button
            type="button"
            class="btn-secondary"
            @click="cerrarFormulario"
          >
            Cancelar
          </button>

          <button
            type="submit"
            class="btn-primary"
            :disabled="guardando"
          >
            {{ guardando ? 'Guardando...' : 'Guardar respaldo' }}
          </button>
        </div>

      </form>
    </section>

    <!-- Mensajes generales -->
    <div v-if="mensajeExito" class="message success">
      {{ mensajeExito }}
    </div>

    <div v-if="mensajeError && !mostrarFormulario" class="message error">
      {{ mensajeError }}
    </div>

    <!-- Sección de consulta -->
    <section class="table-card">

      <div class="section-header">
        <div>
          <h2>Historial de respaldos</h2>
          <p>Consulta las operaciones registradas en el sistema.</p>
        </div>
      </div>

      <!-- Buscador y filtros -->
      <div class="filters">

        <input
          v-model="busqueda"
          type="text"
          placeholder="Buscar por equipo, servidor o dispositivo..."
          class="search-input"
        />

        <select v-model="filtroResultado" class="filter-select">
          <option value="Todos">Todos los resultados</option>
          <option value="Exitoso">Exitosos</option>
          <option value="Fallido">Fallidos</option>
        </select>

      </div>

      <div class="results-count">
        Mostrando {{ respaldosFiltrados.length }} de {{ totalRespaldos }} registros
      </div>

      <!-- Tabla de resultados -->
      <div class="table-container">

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Equipo</th>
              <th>Servidor</th>
              <th>Fecha y hora</th>
              <th>Tipo</th>
              <th>Tamaño</th>
              <th>Resultado</th>
              <th>Destino</th>
            </tr>
          </thead>

          <tbody>

            <tr v-if="cargando">
              <td colspan="8" class="empty-state">
                Cargando respaldos...
              </td>
            </tr>

            <tr v-else-if="respaldosFiltrados.length === 0">
              <td colspan="8" class="empty-state">
                No se encontraron respaldos registrados.
              </td>
            </tr>

            <tr
              v-for="respaldo in respaldosFiltrados"
              :key="respaldo.id"
            >
              <td>#{{ respaldo.id }}</td>

              <td>{{ obtenerNombreEquipo(respaldo.equipo_id) }}</td>

              <td>{{ obtenerNombreServidor(respaldo.servidor_id) }}</td>

              <td>{{ formatearFecha(respaldo.fecha_hora) }}</td>

              <td>{{ respaldo.tipo_respaldo || 'No especificado' }}</td>

              <td>
                {{
                  respaldo.tamanio_mb !== null
                    ? `${respaldo.tamanio_mb} MB`
                    : 'No especificado'
                }}
              </td>

              <td>
                <span
                  class="status-badge"
                  :class="respaldo.resultado?.toLowerCase() === 'exitoso'
                    ? 'status-success'
                    : respaldo.resultado?.toLowerCase() === 'fallido'
                      ? 'status-error'
                      : 'status-unknown'"
                >
                  {{ respaldo.resultado || 'Sin resultado' }}
                </span>
              </td>

              <td>
                {{ respaldo.dispositivo_externo || respaldo.ruta_destino || 'No especificado' }}
              </td>
            </tr>

          </tbody>
        </table>

      </div>
    </section>

  </div>
</template>

<style scoped>
/* Contenedor principal de la vista */
.respaldos {
  padding: 24px;
  color: #1f2937;
}

/* Encabezado y botones principales */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 25px;
}

.page-header h1 {
  margin: 0 0 6px;
  font-size: 25px;
}

.page-header p,
.section-header p {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* Estilos generales de botones */
button {
  border: none;
  border-radius: 7px;
  padding: 10px 15px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #2563eb;
  color: white;
}

.btn-primary:hover {
  background-color: #1d4ed8;
}

.btn-refresh,
.btn-secondary {
  background-color: #e2e8f0;
  color: #334155;
}

.btn-close {
  background: transparent;
  color: #64748b;
  font-size: 18px;
  padding: 5px 10px;
}

/* Tarjetas de resumen */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 15px;
  background: white;
  padding: 20px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(15, 23, 42, 0.04);
  min-width: 0;
}

.summary-icon {
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-size: 20px;
  flex-shrink: 0;
}

.summary-icon.blue {
  background: #dbeafe;
  color: #2563eb;
}

.summary-icon.green {
  background: #dcfce7;
  color: #16a34a;
}

.summary-icon.red {
  background: #fee2e2;
  color: #dc2626;
}

.summary-icon.purple {
  background: #ede9fe;
  color: #7c3aed;
}

.summary-card p {
  margin: 0 0 7px;
  color: #64748b;
  font-size: 12px;
}

.summary-card h2 {
  margin: 0;
  font-size: 23px;
}

.summary-card .last-backup {
  font-size: 12px;
  line-height: 1.5;
}

/* Tarjetas del formulario y de la tabla */
.form-card,
.table-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 22px;
  margin-bottom: 24px;
  box-shadow: 0 2px 5px rgba(15, 23, 42, 0.04);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0 0 6px;
  font-size: 17px;
}

/* Distribución de los campos del formulario */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 17px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.form-group label {
  font-size: 12px;
  font-weight: 600;
  color: #475569;
}

.form-group input,
.form-group select,
.form-group textarea,
.search-input,
.filter-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 7px;
  background: white;
  color: #1f2937;
  font-family: inherit;
  font-size: 13px;
  outline: none;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus,
.search-input:focus,
.filter-select:focus {
  border-color: #2563eb;
}

.form-group textarea {
  resize: vertical;
}

.full-width {
  grid-column: 1 / -1;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

/* Mensajes de confirmación y error */
.message {
  padding: 12px 15px;
  border-radius: 7px;
  margin-bottom: 18px;
  font-size: 13px;
}

.success {
  background: #dcfce7;
  color: #166534;
}

.error {
  background: #fee2e2;
  color: #991b1b;
}

/* Buscador y filtros */
.filters {
  display: grid;
  grid-template-columns: 1fr 220px;
  gap: 12px;
  margin-bottom: 15px;
}

.results-count {
  color: #64748b;
  font-size: 12px;
  margin-bottom: 12px;
}

/* Tabla de respaldos */
.table-container {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 950px;
}

th {
  background: #f8fafc;
  color: #475569;
  font-size: 11px;
  font-weight: 700;
  text-align: left;
  padding: 13px 12px;
  white-space: nowrap;
}

td {
  padding: 13px 12px;
  border-bottom: 1px solid #e2e8f0;
  font-size: 12px;
  color: #334155;
}

tbody tr:hover {
  background: #f8fafc;
}

.empty-state {
  text-align: center;
  color: #64748b;
  padding: 30px;
}

/* Indicadores de resultado */
.status-badge {
  display: inline-block;
  padding: 5px 9px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.status-success {
  background: #dcfce7;
  color: #166534;
}

.status-error {
  background: #fee2e2;
  color: #991b1b;
}

.status-unknown {
  background: #e2e8f0;
  color: #475569;
}

/* Adaptación a pantallas medianas */
@media (max-width: 1000px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

/* Adaptación a celulares */
@media (max-width: 700px) {
  .respaldos {
    padding: 15px;
  }

  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions button {
    flex: 1;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .form-grid,
  .filters {
    grid-template-columns: 1fr;
  }

  .full-width {
    grid-column: auto;
  }
}
</style>
