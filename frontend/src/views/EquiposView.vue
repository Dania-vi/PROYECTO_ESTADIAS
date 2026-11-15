
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import {
  obtenerDatos,
  enviarDatos,
  actualizarDatos,
  eliminarDatos
} from '../services/api'

// Estructura de los equipos recibidos desde el backend.
interface Equipo {
  id: number
  sucursal_id: number
  nombre: string
  tipo_equipo: string | null
  marca: string | null
  modelo: string | null
  numero_serie: string | null
  estado: string | null
}

// Estructura de las sucursales para el selector del formulario.
interface Sucursal {
  id: number
  nombre: string
  activo: boolean
}

// Datos que se enviarán al backend al crear o editar un equipo.
interface EquipoDatos {
  sucursal_id: number
  nombre: string
  tipo_equipo: string | null
  marca: string | null
  modelo: string | null
  numero_serie: string | null
  estado: string
}

// Listas principales.
const equipos = ref<Equipo[]>([])
const sucursales = ref<Sucursal[]>([])

// Estados de la pantalla.
const cargando = ref(false)
const guardando = ref(false)
const editando = ref(false)
const equipoIdActual = ref<number | null>(null)

// Guarda el ID del equipo que se está eliminando.
// Permite evitar solicitudes de eliminación duplicadas.
const eliminandoId = ref<number | null>(null)

// Mensajes para informar el resultado de las operaciones.
const mensajeExito = ref('')
const mensajeError = ref('')

// Formulario.
const formulario = ref<EquipoDatos>({
  sucursal_id: 0,
  nombre: '',
  tipo_equipo: '',
  marca: '',
  modelo: '',
  numero_serie: '',
  estado: 'Activo'
})

// Contadores para las tarjetas de resumen.
const totalEquipos = computed(() => equipos.value.length)

const equiposActivos = computed(() =>
  equipos.value.filter(equipo =>
    (equipo.estado || '').toLowerCase() === 'activo'
  ).length
)

const equiposInactivos = computed(() =>
  equipos.value.filter(equipo =>
    (equipo.estado || '').toLowerCase() !== 'activo'
  ).length
)

// Obtiene el nombre de una sucursal a partir de su identificador.
function obtenerNombreSucursal(sucursalId: number): string {
  const sucursal = sucursales.value.find(
    item => item.id === sucursalId
  )

  return sucursal?.nombre || 'Sucursal no encontrada'
}

// Consulta los equipos registrados.
async function cargarEquipos() {
  cargando.value = true
  mensajeError.value = ''

  try {
    equipos.value = await obtenerDatos<Equipo[]>('/api/equipos/')
  } catch (error) {
    mensajeError.value =
      error instanceof Error
        ? error.message
        : 'No se pudieron cargar los equipos.'
  } finally {
    cargando.value = false
  }
}

// Consulta las sucursales disponibles para relacionarlas con los equipos.
async function cargarSucursales() {
  try {
    sucursales.value = await obtenerDatos<Sucursal[]>('/api/sucursales/')
  } catch (error) {
    mensajeError.value =
      error instanceof Error
        ? error.message
        : 'No se pudieron cargar las sucursales.'
  }
}

// Limpia el formulario y lo prepara para registrar un equipo nuevo.
function limpiarFormulario() {
  formulario.value = {
    sucursal_id: sucursales.value[0]?.id || 0,
    nombre: '',
    tipo_equipo: '',
    marca: '',
    modelo: '',
    numero_serie: '',
    estado: 'Activo'
  }

  editando.value = false
  equipoIdActual.value = null
}

// Carga los datos de un equipo seleccionado en el formulario.
function seleccionarEquipo(equipo: Equipo) {
  formulario.value = {
    sucursal_id: equipo.sucursal_id,
    nombre: equipo.nombre,
    tipo_equipo: equipo.tipo_equipo || '',
    marca: equipo.marca || '',
    modelo: equipo.modelo || '',
    numero_serie: equipo.numero_serie || '',
    estado: equipo.estado || 'Activo'
  }

  equipoIdActual.value = equipo.id
  editando.value = true
  mensajeExito.value = ''
  mensajeError.value = ''

  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Registra un equipo nuevo o actualiza uno existente.
async function guardarEquipo() {
  mensajeExito.value = ''
  mensajeError.value = ''

  // Verifica que los campos indispensables estén completos.
  if (!formulario.value.nombre.trim()) {
    mensajeError.value = 'El nombre del equipo es obligatorio.'
    return
  }

  if (!formulario.value.sucursal_id) {
    mensajeError.value = 'Debes seleccionar una sucursal.'
    return
  }

  // Prepara los datos y convierte los campos vacíos en valores nulos.
  const datos: EquipoDatos = {
    sucursal_id: formulario.value.sucursal_id,
    nombre: formulario.value.nombre.trim(),
    tipo_equipo: formulario.value.tipo_equipo?.trim() || null,
    marca: formulario.value.marca?.trim() || null,
    modelo: formulario.value.modelo?.trim() || null,
    numero_serie: formulario.value.numero_serie?.trim() || null,
    estado: formulario.value.estado
  }

  guardando.value = true

  try {
    if (editando.value && equipoIdActual.value !== null) {
      // Actualiza el equipo seleccionado.
      await actualizarDatos(
        `/api/equipos/${equipoIdActual.value}`,
        datos
      )

      mensajeExito.value = 'Equipo actualizado correctamente.'
    } else {
      // Registra un equipo nuevo.
      await enviarDatos('/api/equipos/', datos)

      mensajeExito.value = 'Equipo registrado correctamente.'
    }

    limpiarFormulario()
    await cargarEquipos()
  } catch (error) {
    mensajeError.value =
      error instanceof Error
        ? error.message
        : 'No se pudo guardar la información del equipo.'
  } finally {
    guardando.value = false
  }
}

// Elimina un equipo. El backend impedirá hacerlo si tiene
// mantenimientos o respaldos relacionados.
async function eliminarEquipo(equipo: Equipo) {

  // Evitamos iniciar otra eliminación mientras exista una en curso.
  if (eliminandoId.value !== null) return

  // Solicitamos confirmación antes de eliminar.
  const confirmar = window.confirm(
    `¿Estás seguro de eliminar el equipo "${equipo.nombre}"?`
  )

  if (!confirmar) return

  // Limpiamos los mensajes anteriores.
  mensajeExito.value = ''
  mensajeError.value = ''

  // Guardamos el ID del equipo que se está eliminando.
  eliminandoId.value = equipo.id

  try {
    // Enviamos la solicitud de eliminación al backend.
    await eliminarDatos(`/api/equipos/${equipo.id}`)

    mensajeExito.value = 'Equipo eliminado correctamente.'

    // Actualizamos la lista de equipos.
    await cargarEquipos()

    // Si se estaba editando el equipo eliminado, limpiamos el formulario.
    if (equipoIdActual.value === equipo.id) {
      limpiarFormulario()
    }

  } catch (error) {
    // Mostramos el error recibido.
    mensajeError.value =
      error instanceof Error
        ? error.message
        : 'No se pudo eliminar el equipo.'

  } finally {
    // Liberamos el control para permitir futuras eliminaciones.
    eliminandoId.value = null
  }
}

// Carga inicial de información.
onMounted(async () => {
  await cargarSucursales()
  await cargarEquipos()
})
</script>

<template>
  <div class="equipos-view">

    <!-- Encabezado de la sección. -->
    <div class="page-header">
      <div>
        <h1>Gestión de equipos</h1>
        <p>Administra los equipos registrados en las sucursales.</p>
      </div>

      <div class="header-actions">
        <button class="btn-secondary" @click="cargarEquipos">
          Actualizar
        </button>

        <button class="btn-primary" @click="limpiarFormulario">
          + Nuevo equipo
        </button>
      </div>
    </div>

    <!-- Formulario para registrar o editar equipos. -->
    <section class="formulario-contenedor">
      <div class="formulario-header">
        <h2>{{ editando ? 'Editar equipo' : 'Registrar equipo' }}</h2>
        <span class="formulario-descripcion">
          Completa la información del equipo.
        </span>
      </div>

      <form @submit.prevent="guardarEquipo">
        <div class="campos">

          <div class="campo">
            <label for="nombre">Nombre del equipo *</label>
            <input
              id="nombre"
              v-model="formulario.nombre"
              type="text"
              placeholder="Ej. Caja registradora 01"
              maxlength="80"
              required
            />
          </div>

          <div class="campo">
            <label for="sucursal">Sucursal *</label>
            <select
              id="sucursal"
              v-model.number="formulario.sucursal_id"
              required
            >
              <option :value="0" disabled>
                Selecciona una sucursal
              </option>

              <option
                v-for="sucursal in sucursales"
                :key="sucursal.id"
                :value="sucursal.id"
                :disabled="!sucursal.activo"
              >
                {{ sucursal.nombre }}
                {{ !sucursal.activo ? '(Inactiva)' : '' }}
              </option>
            </select>
          </div>

          <div class="campo">
            <label for="tipo">Tipo de equipo</label>
            <input
              id="tipo"
              v-model="formulario.tipo_equipo"
              type="text"
              placeholder="Ej. Caja registradora"
              maxlength="50"
            />
          </div>

          <div class="campo">
            <label for="marca">Marca</label>
            <input
              id="marca"
              v-model="formulario.marca"
              type="text"
              placeholder="Ej. HP"
              maxlength="50"
            />
          </div>

          <div class="campo">
            <label for="modelo">Modelo</label>
            <input
              id="modelo"
              v-model="formulario.modelo"
              type="text"
              placeholder="Ej. ProDesk"
              maxlength="50"
            />
          </div>

          <div class="campo">
            <label for="serie">Número de serie</label>
            <input
              id="serie"
              v-model="formulario.numero_serie"
              type="text"
              placeholder="Número de serie del equipo"
              maxlength="80"
            />
          </div>

          <div class="campo">
            <label for="estado">Estado</label>
            <select id="estado" v-model="formulario.estado">
              <option value="Activo">Activo</option>
              <option value="Inactivo">Inactivo</option>
              <option value="En mantenimiento">En mantenimiento</option>
            </select>
          </div>

        </div>

        <div class="formulario-acciones">
          <button
            v-if="editando"
            type="button"
            class="btn-secondary"
            @click="limpiarFormulario"
          >
            Cancelar edición
          </button>

          <button
            type="submit"
            class="btn-primary"
            :disabled="guardando"
          >
            {{
              guardando
                ? 'Guardando...'
                : editando
                  ? 'Guardar cambios'
                  : 'Registrar equipo'
            }}
          </button>
        </div>
      </form>
    </section>

    <!-- Mensajes de resultado de las operaciones. -->
    <div v-if="mensajeExito" class="mensaje mensaje-exito">
      {{ mensajeExito }}
    </div>

    <div v-if="mensajeError" class="mensaje mensaje-error">
      {{ mensajeError }}
    </div>

    <!-- Tarjetas con el resumen de equipos. -->
    <section class="summary-grid">
      <div class="summary-card">
        <span class="summary-label">Total de equipos</span>
        <strong>{{ totalEquipos }}</strong>
      </div>

      <div class="summary-card">
        <span class="summary-label">Equipos activos</span>
        <strong class="texto-activo">{{ equiposActivos }}</strong>
      </div>

      <div class="summary-card">
        <span class="summary-label">Otros estados</span>
        <strong class="texto-inactivo">{{ equiposInactivos }}</strong>
      </div>
    </section>

    <!-- Tabla de equipos registrados. -->
    <section class="tabla-contenedor">
      <div class="tabla-header">
        <div>
          <h2>Equipos registrados</h2>
          <p>Consulta y administra los equipos de cada sucursal.</p>
        </div>
      </div>

      <div v-if="cargando" class="estado-carga">
        Cargando equipos...
      </div>

      <div v-else-if="equipos.length === 0" class="estado-vacio">
        No hay equipos registrados.
      </div>

      <div v-else class="table-container">
        <table>
          <thead>
            <tr>
              <th>Equipo</th>
              <th>Sucursal</th>
              <th>Tipo</th>
              <th>Marca / Modelo</th>
              <th>Número de serie</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="equipo in equipos" :key="equipo.id">
              <td>
                <strong>{{ equipo.nombre }}</strong>
              </td>

              <td>{{ obtenerNombreSucursal(equipo.sucursal_id) }}</td>

              <td>{{ equipo.tipo_equipo || '—' }}</td>

              <td>
                {{ equipo.marca || '—' }}
                <span v-if="equipo.modelo">
                  / {{ equipo.modelo }}
                </span>
              </td>

              <td>{{ equipo.numero_serie || '—' }}</td>

              <td>
                <span
                  class="estado-badge"
                  :class="{
                    'estado-activo':
                      (equipo.estado || '').toLowerCase() === 'activo',
                    'estado-inactivo':
                      (equipo.estado || '').toLowerCase() !== 'activo'
                  }"
                >
                  {{ equipo.estado || 'Sin estado' }}
                </span>
              </td>

              <td>
                <div class="acciones-tabla">
                  <button
                    class="btn-editar"
                    :disabled="eliminandoId !== null"
                    @click="seleccionarEquipo(equipo)"
                  >
                    Editar
                  </button>

                  <button
                    class="btn-eliminar"
                    :disabled="eliminandoId !== null"
                    @click="eliminarEquipo(equipo)"
                  >
                    {{ eliminandoId === equipo.id ? 'Eliminando...' : 'Eliminar' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

  </div>
</template>

<style scoped>
.equipos-view {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 28px;
}

.page-header h1 {
  margin: 0 0 7px;
  color: #172b4d;
  font-size: 26px;
}

.page-header p,
.tabla-header p {
  margin: 0;
  color: #718096;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

button {
  border: none;
  border-radius: 7px;
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-secondary {
  background: #e9eef5;
  color: #334155;
}

.btn-secondary:hover {
  background: #dce4ef;
}

.formulario-contenedor {
  padding: 24px;
  margin-bottom: 22px;
  background: white;
  border: 1px solid #e5eaf1;
  border-radius: 12px;
}

.formulario-header {
  margin-bottom: 20px;
}

.formulario-header h2,
.tabla-header h2 {
  margin: 0 0 6px;
  color: #243b5a;
  font-size: 17px;
}

.formulario-descripcion {
  color: #8492a6;
  font-size: 13px;
}

.campos {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 17px;
}

.campo {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.campo label {
  color: #475569;
  font-size: 13px;
  font-weight: 600;
}

.campo input,
.campo select {
  width: 100%;
  box-sizing: border-box;
  padding: 11px 12px;
  border: 1px solid #dce3ed;
  border-radius: 7px;
  outline: none;
  background: white;
  color: #334155;
  font-size: 13px;
}

.campo input:focus,
.campo select:focus {
  border-color: #3b82f6;
}

.formulario-acciones {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 22px;
}

.mensaje {
  padding: 12px 16px;
  margin-bottom: 18px;
  border-radius: 8px;
  font-size: 13px;
}

.mensaje-exito {
  background: #ecfdf3;
  color: #167647;
  border: 1px solid #bbf7d0;
}

.mensaje-error {
  background: #fff1f2;
  color: #be123c;
  border: 1px solid #fecdd3;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  margin-bottom: 24px;
}

.summary-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
  background: white;
  border: 1px solid #e5eaf1;
  border-radius: 12px;
}

.summary-label {
  color: #718096;
  font-size: 13px;
}

.summary-card strong {
  color: #243b5a;
  font-size: 27px;
}

.summary-card .texto-activo {
  color: #16a36a;
}

.summary-card .texto-inactivo {
  color: #d97706;
}

.tabla-contenedor {
  padding: 22px;
  background: white;
  border: 1px solid #e5eaf1;
  border-radius: 12px;
}

.tabla-header {
  margin-bottom: 20px;
}

.table-container {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  white-space: nowrap;
}

thead {
  background: #f7f9fc;
}

th {
  padding: 13px 12px;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
}

td {
  padding: 15px 12px;
  border-bottom: 1px solid #edf0f5;
  color: #475569;
  font-size: 13px;
}

td strong {
  color: #243b5a;
}

.estado-badge {
  display: inline-block;
  padding: 5px 9px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
}

.estado-activo {
  background: #dcfce7;
  color: #15803d;
}

.estado-inactivo {
  background: #fef3c7;
  color: #b45309;
}

.acciones-tabla {
  display: flex;
  gap: 7px;
}

.btn-editar {
  padding: 7px 10px;
  background: #fff7ed;
  color: #c2410c;
}

.btn-editar:hover:not(:disabled) {
  background: #ffedd5;
}

.btn-eliminar {
  padding: 7px 10px;
  background: #fff1f2;
  color: #be123c;
}

.btn-eliminar:hover:not(:disabled) {
  background: #ffe4e6;
}

.estado-carga,
.estado-vacio {
  padding: 30px;
  color: #718096;
  text-align: center;
  font-size: 14px;
}

@media (max-width: 768px) {
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

  .formulario-acciones {
    flex-direction: column;
  }
}
</style>
