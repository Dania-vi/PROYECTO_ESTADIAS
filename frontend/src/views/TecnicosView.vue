
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  obtenerDatos,
  enviarDatos,
  actualizarDatos,
  eliminarDatos
} from '../services/api'

// Estructura de los técnicos registrados en la base de datos.
interface Tecnico {
  id: number
  nombre: string
  correo: string | null
  telefono: string | null
  activo: boolean
}

// Datos que se envían al backend para registrar o actualizar un técnico.
interface TecnicoDatos {
  nombre: string
  correo: string | null
  telefono: string | null
  activo: boolean
}

// Lista de técnicos.
const tecnicos = ref<Tecnico[]>([])

// Estados de la pantalla.
const cargando = ref(false)
const guardando = ref(false)
const editando = ref(false)
const tecnicoIdActual = ref<number | null>(null)

// Mensajes para informar el resultado de las operaciones.
const mensajeExito = ref('')
const mensajeError = ref('')

// Datos del formulario.
const formulario = ref<TecnicoDatos>({
  nombre: '',
  correo: '',
  telefono: '',
  activo: true
})

// Contadores para las tarjetas de resumen.
const totalTecnicos = computed(() => tecnicos.value.length)

const tecnicosActivos = computed(() =>
  tecnicos.value.filter(tecnico => tecnico.activo).length
)

const tecnicosInactivos = computed(() =>
  tecnicos.value.filter(tecnico => !tecnico.activo).length
)

// Consulta los técnicos registrados en el backend.
async function cargarTecnicos() {
  cargando.value = true
  mensajeError.value = ''

  try {
    tecnicos.value = await obtenerDatos<Tecnico[]>('/api/tecnicos/')
  } catch (error) {
    mensajeError.value =
      error instanceof Error
        ? error.message
        : 'No se pudieron cargar los técnicos.'
  } finally {
    cargando.value = false
  }
}

// Limpia el formulario y lo prepara para registrar un técnico nuevo.
function limpiarFormulario() {
  formulario.value = {
    nombre: '',
    correo: '',
    telefono: '',
    activo: true
  }

  editando.value = false
  tecnicoIdActual.value = null
}

// Carga los datos del técnico seleccionado en el formulario.
function seleccionarTecnico(tecnico: Tecnico) {
  formulario.value = {
    nombre: tecnico.nombre,
    correo: tecnico.correo || '',
    telefono: tecnico.telefono || '',
    activo: tecnico.activo
  }

  tecnicoIdActual.value = tecnico.id
  editando.value = true
  mensajeExito.value = ''
  mensajeError.value = ''

  // Desplaza la pantalla hacia el formulario.
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Registra un técnico nuevo o actualiza uno existente.
async function guardarTecnico() {
  mensajeExito.value = ''
  mensajeError.value = ''

  // Verifica que el nombre sea obligatorio.
  if (!formulario.value.nombre.trim()) {
    mensajeError.value = 'El nombre del técnico es obligatorio.'
    return
  }

  // Prepara los datos antes de enviarlos al backend.
  const datos: TecnicoDatos = {
    nombre: formulario.value.nombre.trim(),
    correo: formulario.value.correo?.trim() || null,
    telefono: formulario.value.telefono?.trim() || null,
    activo: formulario.value.activo
  }

  guardando.value = true

  try {
    if (editando.value && tecnicoIdActual.value !== null) {
      // Actualiza el técnico seleccionado.
      await actualizarDatos(
        `/api/tecnicos/${tecnicoIdActual.value}`,
        datos
      )

      mensajeExito.value = 'Técnico actualizado correctamente.'
    } else {
      // Registra un técnico nuevo.
      await enviarDatos('/api/tecnicos/', datos)

      mensajeExito.value = 'Técnico registrado correctamente.'
    }

    limpiarFormulario()
    await cargarTecnicos()
  } catch (error) {
    mensajeError.value =
      error instanceof Error
        ? error.message
        : 'No se pudo guardar la información del técnico.'
  } finally {
    guardando.value = false
  }
}

// Elimina un técnico. El backend impedirá la operación
// si existen mantenimientos asociados a ese técnico.
async function eliminarTecnico(tecnico: Tecnico) {
  const confirmar = window.confirm(
    `¿Estás seguro de eliminar al técnico "${tecnico.nombre}"?`
  )

  if (!confirmar) return

  mensajeExito.value = ''
  mensajeError.value = ''

  try {
    await eliminarDatos(`/api/tecnicos/${tecnico.id}`)

    mensajeExito.value = 'Técnico eliminado correctamente.'
    await cargarTecnicos()

    // Si se estaba editando el técnico eliminado, limpia el formulario.
    if (tecnicoIdActual.value === tecnico.id) {
      limpiarFormulario()
    }
  } catch (error) {
    mensajeError.value =
      error instanceof Error
        ? error.message
        : 'No se pudo eliminar el técnico.'
  }
}

// Carga inicial de los técnicos al abrir la vista.
onMounted(() => {
  cargarTecnicos()
})
</script>

<template>
  <div class="tecnicos-view">
    <!-- Encabezado de la sección. -->
    <div class="page-header">
      <div>
        <h1>Gestión de técnicos</h1>
        <p>Administra la información del personal de soporte técnico.</p>
      </div>

      <div class="header-actions">
        <button class="btn-secondary" @click="cargarTecnicos">
          Actualizar
        </button>

        <button class="btn-primary" @click="limpiarFormulario">
          + Nuevo técnico
        </button>
      </div>
    </div>

    <!-- Formulario para registrar o editar técnicos. -->
    <section class="formulario-contenedor">
      <div class="formulario-header">
        <h2>{{ editando ? 'Editar técnico' : 'Registrar técnico' }}</h2>
        <span class="formulario-descripcion">
          Completa la información del técnico.
        </span>
      </div>

      <form @submit.prevent="guardarTecnico">
        <div class="campos">
          <div class="campo">
            <label for="nombre">Nombre completo *</label>
            <input
              id="nombre"
              v-model="formulario.nombre"
              type="text"
              placeholder="Nombre del técnico"
              maxlength="120"
              required
            />
          </div>

          <div class="campo">
            <label for="correo">Correo electrónico</label>
            <input
              id="correo"
              v-model="formulario.correo"
              type="email"
              placeholder="tecnico@ejemplo.com"
              maxlength="100"
            />
          </div>

          <div class="campo">
            <label for="telefono">Teléfono</label>
            <input
              id="telefono"
              v-model="formulario.telefono"
              type="tel"
              placeholder="Número de teléfono"
              maxlength="20"
            />
          </div>

          <div class="campo">
            <label for="activo">Estado</label>
            <select id="activo" v-model="formulario.activo">
              <option :value="true">Activo</option>
              <option :value="false">Inactivo</option>
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
                  : 'Registrar técnico'
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

    <!-- Tarjetas con el resumen de técnicos. -->
    <section class="summary-grid">
      <div class="summary-card">
        <span class="summary-label">Total de técnicos</span>
        <strong>{{ totalTecnicos }}</strong>
      </div>

      <div class="summary-card">
        <span class="summary-label">Técnicos activos</span>
        <strong class="texto-activo">{{ tecnicosActivos }}</strong>
      </div>

      <div class="summary-card">
        <span class="summary-label">Técnicos inactivos</span>
        <strong class="texto-inactivo">{{ tecnicosInactivos }}</strong>
      </div>
    </section>

    <!-- Tabla de técnicos registrados. -->
    <section class="tabla-contenedor">
      <div class="tabla-header">
        <div>
          <h2>Técnicos registrados</h2>
          <p>Consulta y administra al personal de soporte.</p>
        </div>
      </div>

      <div v-if="cargando" class="estado-carga">
        Cargando técnicos...
      </div>

      <div v-else-if="tecnicos.length === 0" class="estado-vacio">
        No hay técnicos registrados.
      </div>

      <div v-else class="table-container">
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Correo electrónico</th>
              <th>Teléfono</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="tecnico in tecnicos" :key="tecnico.id">
              <td>
                <strong>{{ tecnico.nombre }}</strong>
              </td>

              <td>{{ tecnico.correo || '—' }}</td>

              <td>{{ tecnico.telefono || '—' }}</td>

              <td>
                <span
                  class="estado-badge"
                  :class="
                    tecnico.activo
                      ? 'estado-activo'
                      : 'estado-inactivo'
                  "
                >
                  {{ tecnico.activo ? 'Activo' : 'Inactivo' }}
                </span>
              </td>

              <td>
                <div class="acciones-tabla">
                  <button
                    class="btn-editar"
                    @click="seleccionarTecnico(tecnico)"
                  >
                    Editar
                  </button>

                  <button
                    class="btn-eliminar"
                    @click="eliminarTecnico(tecnico)"
                  >
                    Eliminar
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
.tecnicos-view {
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

.btn-editar:hover {
  background: #ffedd5;
}

.btn-eliminar {
  padding: 7px 10px;
  background: #fff1f2;
  color: #be123c;
}

.btn-eliminar:hover {
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
