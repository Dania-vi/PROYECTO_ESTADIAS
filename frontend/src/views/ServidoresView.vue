
<script setup lang="ts">
// Importamos las herramientas reactivas de Vue.
import { computed, onMounted, ref } from 'vue'

// Importamos las funciones para consultar, registrar, actualizar y eliminar servidores.
import {
  obtenerDatos,
  enviarDatos,
  actualizarDatos,
  eliminarDatos,
} from '../services/api'

// Importamos el componente que muestra visualmente el estado del servidor.
import EstadoBadge from '../components/ui/EstadoBadge.vue'

// Definimos la estructura de cada servidor recibido del backend.
interface Servidor {
  id: number
  nombre_host: string
  direccion_ip: string | null
  sistema_operativo: string | null
  estado_actual: string | null
  ultima_conexion: string | null
}

// Definimos la estructura de los datos que enviaremos al backend.
interface ServidorDatos {
  nombre_host: string
  direccion_ip: string | null
  sistema_operativo: string | null
  estado_actual: string | null
}

// Guardamos los servidores recibidos desde la base de datos.
const servidores = ref<Servidor[]>([])

// Calculamos la cantidad total de servidores registrados.
const totalServidores = computed(() => servidores.value.length)

// Normalizamos los estados para evitar diferencias entre mayúsculas y minúsculas.
function estadoNormalizado(estado: string | null): string {
  return (estado ?? '').trim().toLowerCase()
}

// Calculamos cuántos servidores están activos.
const servidoresActivos = computed(() =>
  servidores.value.filter(
    (servidor) => estadoNormalizado(servidor.estado_actual) === 'activo',
  ).length,
)

// Calculamos cuántos servidores están inactivos.
const servidoresInactivos = computed(() =>
  servidores.value.filter(
    (servidor) => estadoNormalizado(servidor.estado_actual) === 'inactivo',
  ).length,
)

// Calculamos los servidores que tienen otro estado o no tienen uno asignado.
const servidoresOtros = computed(() =>
  servidores.value.filter((servidor) => {
    const estado = estadoNormalizado(servidor.estado_actual)
    return estado !== 'activo' && estado !== 'inactivo'
  }).length,
)

// Controlamos los indicadores de carga y las operaciones.
const cargando = ref(false)
const guardando = ref(false)
const eliminando = ref<number | null>(null)

// Guardamos los mensajes de error y confirmación.
const error = ref('')
const mensajeExito = ref('')

// Controlamos la visibilidad del formulario.
const mostrarFormulario = ref(false)

// Guardamos el identificador del servidor que estamos editando.
const servidorEditando = ref<number | null>(null)

// Almacenamos los datos capturados en el formulario.
const formulario = ref({
  nombre_host: '',
  direccion_ip: '',
  sistema_operativo: '',
  estado_actual: 'Activo',
})

// Consultamos los servidores registrados en el backend.
async function cargarServidores() {
  try {
    // Activamos el indicador de carga.
    cargando.value = true

    // Limpiamos los errores anteriores.
    error.value = ''

    // Solicitamos los servidores al backend.
    servidores.value = await obtenerDatos<Servidor[]>('/api/servidores/')
  } catch (err) {
    // Mostramos un mensaje si ocurre algún problema.
    error.value =
      err instanceof Error
        ? err.message
        : 'No fue posible cargar los servidores.'

    console.error('Error al cargar servidores:', err)
  } finally {
    // Finalizamos el indicador de carga.
    cargando.value = false
  }
}

// Formateamos la fecha de la última conexión.
function formatearFecha(fecha: string | null): string {
  // Si no existe una fecha, mostramos un mensaje.
  if (!fecha) return 'Sin registro'

  // Convertimos la fecha a un formato legible.
  const fechaObjeto = new Date(fecha)

  // Si la fecha no es válida, mostramos el valor recibido.
  if (Number.isNaN(fechaObjeto.getTime())) return fecha

  // Mostramos la fecha con el formato utilizado en México.
  return fechaObjeto.toLocaleString('es-MX')
}

// Limpiamos los campos del formulario.
function limpiarFormulario() {
  formulario.value = {
    nombre_host: '',
    direccion_ip: '',
    sistema_operativo: '',
    estado_actual: 'Activo',
  }

  // Indicamos que ya no estamos editando un servidor.
  servidorEditando.value = null
}

// Preparamos el formulario para registrar un servidor nuevo.
function nuevoServidor() {
  // Limpiamos los campos anteriores.
  limpiarFormulario()

  // Mostramos el formulario.
  mostrarFormulario.value = true

  // Limpiamos los mensajes anteriores.
  error.value = ''
  mensajeExito.value = ''
}

// Cargamos los datos del servidor seleccionado para editarlo.
function editarServidor(servidor: Servidor) {
  // Guardamos el identificador del servidor seleccionado.
  servidorEditando.value = servidor.id

  // Colocamos sus datos actuales en el formulario.
  formulario.value = {
    nombre_host: servidor.nombre_host,
    direccion_ip: servidor.direccion_ip ?? '',
    sistema_operativo: servidor.sistema_operativo ?? '',
    estado_actual: servidor.estado_actual ?? 'Activo',
  }

  // Mostramos el formulario.
  mostrarFormulario.value = true

  // Limpiamos los mensajes anteriores.
  error.value = ''
  mensajeExito.value = ''
}

// Registra un servidor nuevo o actualiza uno existente.
async function guardarServidor() {
  // Limpiamos los mensajes anteriores.
  error.value = ''
  mensajeExito.value = ''

  // Verificamos que el nombre del servidor no esté vacío.
  if (!formulario.value.nombre_host.trim()) {
    error.value = 'El nombre del servidor es obligatorio.'
    return
  }

  // Evitamos guardar información mientras otra operación está en proceso.
  if (guardando.value) return

  // Activamos el indicador de guardado.
  guardando.value = true

  try {
    // Preparamos los datos que enviaremos al backend.
    const datos: ServidorDatos = {
      nombre_host: formulario.value.nombre_host.trim(),
      direccion_ip: formulario.value.direccion_ip.trim() || null,
      sistema_operativo: formulario.value.sistema_operativo.trim() || null,
      estado_actual: formulario.value.estado_actual.trim() || null,
    }

    // Comprobamos si estamos editando un servidor existente.
    if (servidorEditando.value !== null) {
      // Enviamos los cambios mediante una petición PUT.
      await actualizarDatos<ServidorDatos, Servidor>(
        `/api/servidores/${servidorEditando.value}`,
        datos,
      )

      // Mostramos un mensaje de confirmación.
      mensajeExito.value = 'El servidor se actualizó correctamente.'
    } else {
      // Registramos un servidor nuevo mediante una petición POST.
      await enviarDatos<ServidorDatos, Servidor>(
        '/api/servidores/',
        datos,
      )

      // Mostramos un mensaje de confirmación.
      mensajeExito.value = 'El servidor se registró correctamente.'
    }

    // Limpiamos el formulario y lo ocultamos.
    limpiarFormulario()
    mostrarFormulario.value = false

    // Actualizamos la tabla con los datos del backend.
    await cargarServidores()
  } catch (err) {
    // Mostramos el error recibido del backend.
    error.value =
      err instanceof Error
        ? err.message
        : 'No fue posible guardar el servidor.'
  } finally {
    // Finalizamos el indicador de guardado.
    guardando.value = false
  }
}

// Eliminamos un servidor después de solicitar confirmación.
async function eliminarServidor(servidor: Servidor) {
  // Evitamos iniciar otra eliminación mientras exista una en proceso.
  if (eliminando.value !== null) return

  // Solicitamos confirmación antes de eliminar el registro.
  const confirmar = window.confirm(
    `¿Estás segura de que deseas eliminar el servidor "${servidor.nombre_host}"? Esta acción no se puede deshacer.`,
  )

  // Si el usuario cancela, detenemos la operación.
  if (!confirmar) return

  // Guardamos el identificador del servidor que se está eliminando.
  eliminando.value = servidor.id

  // Limpiamos los mensajes anteriores.
  error.value = ''
  mensajeExito.value = ''

  try {
    // Enviamos la petición DELETE al backend.
    await eliminarDatos<{ mensaje: string; id: number }>(
      `/api/servidores/${servidor.id}`,
    )

    // Si el servidor eliminado estaba abierto para edición,
    // cerramos el formulario y limpiamos sus campos.
    if (servidorEditando.value === servidor.id) {
      limpiarFormulario()
      mostrarFormulario.value = false
    }

    // Mostramos un mensaje de confirmación.
    mensajeExito.value = `El servidor "${servidor.nombre_host}" se eliminó correctamente.`

    // Actualizamos la tabla para retirar el registro eliminado.
    await cargarServidores()
  } catch (err) {
    // Mostramos el error si no fue posible eliminar el servidor.
    error.value =
      err instanceof Error
        ? err.message
        : 'No fue posible eliminar el servidor.'
  } finally {
    // Liberamos el control de eliminación.
    eliminando.value = null
  }
}

// Consultamos los servidores cuando se abre esta pantalla.
onMounted(() => {
  cargarServidores()
})
</script>

<template>
  <section class="servidores-view">

    <!-- Encabezado de la pantalla. -->
    <div class="page-header">
      <div>
        <h1>Servidores</h1>
        <p>Consulta y administra los servidores registrados en el sistema.</p>
      </div>

      <!-- Botones para registrar y actualizar servidores. -->
      <div class="header-actions">
        <button
          class="new-button"
          @click="nuevoServidor"
          :disabled="guardando || eliminando !== null"
        >
          + Nuevo servidor
        </button>

        <button
          class="refresh-button"
          :disabled="cargando"
          @click="cargarServidores"
        >
          {{ cargando ? 'Actualizando...' : 'Actualizar' }}
        </button>
      </div>
    </div>

    <!-- Formulario para registrar o editar un servidor. -->
    <section v-if="mostrarFormulario" class="formulario-contenedor">

      <!-- El título cambia según la operación. -->
      <h2>
        {{ servidorEditando !== null ? 'Editar servidor' : 'Registrar nuevo servidor' }}
      </h2>

      <p class="ayuda-formulario">
        Ingresa los datos del servidor. El nombre del host es obligatorio.
      </p>

      <form @submit.prevent="guardarServidor">
        <div class="campos">

          <!-- Campo para el nombre del servidor. -->
          <div class="campo">
            <label for="nombre-host">Nombre del servidor *</label>
            <input
              id="nombre-host"
              v-model="formulario.nombre_host"
              type="text"
              maxlength="80"
              placeholder="Ej. SERVIDOR-PRINCIPAL"
              required
            />
          </div>

          <!-- Campo para la dirección IP. -->
          <div class="campo">
            <label for="direccion-ip">Dirección IP</label>
            <input
              id="direccion-ip"
              v-model="formulario.direccion_ip"
              type="text"
              maxlength="45"
              placeholder="Ej. 192.168.1.100"
            />
          </div>

          <!-- Campo para el sistema operativo. -->
          <div class="campo">
            <label for="sistema-operativo">Sistema operativo</label>
            <input
              id="sistema-operativo"
              v-model="formulario.sistema_operativo"
              type="text"
              maxlength="80"
              placeholder="Ej. Windows Server 2022"
            />
          </div>

          <!-- Selector para el estado actual. -->
          <div class="campo">
            <label for="estado-actual">Estado</label>
            <select
              id="estado-actual"
              v-model="formulario.estado_actual"
            >
              <option value="Activo">Activo</option>
              <option value="Inactivo">Inactivo</option>
              <option value="Mantenimiento">Mantenimiento</option>
            </select>
          </div>

        </div>

        <!-- Botones para cancelar o guardar los datos. -->
        <div class="botones-formulario">
          <button
            type="button"
            class="cancel-button"
            @click="mostrarFormulario = false; limpiarFormulario()"
            :disabled="guardando"
          >
            Cancelar
          </button>

          <button
            type="submit"
            class="save-button"
            :disabled="guardando"
          >
            {{
              guardando
                ? 'Guardando...'
                : servidorEditando !== null
                  ? 'Guardar cambios'
                  : 'Registrar servidor'
            }}
          </button>
        </div>
      </form>
    </section>

    <!-- Mensaje de confirmación. -->
    <p v-if="mensajeExito" class="success-message" role="status">
      {{ mensajeExito }}
    </p>

    <!-- Mensaje cuando ocurre un error. -->
    <div v-if="error" class="message error" role="alert">
      {{ error }}
    </div>

    <!-- Mensaje mientras se consultan los datos. -->
    <div v-if="cargando" class="message">
      Cargando servidores...
    </div>

    <!-- Contenido cuando la consulta termina correctamente. -->
    <template v-else>

      <!-- Indicadores generales de los servidores. -->
      <div class="summary-grid">

        <!-- Total de servidores registrados. -->
        <div class="summary-card">
          <span class="summary-label">Total de servidores</span>
          <strong>{{ totalServidores }}</strong>
        </div>

        <!-- Servidores que aparecen como activos. -->
        <div class="summary-card">
          <span class="summary-label">Servidores activos</span>
          <strong class="active-number">{{ servidoresActivos }}</strong>
        </div>

        <!-- Servidores que aparecen como inactivos. -->
        <div class="summary-card">
          <span class="summary-label">Servidores inactivos</span>
          <strong class="inactive-number">{{ servidoresInactivos }}</strong>
        </div>

        <!-- Servidores con otros estados. -->
        <div v-if="servidoresOtros > 0" class="summary-card">
          <span class="summary-label">Otros estados</span>
          <strong>{{ servidoresOtros }}</strong>
        </div>

      </div>

      <!-- Mensaje cuando no existen servidores registrados. -->
      <div v-if="servidores.length === 0" class="message">
        No hay servidores registrados.
      </div>

      <!-- Tabla con los servidores recibidos del backend. -->
      <div v-else class="table-container">
        <table>
          <thead>
            <tr>
              <th>Nombre del servidor</th>
              <th>Dirección IP</th>
              <th>Sistema operativo</th>
              <th>Estado</th>
              <th>Última conexión</th>
              <th>Acciones</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="servidor in servidores" :key="servidor.id">
              <td>{{ servidor.nombre_host }}</td>
              <td>{{ servidor.direccion_ip || 'Sin registro' }}</td>
              <td>{{ servidor.sistema_operativo || 'Sin registro' }}</td>

              <td>
                <EstadoBadge :estado="servidor.estado_actual" />
              </td>

              <td>{{ formatearFecha(servidor.ultima_conexion) }}</td>

              <!-- Acciones disponibles para cada servidor. -->
              <td>
                <!-- Botón para editar el servidor. -->
                <button
                  class="edit-button"
                  @click="editarServidor(servidor)"
                  :disabled="eliminando !== null || guardando"
                >
                  Editar
                </button>

                <!-- Botón para eliminar el servidor. -->
                <button
                  class="delete-button"
                  @click="eliminarServidor(servidor)"
                  :disabled="eliminando !== null || guardando"
                >
                  {{
                    eliminando === servidor.id
                      ? 'Eliminando...'
                      : 'Eliminar'
                  }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </template>
  </section>
</template>

<style scoped>
/* Contenedor principal de la pantalla. */
.servidores-view {
  padding: 25px;
}

/* Encabezado y botones de acciones. */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
}

.page-header h1 {
  margin: 0 0 8px;
  color: #1e293b;
  font-size: 25px;
}

.page-header p {
  margin: 0;
  color: #64748b;
}

/* Distribución de los botones del encabezado. */
.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* Estilos generales de los botones. */
button {
  padding: 10px 18px;
  border: none;
  border-radius: 7px;
  color: white;
  cursor: pointer;
  font: inherit;
}

button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

/* Botón para registrar un servidor. */
.new-button,
.save-button {
  background-color: #2563eb;
}

.new-button:hover:not(:disabled),
.save-button:hover:not(:disabled) {
  background-color: #1d4ed8;
}

/* Botón para actualizar la información. */
.refresh-button {
  background-color: #2563eb;
}

.refresh-button:hover:not(:disabled) {
  background-color: #1d4ed8;
}

/* Mensajes de carga, error o ausencia de registros. */
.message {
  padding: 25px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  color: #64748b;
  text-align: center;
}

.error {
  margin-bottom: 15px;
  color: #991b1b;
  background-color: #fef2f2;
  border-color: #fecaca;
}

/* Mensaje de operación exitosa. */
.success-message {
  margin-bottom: 18px;
  padding: 12px;
  color: #15803d;
  background-color: #f0fdf4;
  border-radius: 7px;
}

/* Contenedor del formulario. */
.formulario-contenedor {
  margin-bottom: 24px;
  padding: 24px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

.formulario-contenedor h2 {
  margin-top: 0;
  margin-bottom: 8px;
  color: #1e293b;
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

/* Organización de cada campo. */
.campo {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.campo label {
  color: #334155;
  font-size: 14px;
  font-weight: 600;
}

/* Apariencia de los campos de entrada y selectores. */
.campo input,
.campo select {
  width: 100%;
  box-sizing: border-box;
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: white;
  color: #1f2937;
  font: inherit;
}

.campo input:focus,
.campo select:focus {
  border-color: #2563eb;
  outline: none;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12);
}

/* Botones ubicados al final del formulario. */
.botones-formulario {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 22px;
}

/* Botón para cancelar el formulario. */
.cancel-button {
  background-color: #6b7280;
}

.cancel-button:hover:not(:disabled) {
  background-color: #4b5563;
}

/* Diseño de las tarjetas de resumen. */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 18px;
  margin-bottom: 25px;
}

.summary-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

/* Texto descriptivo de cada indicador. */
.summary-label {
  color: #64748b;
  font-size: 14px;
}

/* Número principal de cada tarjeta. */
.summary-card strong {
  color: #1e293b;
  font-size: 28px;
}

/* Color para servidores activos. */
.summary-card .active-number {
  color: #16a34a;
}

/* Color para servidores inactivos. */
.summary-card .inactive-number {
  color: #dc2626;
}

/* Contenedor que permite desplazar la tabla en pantallas pequeñas. */
.table-container {
  overflow-x: auto;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

/* Estilos generales de la tabla. */
table {
  width: 100%;
  min-width: 950px;
  border-collapse: collapse;
  text-align: left;
}

th,
td {
  padding: 15px;
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
}

th {
  background-color: #f8fafc;
  color: #475569;
  font-size: 13px;
}

td {
  color: #334155;
  font-size: 14px;
}

/* Botón para editar un servidor. */
.edit-button {
  padding: 8px 12px;
  background-color: #d97706;
}

.edit-button:hover:not(:disabled) {
  background-color: #b45309;
}

/* Botón para eliminar un servidor. */
.delete-button {
  margin-left: 6px;
  padding: 8px 12px;
  background-color: #dc2626;
}

.delete-button:hover:not(:disabled) {
  background-color: #b91c1c;
}

/* Adaptación de los elementos para pantallas pequeñas. */
@media (max-width: 700px) {
  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
  }

  .campos {
    grid-template-columns: 1fr;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
