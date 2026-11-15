
<script setup lang="ts">
// Importamos las herramientas reactivas de Vue.
import { computed, onMounted, ref } from 'vue'

// Importamos la función para consultar los datos del backend.
import { obtenerDatos } from '../services/api'

// Representa la estructura de cada registro que devuelve el backend.
interface RegistroHistorial {
  id: number
  fecha_hora: string
  modulo: string
  accion: string
  descripcion: string
  entidad: string | null
  entidad_id: number | null
  usuario: string
}

// Guarda los registros obtenidos desde FastAPI.
const registros = ref<RegistroHistorial[]>([])

// Controla el estado de carga de la información.
const cargando = ref(false)

// Guarda los posibles errores de consulta.
const error = ref('')

// Almacena el texto escrito en el buscador.
const busqueda = ref('')

// Almacena el módulo seleccionado.
const filtroModulo = ref('Todos')

// Almacena la acción seleccionada.
const filtroAccion = ref('Todas')

// Almacena las fechas seleccionadas.
const fechaInicial = ref('')
const fechaFinal = ref('')

// Consulta los registros del historial.
async function cargarHistorial() {
  cargando.value = true
  error.value = ''

  try {
    // Solicitamos los registros al backend.
    registros.value = await obtenerDatos<RegistroHistorial[]>('/api/historial/')
  } catch (err) {
    // Capturamos cualquier error durante la consulta.
    error.value =
      err instanceof Error
        ? err.message
        : 'No fue posible consultar el historial.'
  } finally {
    // Finalizamos el indicador de carga.
    cargando.value = false
  }
}

// Obtenemos los módulos existentes en los registros.
const modulosDisponibles = computed(() => {
  return [...new Set(registros.value.map((registro) => registro.modulo))]
    .sort((a, b) => a.localeCompare(b))
})

// Obtenemos las acciones existentes en los registros.
const accionesDisponibles = computed(() => {
  return [...new Set(registros.value.map((registro) => registro.accion))]
    .sort((a, b) => a.localeCompare(b))
})

// Obtiene la fecha del registro en formato AAAA-MM-DD.
function fechaCalendario(fecha: string): string {
  // Si no existe una fecha, devolvemos una cadena vacía.
  if (!fecha) return ''

  // Normalizamos el formato recibido.
  const normalizada = fecha.includes('T') ? fecha : fecha.replace(' ', 'T')
  const fechaObjeto = new Date(normalizada)

  // Comprobamos que la fecha sea válida.
  if (Number.isNaN(fechaObjeto.getTime())) return ''

  // Construimos la fecha utilizando la zona horaria local.
  const anio = fechaObjeto.getFullYear()
  const mes = String(fechaObjeto.getMonth() + 1).padStart(2, '0')
  const dia = String(fechaObjeto.getDate()).padStart(2, '0')

  return `${anio}-${mes}-${dia}`
}

// Convierte la fecha recibida en un formato legible.
function formatearFecha(fecha: string): string {
  // Si la fecha no existe, mostramos un guion.
  if (!fecha) return '—'

  // Normalizamos el formato recibido.
  const normalizada = fecha.includes('T') ? fecha : fecha.replace(' ', 'T')
  const fechaObjeto = new Date(normalizada)

  // Si la fecha no es válida, mostramos el valor original.
  if (Number.isNaN(fechaObjeto.getTime())) return fecha

  // Mostramos fecha y hora con el formato utilizado en México.
  return fechaObjeto.toLocaleString('es-MX', {
    dateStyle: 'short',
    timeStyle: 'short',
  })
}

// Comprobamos que el rango de fechas seleccionado sea válido.
const rangoFechasInvalido = computed(() => {
  return (
    fechaInicial.value !== '' &&
    fechaFinal.value !== '' &&
    fechaInicial.value > fechaFinal.value
  )
})

// Filtramos los registros según los criterios seleccionados.
const registrosFiltrados = computed(() => {
  // Convertimos el texto de búsqueda a minúsculas.
  const texto = busqueda.value.trim().toLowerCase()

  return registros.value.filter((registro) => {
    // Comprobamos si coincide con el módulo seleccionado.
    const coincideModulo =
      filtroModulo.value === 'Todos' ||
      registro.modulo === filtroModulo.value

    // Comprobamos si coincide con la acción seleccionada.
    const coincideAccion =
      filtroAccion.value === 'Todas' ||
      registro.accion === filtroAccion.value

    // Preparamos los datos que se pueden consultar mediante el buscador.
    const datosBusqueda = [
      registro.id,
      registro.modulo,
      registro.accion,
      registro.descripcion,
      registro.usuario,
      registro.entidad ?? '',
      registro.entidad_id ?? '',
    ].join(' ').toLowerCase()

    // Comprobamos si el texto aparece en alguno de los campos.
    const coincideBusqueda = !texto || datosBusqueda.includes(texto)

    // Obtenemos la fecha del registro.
    const fechaRegistro = fechaCalendario(registro.fecha_hora)

    // Comprobamos la fecha inicial.
    const coincideFechaInicial =
      !fechaInicial.value ||
      (fechaRegistro !== '' && fechaRegistro >= fechaInicial.value)

    // Comprobamos la fecha final.
    const coincideFechaFinal =
      !fechaFinal.value ||
      (fechaRegistro !== '' && fechaRegistro <= fechaFinal.value)

    // El registro aparece si cumple todos los filtros.
    return (
      coincideModulo &&
      coincideAccion &&
      coincideBusqueda &&
      coincideFechaInicial &&
      coincideFechaFinal
    )
  })
})

// Limpiamos todos los filtros.
function limpiarFiltros() {
  busqueda.value = ''
  filtroModulo.value = 'Todos'
  filtroAccion.value = 'Todas'
  fechaInicial.value = ''
  fechaFinal.value = ''
}

// Consultamos el historial cuando se abre la vista.
onMounted(cargarHistorial)
</script>

<template>
  <section class="historial-view">

    <!-- Encabezado del módulo. -->
    <header class="encabezado">
      <div>
        <h1>Historial de actividades</h1>
        <p>Consulta los movimientos realizados en el sistema.</p>
      </div>

      <!-- Botón para actualizar los registros. -->
      <button
        type="button"
        class="btn-actualizar"
        @click="cargarHistorial"
        :disabled="cargando"
      >
        {{ cargando ? 'Actualizando...' : 'Actualizar' }}
      </button>
    </header>

    <!-- Indicador de carga. -->
    <p v-if="cargando" class="mensaje">
      Cargando registros...
    </p>

    <!-- Mensaje cuando ocurre un error. -->
    <p v-else-if="error" class="mensaje error">
      {{ error }}
    </p>

    <!-- Contenido cuando termina la consulta. -->
    <template v-else>

      <!-- Mensaje cuando no existen registros. -->
      <div v-if="registros.length === 0" class="mensaje">
        No hay registros disponibles en el historial.
      </div>

      <template v-else>

        <!-- Controles de búsqueda y filtros. -->
        <section class="filtros-contenedor">

          <!-- Buscador general. -->
          <div class="campo campo-busqueda">
            <label for="busqueda">Buscar registros</label>
            <input
              id="busqueda"
              v-model="busqueda"
              type="text"
              placeholder="Descripción, usuario, ID..."
            />
          </div>

          <!-- Filtro por módulo. -->
          <div class="campo">
            <label for="filtro-modulo">Módulo</label>
            <select id="filtro-modulo" v-model="filtroModulo">
              <option value="Todos">Todos los módulos</option>
              <option
                v-for="modulo in modulosDisponibles"
                :key="modulo"
                :value="modulo"
              >
                {{ modulo }}
              </option>
            </select>
          </div>

          <!-- Filtro por acción. -->
          <div class="campo">
            <label for="filtro-accion">Acción</label>
            <select id="filtro-accion" v-model="filtroAccion">
              <option value="Todas">Todas las acciones</option>
              <option
                v-for="accion in accionesDisponibles"
                :key="accion"
                :value="accion"
              >
                {{ accion }}
              </option>
            </select>
          </div>

          <!-- Filtro por fecha inicial. -->
          <div class="campo">
            <label for="fecha-inicial">Desde</label>
            <input
              id="fecha-inicial"
              v-model="fechaInicial"
              type="date"
              :max="fechaFinal || undefined"
            />
          </div>

          <!-- Filtro por fecha final. -->
          <div class="campo">
            <label for="fecha-final">Hasta</label>
            <input
              id="fecha-final"
              v-model="fechaFinal"
              type="date"
              :min="fechaInicial || undefined"
            />
          </div>

          <!-- Botón para restablecer los filtros. -->
          <button
            type="button"
            class="btn-limpiar"
            @click="limpiarFiltros"
          >
            Limpiar filtros
          </button>

        </section>

        <!-- Mensaje cuando el periodo seleccionado no es válido. -->
        <p v-if="rangoFechasInvalido" class="error mensaje-error">
          La fecha inicial no puede ser posterior a la fecha final.
        </p>

        <!-- Contador de resultados. -->
        <div v-if="!rangoFechasInvalido" class="contador-resultados">
          Mostrando
          <strong>{{ registrosFiltrados.length }}</strong>
          de
          <strong>{{ registros.length }}</strong>
          registros
        </div>

        <!-- Tabla de resultados. -->
        <div v-if="!rangoFechasInvalido" class="tabla-contenedor">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Fecha y hora</th>
                <th>Módulo</th>
                <th>Acción</th>
                <th>Descripción</th>
                <th>Usuario</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="registro in registrosFiltrados"
                :key="registro.id"
              >
                <td>{{ registro.id }}</td>
                <td>{{ formatearFecha(registro.fecha_hora) }}</td>
                <td>{{ registro.modulo }}</td>
                <td>{{ registro.accion }}</td>
                <td>{{ registro.descripcion }}</td>
                <td>{{ registro.usuario }}</td>
              </tr>

              <!-- Mensaje cuando ningún registro coincide con los filtros. -->
              <tr v-if="registrosFiltrados.length === 0">
                <td colspan="6" class="sin-registros">
                  No se encontraron registros con los criterios seleccionados.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </template>
    </template>
  </section>
</template>

<style scoped>
/* Contenedor principal del historial. */
.historial-view {
  width: 100%;
  padding: 24px;
  box-sizing: border-box;
  color: #1f2937;
}

/* Distribución del encabezado. */
.encabezado {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.encabezado h1 {
  margin: 0 0 8px;
}

.encabezado p {
  margin: 0;
  color: #64748b;
}

/* Estilos generales de los botones. */
button {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  font: inherit;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

/* Botón para actualizar la información. */
.btn-actualizar {
  background-color: #2563eb;
}

.btn-actualizar:hover:not(:disabled) {
  background-color: #1d4ed8;
}

/* Contenedor de los filtros. */
.filtros-contenedor {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  gap: 14px;
  margin-bottom: 18px;
  padding: 18px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

/* Organización individual de los campos. */
.campo {
  display: flex;
  flex-direction: column;
  gap: 7px;
  min-width: 150px;
}

.campo-busqueda {
  flex: 1;
  min-width: 220px;
}

.campo label {
  color: #475569;
  font-size: 13px;
  font-weight: 600;
}

/* Estilos de los campos de búsqueda y filtros. */
.campo input,
.campo select {
  box-sizing: border-box;
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: white;
  color: #334155;
  font: inherit;
}

.campo input:focus,
.campo select:focus {
  border-color: #2563eb;
  outline: none;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12);
}

/* Botón para limpiar los filtros. */
.btn-limpiar {
  background-color: #6b7280;
}

.btn-limpiar:hover {
  background-color: #4b5563;
}

/* Contador de resultados. */
.contador-resultados {
  margin: 16px 0 10px;
  color: #64748b;
  font-size: 14px;
}

.contador-resultados strong {
  color: #1e293b;
}

/* Contenedor de la tabla. */
.tabla-contenedor {
  width: 100%;
  overflow-x: auto;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

/* Estilos generales de la tabla. */
table {
  width: 100%;
  min-width: 850px;
  border-collapse: collapse;
}

th,
td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
  font-size: 14px;
}

th {
  background-color: #f8fafc;
  color: #475569;
  font-weight: 600;
}

/* Mensajes de carga y ausencia de registros. */
.mensaje {
  padding: 20px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #64748b;
  text-align: center;
}

.error {
  color: #c0392b;
  background-color: #fef2f2;
  border-color: #fecaca;
}

.mensaje-error {
  margin-bottom: 15px;
}

.sin-registros {
  padding: 25px;
  color: #64748b;
  text-align: center;
}

/* Adaptación a pantallas pequeñas. */
@media (max-width: 700px) {
  .encabezado {
    align-items: flex-start;
    flex-direction: column;
  }

  .filtros-contenedor {
    align-items: stretch;
    flex-direction: column;
  }

  .campo {
    width: 100%;
  }
}
</style>
