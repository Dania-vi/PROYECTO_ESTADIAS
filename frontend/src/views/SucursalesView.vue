
<script setup lang="ts">
// Importamos las herramientas reactivas de Vue.
import { computed, onMounted, ref } from 'vue'

// Importamos las funciones para consultar, registrar, actualizar y eliminar.
import {
  obtenerDatos,
  enviarDatos,
  actualizarDatos,
  eliminarDatos,
} from '../services/api'

// Estructura de una sucursal recibida del backend.
interface Sucursal {
  id: number
  nombre: string
  direccion: string | null
  telefono: string | null
  activo: boolean
}

// Estructura de los datos que enviaremos al backend.
interface SucursalDatos {
  nombre: string
  direccion: string | null
  telefono: string | null
  activo: boolean
}

// Almacenamos las sucursales registradas.
const sucursales = ref<Sucursal[]>([])

// Calculamos los indicadores generales.
const totalSucursales = computed(() => sucursales.value.length)

const sucursalesActivas = computed(() =>
  sucursales.value.filter((sucursal) => sucursal.activo).length,
)

const sucursalesInactivas = computed(() =>
  sucursales.value.filter((sucursal) => !sucursal.activo).length,
)

// Controlamos los indicadores de carga y operaciones.
const cargando = ref(false)
const guardando = ref(false)
const eliminando = ref<number | null>(null)

// Guardamos los mensajes de error y confirmación.
const error = ref('')
const mensajeExito = ref('')

// Controlamos la visibilidad del formulario.
const mostrarFormulario = ref(false)

// Identificador de la sucursal que se está editando.
const sucursalEditando = ref<number | null>(null)

// Datos capturados en el formulario.
const formulario = ref({
  nombre: '',
  direccion: '',
  telefono: '',
  activo: true,
})

// Consultamos las sucursales registradas.
async function cargarSucursales() {
  try {
    cargando.value = true
    error.value = ''

    sucursales.value = await obtenerDatos<Sucursal[]>('/api/sucursales/')
  } catch (err) {
    error.value =
      err instanceof Error
        ? err.message
        : 'No fue posible cargar las sucursales.'

    console.error('Error al cargar sucursales:', err)
  } finally {
    cargando.value = false
  }
}

// Limpiamos los campos del formulario.
function limpiarFormulario() {
  formulario.value = {
    nombre: '',
    direccion: '',
    telefono: '',
    activo: true,
  }

  sucursalEditando.value = null
}

// Preparamos el formulario para registrar una sucursal.
function nuevaSucursal() {
  limpiarFormulario()
  mostrarFormulario.value = true
  error.value = ''
  mensajeExito.value = ''
}

// Cargamos los datos de una sucursal para editarla.
function editarSucursal(sucursal: Sucursal) {
  sucursalEditando.value = sucursal.id

  formulario.value = {
    nombre: sucursal.nombre,
    direccion: sucursal.direccion ?? '',
    telefono: sucursal.telefono ?? '',
    activo: sucursal.activo,
  }

  mostrarFormulario.value = true
  error.value = ''
  mensajeExito.value = ''
}

// Registra una sucursal o actualiza una existente.
async function guardarSucursal() {
  error.value = ''
  mensajeExito.value = ''

  // Validamos que el nombre no esté vacío.
  if (!formulario.value.nombre.trim()) {
    error.value = 'El nombre de la sucursal es obligatorio.'
    return
  }

  // Evitamos ejecutar operaciones simultáneas.
  if (guardando.value || eliminando.value !== null) return

  guardando.value = true

  try {
    // Preparamos los datos que enviaremos al backend.
    const datos: SucursalDatos = {
      nombre: formulario.value.nombre.trim(),
      direccion: formulario.value.direccion.trim() || null,
      telefono: formulario.value.telefono.trim() || null,
      activo: formulario.value.activo,
    }

    if (sucursalEditando.value !== null) {
      // Actualizamos la sucursal existente mediante PUT.
      await actualizarDatos<SucursalDatos, Sucursal>(
        `/api/sucursales/${sucursalEditando.value}`,
        datos,
      )

      mensajeExito.value = 'La sucursal se actualizó correctamente.'
    } else {
      // Registramos una sucursal nueva mediante POST.
      await enviarDatos<SucursalDatos, Sucursal>(
        '/api/sucursales/',
        datos,
      )

      mensajeExito.value = 'La sucursal se registró correctamente.'
    }

    // Cerramos y limpiamos el formulario.
    limpiarFormulario()
    mostrarFormulario.value = false

    // Actualizamos la tabla.
    await cargarSucursales()
  } catch (err) {
    error.value =
      err instanceof Error
        ? err.message
        : 'No fue posible guardar la sucursal.'
  } finally {
    guardando.value = false
  }
}

// Eliminamos una sucursal después de solicitar confirmación.
async function eliminarSucursal(sucursal: Sucursal) {
  if (eliminando.value !== null || guardando.value) return

  // Solicitamos confirmación antes de eliminar.
  const confirmar = window.confirm(
    `¿Deseas eliminar la sucursal "${sucursal.nombre}"? Si tiene equipos asociados, el sistema bloqueará la operación.`,
  )

  if (!confirmar) return

  eliminando.value = sucursal.id
  error.value = ''
  mensajeExito.value = ''

  try {
    // Enviamos la petición DELETE al backend.
    await eliminarDatos<{ mensaje: string; id: number }>(
      `/api/sucursales/${sucursal.id}`,
    )

    // Cerramos el formulario si se estaba editando esta sucursal.
    if (sucursalEditando.value === sucursal.id) {
      limpiarFormulario()
      mostrarFormulario.value = false
    }

    mensajeExito.value = `La sucursal "${sucursal.nombre}" se eliminó correctamente.`

    // Actualizamos la información de la tabla.
    await cargarSucursales()
  } catch (err) {
    error.value =
      err instanceof Error
        ? err.message
        : 'No fue posible eliminar la sucursal.'
  } finally {
    eliminando.value = null
  }
}

// Consultamos las sucursales al abrir la pantalla.
onMounted(() => {
  cargarSucursales()
})
</script>

<template>
  <section class="sucursales-view">

    <!-- Encabezado de la pantalla. -->
    <div class="page-header">
      <div>
        <h1>Sucursales</h1>
        <p>Consulta y administra las sucursales registradas en el sistema.</p>
      </div>

      <!-- Botones para registrar y actualizar. -->
      <div class="header-actions">
        <button
          class="new-button"
          @click="nuevaSucursal"
          :disabled="guardando || eliminando !== null"
        >
          + Nueva sucursal
        </button>

        <button
          class="refresh-button"
          @click="cargarSucursales"
          :disabled="cargando"
        >
          {{ cargando ? 'Actualizando...' : 'Actualizar' }}
        </button>
      </div>
    </div>

    <!-- Formulario para registrar o editar una sucursal. -->
    <section v-if="mostrarFormulario" class="formulario-contenedor">
      <h2>
        {{ sucursalEditando !== null ? 'Editar sucursal' : 'Registrar nueva sucursal' }}
      </h2>

      <p class="ayuda-formulario">
        Ingresa la información de la sucursal. El nombre es obligatorio.
      </p>

      <form @submit.prevent="guardarSucursal">
        <div class="campos">

          <div class="campo">
            <label for="nombre-sucursal">Nombre de la sucursal *</label>
            <input
              id="nombre-sucursal"
              v-model="formulario.nombre"
              type="text"
              maxlength="100"
              placeholder="Ej. Sucursal Norte"
              required
            />
          </div>

          <div class="campo">
            <label for="telefono-sucursal">Teléfono</label>
            <input
              id="telefono-sucursal"
              v-model="formulario.telefono"
              type="text"
              maxlength="20"
              placeholder="Ej. 4491234567"
            />
          </div>

          <div class="campo campo-completo">
            <label for="direccion-sucursal">Dirección</label>
            <input
              id="direccion-sucursal"
              v-model="formulario.direccion"
              type="text"
              placeholder="Dirección de la sucursal"
            />
          </div>

          <div class="campo campo-completo">
            <label for="estado-sucursal">Estado</label>
            <select
              id="estado-sucursal"
              v-model="formulario.activo"
            >
              <option :value="true">Activa</option>
              <option :value="false">Inactiva</option>
            </select>
          </div>

        </div>

        <!-- Botones para cancelar o guardar. -->
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
                : sucursalEditando !== null
                  ? 'Guardar cambios'
                  : 'Registrar sucursal'
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

    <!-- Indicador de carga. -->
    <div v-if="cargando" class="message">
      Cargando sucursales...
    </div>

    <template v-else>

      <!-- Indicadores generales. -->
      <div class="summary-grid">
        <div class="summary-card">
          <span class="summary-label">Total de sucursales</span>
          <strong>{{ totalSucursales }}</strong>
        </div>

        <div class="summary-card">
          <span class="summary-label">Sucursales activas</span>
          <strong class="active-number">{{ sucursalesActivas }}</strong>
        </div>

        <div class="summary-card">
          <span class="summary-label">Sucursales inactivas</span>
          <strong class="inactive-number">{{ sucursalesInactivas }}</strong>
        </div>
      </div>

      <!-- Mensaje cuando no existen registros. -->
      <div v-if="sucursales.length === 0" class="message">
        No hay sucursales registradas.
      </div>

      <!-- Tabla de sucursales. -->
      <div v-else class="table-container">
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Dirección</th>
              <th>Teléfono</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="sucursal in sucursales" :key="sucursal.id">
              <td>{{ sucursal.nombre }}</td>
              <td>{{ sucursal.direccion || 'Sin registro' }}</td>
              <td>{{ sucursal.telefono || 'Sin registro' }}</td>

              <td>
                <span
                  class="estado-badge"
                  :class="sucursal.activo ? 'estado-activo' : 'estado-inactivo'"
                >
                  {{ sucursal.activo ? 'Activa' : 'Inactiva' }}
                </span>
              </td>

              <!-- Acciones disponibles. -->
              <td>
                <button
                  class="edit-button"
                  @click="editarSucursal(sucursal)"
                  :disabled="eliminando !== null || guardando"
                >
                  Editar
                </button>

                <button
                  class="delete-button"
                  @click="eliminarSucursal(sucursal)"
                  :disabled="eliminando !== null || guardando"
                >
                  {{
                    eliminando === sucursal.id
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
.sucursales-view {
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

/* Botones principales. */
.new-button,
.save-button,
.refresh-button {
  background-color: #2563eb;
}

.new-button:hover:not(:disabled),
.save-button:hover:not(:disabled),
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

.campo {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.campo-completo {
  grid-column: 1 / -1;
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

.cancel-button {
  background-color: #6b7280;
}

.cancel-button:hover:not(:disabled) {
  background-color: #4b5563;
}

/* Tarjetas de resumen. */
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

.summary-label {
  color: #64748b;
  font-size: 14px;
}

.summary-card strong {
  color: #1e293b;
  font-size: 28px;
}

.summary-card .active-number {
  color: #16a34a;
}

.summary-card .inactive-number {
  color: #dc2626;
}

/* Etiquetas visuales de estado. */
.estado-badge {
  display: inline-block;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.estado-activo {
  color: #15803d;
  background-color: #dcfce7;
}

.estado-inactivo {
  color: #b91c1c;
  background-color: #fee2e2;
}

/* Contenedor de la tabla. */
.table-container {
  overflow-x: auto;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

table {
  width: 100%;
  min-width: 850px;
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

/* Botón para editar. */
.edit-button {
  padding: 8px 12px;
  background-color: #d97706;
}

.edit-button:hover:not(:disabled) {
  background-color: #b45309;
}

/* Botón para eliminar. */
.delete-button {
  margin-left: 6px;
  padding: 8px 12px;
  background-color: #dc2626;
}

.delete-button:hover:not(:disabled) {
  background-color: #b91c1c;
}

/* Adaptación para pantallas pequeñas. */
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

  .campo-completo {
    grid-column: auto;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
