<script setup lang="ts">

// Importamos las funciones necesarias de Vue.
import { ref, computed, onMounted } from 'vue'

// Importamos las funciones para consultar, registrar, actualizar y eliminar información.
import {
  obtenerDatos,
  enviarDatos,
  actualizarDatos,
  eliminarDatos
} from '../services/api'

// Definimos la estructura de un mantenimiento.
interface Mantenimiento {
  id: number
  equipo_id: number
  tecnico_id: number
  fecha_mantenimiento: string
  tipo_mantenimiento: string | null
  problema_detectado: string | null
  solucion_aplicada: string | null
  tiempo_empleado_min: number | null
  observaciones: string | null
}

// Definimos la estructura de un equipo.
interface Equipo {
  id: number
  nombre: string
  tipo_equipo: string | null
  estado: string | null
}

// Definimos la estructura de un técnico.
interface Tecnico {
  id: number
  nombre: string
  activo: boolean
}

// Definimos los datos que enviaremos al backend.
interface MantenimientoNuevo {
  equipo_id: number
  tecnico_id: number
  tipo_mantenimiento: string
  problema_detectado: string
  solucion_aplicada: string
  tiempo_empleado_min: number | null
  observaciones: string
}

// Variables para almacenar la información del sistema.
const mantenimientos = ref<Mantenimiento[]>([])
const equipos = ref<Equipo[]>([])
const tecnicos = ref<Tecnico[]>([])

// Almacena el texto que el usuario escribe en el buscador.
const busqueda = ref('')

// Almacena el tipo de mantenimiento seleccionado.
const filtroTipo = ref('Todos')

// Almacena las fechas seleccionadas por el usuario.
const fechaInicial = ref('')
const fechaFinal = ref('')

// Variables para controlar los mensajes y la carga.
const cargando = ref(false)
const guardando = ref(false)
const eliminando = ref<number | null>(null)
const error = ref('')
const mensajeExito = ref('')

// Controla si el formulario está visible.
const mostrarFormulario = ref(false)

// Guarda el ID del mantenimiento que estamos editando.
const mantenimientoEditando = ref<number | null>(null)

// Filtra los técnicos disponibles para asignar a un mantenimiento.
// Conserva al técnico actual durante la edición aunque esté inactivo.
const tecnicosDisponibles = computed(() => {
  const mantenimientoActual = mantenimientos.value.find(
    (mantenimiento) => mantenimiento.id === mantenimientoEditando.value
  )

  return tecnicos.value.filter(
    (tecnico) =>
      tecnico.activo || tecnico.id === mantenimientoActual?.tecnico_id
  )
})

// Filtra los equipos disponibles para asignar a un mantenimiento.
// Conserva el equipo actual durante la edición aunque esté inactivo.
const equiposDisponibles = computed(() => {
  const mantenimientoActual = mantenimientos.value.find(
    (mantenimiento) => mantenimiento.id === mantenimientoEditando.value
  )

  return equipos.value.filter(
    (equipo) =>
      equipo.estado !== 'Inactivo' ||
      equipo.id === mantenimientoActual?.equipo_id
  )
})

// Objeto que almacena los datos capturados en el formulario.
const formulario = ref({
  equipo_id: '',
  tecnico_id: '',
  tipo_mantenimiento: 'Preventivo',
  problema_detectado: '',
  solucion_aplicada: '',
  tiempo_empleado_min: '',
  observaciones: '',
})

// Consultamos los mantenimientos, equipos y técnicos.
async function cargarInformacion() {
  cargando.value = true
  error.value = ''

  try {
    // Solicitamos la información de los tres endpoints.
    const [datosMantenimientos, datosEquipos, datosTecnicos] =
      await Promise.all([
        obtenerDatos<Mantenimiento[]>('/api/mantenimientos/'),
        obtenerDatos<Equipo[]>('/api/equipos/'),
        obtenerDatos<Tecnico[]>('/api/tecnicos/'),
      ])

    // Guardamos las respuestas recibidas.
    mantenimientos.value = datosMantenimientos
    equipos.value = datosEquipos
    tecnicos.value = datosTecnicos

  } catch (err) {
    // Capturamos cualquier error durante las consultas.
    error.value =
      err instanceof Error ? err.message : 'No se pudo cargar la información.'

  } finally {
    // Finalizamos el indicador de carga.
    cargando.value = false
  }
}

// Buscamos el nombre de un equipo mediante su identificador.
function obtenerNombreEquipo(id: number): string {
  const equipo = equipos.value.find((elemento) => elemento.id === id)
  return equipo ? equipo.nombre : `Equipo ${id}`
}

// Buscamos el nombre de un técnico mediante su identificador.
function obtenerNombreTecnico(id: number): string {
  const tecnico = tecnicos.value.find((elemento) => elemento.id === id)
  return tecnico ? tecnico.nombre : `Técnico ${id}`
}

// Generamos una lista de mantenimientos según la búsqueda y los filtros.
const mantenimientosFiltrados = computed(() => {
  // Convertimos el texto de búsqueda a minúsculas.
  const texto = busqueda.value.trim().toLowerCase()

  // Obtenemos el tipo de mantenimiento seleccionado.
  const tipoSeleccionado = filtroTipo.value

  // Filtramos los registros según las condiciones seleccionadas.
  return mantenimientos.value.filter((mantenimiento) => {
    // Comprobamos si coincide con el tipo seleccionado.
    const coincideTipo =
      tipoSeleccionado === 'Todos' ||
      mantenimiento.tipo_mantenimiento === tipoSeleccionado

    // Obtenemos los nombres del equipo y del técnico.
    const equipo = obtenerNombreEquipo(mantenimiento.equipo_id).toLowerCase()
    const tecnico = obtenerNombreTecnico(mantenimiento.tecnico_id).toLowerCase()

    // Convertimos los campos de texto a minúsculas.
    const problema = (mantenimiento.problema_detectado || '').toLowerCase()
    const solucion = (mantenimiento.solucion_aplicada || '').toLowerCase()

    // Comprobamos si coincide con el texto de búsqueda.
    const coincideBusqueda =
      !texto ||
      equipo.includes(texto) ||
      tecnico.includes(texto) ||
      problema.includes(texto) ||
      solucion.includes(texto)

    // Comparamos la fecha civil local, no los primeros caracteres del texto.
    const fechaRegistro = fechaCalendario(mantenimiento.fecha_mantenimiento)

    // Comprobamos si el registro cumple con la fecha inicial.
    const coincideFechaInicial =
      !fechaInicial.value ||
      (fechaRegistro !== '' && fechaRegistro >= fechaInicial.value)

    // Comprobamos si el registro cumple con la fecha final.
    const coincideFechaFinal =
      !fechaFinal.value ||
      (fechaRegistro !== '' && fechaRegistro <= fechaFinal.value)

    // El registro aparece si cumple todos los filtros.
    return (
      coincideTipo &&
      coincideBusqueda &&
      coincideFechaInicial &&
      coincideFechaFinal
    )
  })
})

// Indica si el periodo seleccionado es válido.
const rangoFechasInvalido = computed(() => {
  return (
    fechaInicial.value !== '' &&
    fechaFinal.value !== '' &&
    fechaInicial.value > fechaFinal.value
  )
})

// Limpiamos todos los filtros de búsqueda.
function limpiarFiltros() {
  busqueda.value = ''
  filtroTipo.value = 'Todos'
  fechaInicial.value = ''
  fechaFinal.value = ''
}

// Limpiamos los campos del formulario.
function limpiarFormulario() {
  formulario.value = {
    equipo_id: '',
    tecnico_id: '',
    tipo_mantenimiento: 'Preventivo',
    problema_detectado: '',
    solucion_aplicada: '',
    tiempo_empleado_min: '',
    observaciones: '',
  }

  // Indicamos que ya no estamos editando ningún registro.
  mantenimientoEditando.value = null
}

// Preparamos el formulario para registrar un mantenimiento nuevo.
function nuevoMantenimiento() {
  // Limpiamos los campos anteriores.
  limpiarFormulario()

  // Mostramos el formulario.
  mostrarFormulario.value = true

  // Limpiamos los mensajes anteriores.
  error.value = ''
  mensajeExito.value = ''
}

// Cargamos los datos de un mantenimiento seleccionado para editarlo.
function editarMantenimiento(mantenimiento: Mantenimiento) {
  // Guardamos el identificador del mantenimiento seleccionado.
  mantenimientoEditando.value = mantenimiento.id

  // Colocamos los datos actuales dentro del formulario.
  formulario.value = {
    equipo_id: String(mantenimiento.equipo_id),
    tecnico_id: String(mantenimiento.tecnico_id),
    tipo_mantenimiento: mantenimiento.tipo_mantenimiento || 'Preventivo',
    problema_detectado: mantenimiento.problema_detectado || '',
    solucion_aplicada: mantenimiento.solucion_aplicada || '',
    tiempo_empleado_min: mantenimiento.tiempo_empleado_min !== null
      ? String(mantenimiento.tiempo_empleado_min)
      : '',
    observaciones: mantenimiento.observaciones || '',
  }

  // Mostramos el formulario y limpiamos mensajes anteriores.
  mostrarFormulario.value = true
  error.value = ''
  mensajeExito.value = ''
}

// Obtiene la fecha civil en la zona horaria del navegador (AAAA-MM-DD).
function fechaCalendario(fecha: string | null): string {
  if (!fecha) return ''

  const normalizada = fecha.includes('T') ? fecha : fecha.replace(' ', 'T')
  const fechaObjeto = new Date(normalizada)

  if (Number.isNaN(fechaObjeto.getTime())) return ''

  const anio = fechaObjeto.getFullYear()
  const mes = String(fechaObjeto.getMonth() + 1).padStart(2, '0')
  const dia = String(fechaObjeto.getDate()).padStart(2, '0')

  return `${anio}-${mes}-${dia}`
}

// Convierte la fecha recibida del servidor a un formato más fácil de leer.
function formatearFecha(fecha: string | null): string {
  // Si no existe una fecha, mostramos un guion.
  if (!fecha) return '—'

  const normalizada = fecha.includes('T') ? fecha : fecha.replace(' ', 'T')
  const fechaObjeto = new Date(normalizada)

  // Si la fecha no es válida, mostramos el valor original.
  if (Number.isNaN(fechaObjeto.getTime())) return fecha

  // Mostramos la fecha y hora con el formato usado en México.
  return new Intl.DateTimeFormat('es-MX', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  }).format(fechaObjeto)
}
// Registra un nuevo mantenimiento o actualiza uno existente.
async function guardarMantenimiento() {
  error.value = ''
  mensajeExito.value = ''

  if (!formulario.value.equipo_id || !formulario.value.tecnico_id) {
    error.value = 'Selecciona el equipo y el técnico responsable.'
    return
  }

 // Convertimos el tiempo a texto para poder validarlo correctamente.
const tiempo = String(formulario.value.tiempo_empleado_min ?? '').trim()

// Verificamos que, si se proporcionó un tiempo, sea un número entero no negativo.
if (tiempo !== '' && !/^\d+$/.test(tiempo)) {
  error.value = 'El tiempo empleado debe ser un número entero igual o mayor que cero.'
  return
}

  guardando.value = true

  try {
    // Convertimos los identificadores y el tiempo a números.
    const datos: MantenimientoNuevo = {
      equipo_id: Number(formulario.value.equipo_id),
      tecnico_id: Number(formulario.value.tecnico_id),
      tipo_mantenimiento: formulario.value.tipo_mantenimiento,
      problema_detectado: formulario.value.problema_detectado,
      solucion_aplicada: formulario.value.solucion_aplicada,
      tiempo_empleado_min: formulario.value.tiempo_empleado_min
        ? Number(formulario.value.tiempo_empleado_min)
        : null,
      observaciones: formulario.value.observaciones,
    }

    // Comprobamos si estamos editando o registrando un mantenimiento.
    if (mantenimientoEditando.value !== null) {
      // Actualizamos el mantenimiento mediante una petición PUT.
      await actualizarDatos<MantenimientoNuevo, Mantenimiento>(
        `/api/mantenimientos/${mantenimientoEditando.value}`,
        datos
      )

      // Mostramos el mensaje de actualización.
      mensajeExito.value = 'El mantenimiento se actualizó y ya aparece en el listado.'

    } else {
      // Registramos un nuevo mantenimiento mediante una petición POST.
      await enviarDatos<MantenimientoNuevo, Mantenimiento>(
        '/api/mantenimientos/',
        datos
      )

      // Mostramos el mensaje de registro.
      mensajeExito.value = 'El mantenimiento se registró y ya aparece en el listado.'
    }

    // Limpiamos el formulario y lo ocultamos.
    limpiarFormulario()
    mostrarFormulario.value = false

    // Actualizamos la tabla para mostrar los cambios.
    await cargarInformacion()

  } catch (err) {
    // Mostramos el mensaje de error recibido del backend.
    error.value =
      err instanceof Error ? err.message : 'No se pudo guardar el mantenimiento.'

  } finally {
    // Finalizamos el indicador de guardado.
    guardando.value = false
  }
}

// Elimina un mantenimiento después de solicitar confirmación.
async function eliminarMantenimiento(mantenimiento: Mantenimiento) {
  // Evitamos iniciar otra eliminación mientras exista una en proceso.
  if (eliminando.value !== null) {
    return
  }

  // Solicitamos confirmación antes de eliminar el registro.
  const confirmar = window.confirm(
    `¿Estás segura de que deseas eliminar el mantenimiento #${mantenimiento.id}? Esta acción no se puede deshacer.`
  )

  // Si el usuario cancela, detenemos la operación.
  if (!confirmar) {
    return
  }

  // Guardamos el ID que se está eliminando.
  eliminando.value = mantenimiento.id

  // Limpiamos los mensajes anteriores.
  error.value = ''
  mensajeExito.value = ''

  try {
    // Enviamos la petición DELETE al backend.
    await eliminarDatos<{ mensaje: string; id: number }>(
      `/api/mantenimientos/${mantenimiento.id}`
    )

    // Si el registro eliminado estaba abierto para edición,
    // cerramos el formulario y limpiamos sus campos.
    if (mantenimientoEditando.value === mantenimiento.id) {
      limpiarFormulario()
      mostrarFormulario.value = false
    }

    // Mostramos el mensaje de confirmación.
    mensajeExito.value = `El mantenimiento #${mantenimiento.id} se eliminó del listado.`

    // Actualizamos la tabla para retirar el registro eliminado.
    await cargarInformacion()

  } catch (err) {
    // Mostramos el error si no fue posible eliminar el registro.
    error.value =
      err instanceof Error
        ? err.message
        : 'No se pudo eliminar el mantenimiento.'

  } finally {
    // Liberamos el control de eliminación.
    eliminando.value = null
  }
}

// Cargamos la información cuando se abre la vista.
onMounted(cargarInformacion)

</script>

<template>

  <main class="mantenimientos">

    <!-- Encabezado del módulo. -->
    <header class="encabezado">

      <div>
        <h1>Mantenimientos</h1>
        <p>Consulta y seguimiento de los mantenimientos registrados.</p>
      </div>

      <div class="acciones">

        <!-- Botón para iniciar un nuevo registro. -->
        <button
          class="btn-nuevo"
          @click="nuevoMantenimiento"
        >
          + Nuevo mantenimiento
        </button>

        <!-- Botón para actualizar la información de la tabla. -->
        <button
          class="btn-actualizar"
          @click="cargarInformacion"
          :disabled="cargando"
        >
          {{ cargando ? 'Cargando...' : 'Actualizar' }}
        </button>

      </div>
    </header>

    <!-- Formulario para registrar o editar un mantenimiento. -->
    <section v-if="mostrarFormulario" class="formulario-contenedor">

      <!-- El título cambia dependiendo de la operación. -->
      <h2>
        {{ mantenimientoEditando !== null
          ? 'Editar mantenimiento'
          : 'Registrar nuevo mantenimiento' }}
      </h2>

      <p class="ayuda-formulario">
        Equipo, técnico y tipo son obligatorios. El tiempo, si lo indicas, debe expresarse en minutos enteros.
      </p>

      <form @submit.prevent="guardarMantenimiento">

        <div class="campos">

          <!-- Selector de equipo. -->
          <div class="campo">

            <label for="equipo">Equipo</label>

            <select
              id="equipo"
              v-model="formulario.equipo_id"
              required
            >
              <option value="" disabled>Selecciona un equipo</option>

              <option
                v-for="equipo in equiposDisponibles"
                :key="equipo.id"
                :value="String(equipo.id)"
              >
                {{ equipo.nombre }}
                {{ equipo.estado === 'Inactivo' ? '(Inactivo - asignación actual)' : '' }}
              </option>

            </select>

          </div>

          <!-- Selector de técnico. -->
          <div class="campo">

            <label for="tecnico">Técnico responsable</label>

            <select
              id="tecnico"
              v-model="formulario.tecnico_id"
              required
            >
              <option value="" disabled>Selecciona un técnico</option>

              <option
                v-for="tecnico in tecnicosDisponibles"
                :key="tecnico.id"
                :value="String(tecnico.id)"
              >
                {{ tecnico.nombre }}
                {{ !tecnico.activo ? '(Inactivo - asignación actual)' : '' }}
              </option>

            </select>

          </div>

          <!-- Selector del tipo de mantenimiento. -->
          <div class="campo">

            <label for="tipo">Tipo de mantenimiento</label>

            <select
              id="tipo"
              v-model="formulario.tipo_mantenimiento"
              required
            >
              <option value="Preventivo">Preventivo</option>
              <option value="Correctivo">Correctivo</option>
            </select>

          </div>

          <!-- Campo para describir el problema. -->
          <div class="campo campo-completo">

            <label for="problema">Problema detectado</label>

            <textarea
              id="problema"
              v-model="formulario.problema_detectado"
              rows="3"
              placeholder="Describe el problema encontrado..."
            ></textarea>

          </div>

          <!-- Campo para describir la solución. -->
          <div class="campo campo-completo">

            <label for="solucion">Solución aplicada</label>

            <textarea
              id="solucion"
              v-model="formulario.solucion_aplicada"
              rows="3"
              placeholder="Describe la solución realizada..."
            ></textarea>

          </div>

          <!-- Campo para registrar el tiempo empleado. -->
          <div class="campo">

            <label for="tiempo">Tiempo empleado (minutos)</label>

            <input
              id="tiempo"
              v-model="formulario.tiempo_empleado_min"
              type="number"
              min="0"
              step="1"
              placeholder="Ej. 30"
            />

          </div>

          <!-- Campo para agregar observaciones. -->
          <div class="campo campo-completo">

            <label for="observaciones">Observaciones</label>

            <textarea
              id="observaciones"
              v-model="formulario.observaciones"
              rows="3"
              placeholder="Agrega observaciones adicionales..."
            ></textarea>

          </div>

        </div>

        <!-- Botones para cancelar o guardar el formulario. -->
        <div class="botones-formulario">

          <button
            type="button"
            class="btn-cancelar"
            @click="mostrarFormulario = false; limpiarFormulario()"
          >
            Cancelar
          </button>

          <button
            type="submit"
            class="btn-guardar"
            :disabled="guardando"
          >
            {{
              guardando
                ? 'Guardando...'
                : mantenimientoEditando !== null
                  ? 'Guardar cambios'
                  : 'Guardar mantenimiento'
            }}
          </button>

        </div>

      </form>

    </section>

    <!-- Mensaje de confirmación. -->
    <p v-if="mensajeExito" class="exito" role="status">
      {{ mensajeExito }}
    </p>

    <!-- Mensaje de error. -->
    <p v-if="error" class="error" role="alert">
      {{ error }}
    </p>

    <!-- Indicador de carga. -->
    <p v-if="cargando" class="mensaje">
      Cargando información...
    </p>

    <!-- Tabla de mantenimientos registrados. -->
    <section v-else class="tabla-contenedor">

      <!-- Controles para buscar y filtrar mantenimientos. -->
      <div class="filtros-contenedor">

        <!-- Buscador de mantenimientos. -->
        <input
          v-model="busqueda"
          type="text"
          placeholder="Buscar por equipo, técnico, problema o solución..."
          class="busqueda-input"
          aria-label="Buscar mantenimientos"
        />

        <!-- Filtro por tipo de mantenimiento. -->
        <select
          v-model="filtroTipo"
          class="filtro-tipo"
          aria-label="Filtrar por tipo de mantenimiento"
        >
          <option value="Todos">Todos los tipos</option>
          <option value="Preventivo">Preventivo</option>
          <option value="Correctivo">Correctivo</option>
        </select>

        <!-- Filtro por fecha inicial. -->
        <div class="campo-fecha">

          <label for="fecha-inicial">Desde</label>

          <input
            id="fecha-inicial"
            v-model="fechaInicial"
            type="date"
            class="filtro-fecha"
            :max="fechaFinal || undefined"
          />

        </div>

        <!-- Filtro por fecha final. -->
        <div class="campo-fecha">

          <label for="fecha-final">Hasta</label>

          <input
            id="fecha-final"
            v-model="fechaFinal"
            type="date"
            class="filtro-fecha"
            :min="fechaInicial || undefined"
          />

        </div>

        <!-- Botón para restablecer todos los filtros. -->
        <button
          type="button"
          class="btn-limpiar-filtros"
          @click="limpiarFiltros"
        >
          Limpiar filtros
        </button>

      </div>

      <!-- Mensaje si las fechas seleccionadas son incorrectas. -->
      <p v-if="rangoFechasInvalido" class="error" role="alert">
        La fecha inicial no puede ser posterior a la fecha final. Ajusta el periodo para ver los resultados.
      </p>

      <!-- Contador de resultados según los filtros aplicados. -->
      <div v-if="!rangoFechasInvalido" class="contador-resultados">
        Mostrando
        <strong>{{ mantenimientosFiltrados.length }}</strong>
        de
        <strong>{{ mantenimientos.length }}</strong>
        mantenimientos
      </div>

      <!-- Tabla de resultados. -->
      <table>

        <thead>
          <tr>
            <th>ID</th>
            <th>Equipo</th>
            <th>Técnico</th>
            <th>Fecha</th>
            <th>Tipo</th>
            <th>Problema detectado</th>
            <th>Solución aplicada</th>
            <th>Tiempo (min)</th>
            <th>Observaciones</th>
            <th>Acciones</th>
          </tr>
        </thead>

        <tbody>

          <tr
            v-for="mantenimiento in mantenimientosFiltrados"
            :key="mantenimiento.id"
          >

            <td>{{ mantenimiento.id }}</td>
            <td>{{ obtenerNombreEquipo(mantenimiento.equipo_id) }}</td>
            <td>{{ obtenerNombreTecnico(mantenimiento.tecnico_id) }}</td>
            <td>{{ formatearFecha(mantenimiento.fecha_mantenimiento) }}</td>
            <td>{{ mantenimiento.tipo_mantenimiento || '—' }}</td>
            <td>{{ mantenimiento.problema_detectado || '—' }}</td>
            <td>{{ mantenimiento.solucion_aplicada || '—' }}</td>
            <td>{{ mantenimiento.tiempo_empleado_min ?? '—' }}</td>
            <td>{{ mantenimiento.observaciones || '—' }}</td>

            <!-- Acciones disponibles para cada mantenimiento. -->
            <td>

              <!-- Botón para editar el mantenimiento seleccionado. -->
              <button
                class="btn-editar"
                @click="editarMantenimiento(mantenimiento)"
                :disabled="eliminando !== null"
              >
                Editar
              </button>

              <!-- Botón para eliminar el mantenimiento seleccionado. -->
              <button
                class="btn-eliminar"
                @click="eliminarMantenimiento(mantenimiento)"
                :disabled="eliminando !== null"
              >
                {{
                  eliminando === mantenimiento.id
                    ? 'Eliminando...'
                    : 'Eliminar'
                }}
              </button>

            </td>

          </tr>

          <!-- Mensaje cuando no existen registros o no hay coincidencias. -->
          <tr v-if="!rangoFechasInvalido && mantenimientosFiltrados.length === 0">

            <td colspan="10" class="sin-registros">
              {{
                busqueda.trim() ||
                filtroTipo !== 'Todos' ||
                fechaInicial ||
                fechaFinal
                  ? 'No se encontraron mantenimientos con los criterios seleccionados.'
                  : 'No hay mantenimientos registrados.'
              }}
            </td>

          </tr>

        </tbody>

      </table>

    </section>

  </main>

</template>
<style scoped>

/* Estilos generales de la vista. */
.mantenimientos {
  padding: 24px;
  color: #1f2937;
}

/* Distribución del encabezado y sus botones. */
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
  color: #6b7280;
}

.acciones {
  display: flex;
  gap: 10px;
}

/* Estilos generales de los botones. */
button {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-nuevo,
.btn-guardar {
  background: #2563eb;
}

.btn-actualizar {
  background: #4b5563;
}

.btn-cancelar {
  background: #6b7280;
}

/* Estilo del botón para editar registros. */
.btn-editar {
  background: #d97706;
  padding: 8px 12px;
}

/* Estilo del botón para eliminar registros. */
.btn-eliminar {
  background: #dc2626;
  padding: 8px 12px;
  margin-left: 6px;
}

/* Contenedor del formulario. */
.formulario-contenedor {
  margin-bottom: 24px;
  padding: 24px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

.formulario-contenedor h2 {
  margin-top: 0;
  margin-bottom: 8px;
  font-size: 20px;
}

.ayuda-formulario {
  margin: 0 0 20px;
  color: #64748b;
  font-size: 14px;
}

/* Distribución de los campos del formulario. */
.campos {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.campo {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.campo-completo {
  grid-column: 1 / -1;
}

.campo label {
  font-size: 14px;
  font-weight: 600;
}

.campo input,
.campo select,
.campo textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font: inherit;
}

.campo textarea {
  resize: vertical;
}

/* Botones ubicados al final del formulario. */
.botones-formulario {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 22px;
}

/* Contenedor de los controles de búsqueda y filtros. */
.filtros-contenedor {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  gap: 12px;
  margin-bottom: 16px;
}

/* Estilo del campo de búsqueda. */
.busqueda-input {
  width: 100%;
  max-width: 450px;
  box-sizing: border-box;
  padding: 12px 14px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font: inherit;
  outline: none;
}

/* Estilo del selector de tipo. */
.filtro-tipo {
  min-width: 180px;
  padding: 12px 14px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  font: inherit;
  cursor: pointer;
}

/* Contenedor y etiqueta de los campos de fecha. */
.campo-fecha {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.campo-fecha label {
  font-size: 13px;
  font-weight: 600;
  color: #4b5563;
}

/* Estilo de los selectores de fecha. */
.filtro-fecha {
  padding: 11px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  font: inherit;
}

/* Botón para limpiar todos los filtros. */
.btn-limpiar-filtros {
  background: #6b7280;
  padding: 12px 14px;
}

/* Resaltamos los controles cuando el usuario los selecciona. */
.busqueda-input:focus,
.filtro-tipo:focus,
.filtro-fecha:focus {
  border-color: #2563eb;
  outline: none;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12);
}

/* Estilo del contador de resultados. */
.contador-resultados {
  margin: 16px 0 10px;
  color: #64748b;
  font-size: 14px;
}

/* Destaca las cantidades del contador. */
.contador-resultados strong {
  color: #1e293b;
  font-weight: 600;
}

/* Contenedor que permite desplazar la tabla horizontalmente. */
.tabla-contenedor {
  overflow-x: auto;
  padding: 16px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

/* Formato de la tabla. */
table {
  width: 100%;
  min-width: 1100px;
  border-collapse: collapse;
}

th,
td {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
  font-size: 14px;
}

th {
  background: #f3f4f6;
  font-weight: 600;
}

/* Mensajes informativos y de estado. */
.mensaje,
.sin-registros {
  color: #6b7280;
  text-align: center;
  padding: 20px;
}

.error {
  color: #dc2626;
  padding: 12px;
  background: #fef2f2;
  border-radius: 6px;
}

.exito {
  color: #15803d;
  padding: 12px;
  background: #f0fdf4;
  border-radius: 6px;
}

/* Adaptamos los controles a pantallas pequeñas. */
@media (max-width: 700px) {
  .encabezado {
    align-items: flex-start;
    flex-direction: column;
  }

  .acciones {
    flex-wrap: wrap;
  }

  .campos {
    grid-template-columns: 1fr;
  }

  .campo-completo {
    grid-column: auto;
  }

  /* Los controles ocupan todo el ancho en pantallas pequeñas. */
  .busqueda-input,
  .filtro-tipo,
  .filtro-fecha {
    max-width: 100%;
    width: 100%;
  }

  .campo-fecha {
    width: 100%;
  }
}

</style>