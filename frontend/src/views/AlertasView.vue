
<script setup lang="ts">
// Importamos las herramientas reactivas de Vue.
import { computed, onMounted, ref } from 'vue'

// Importamos la función para consultar el backend.
import { obtenerDatos } from '../services/api'

// Representa la estructura de una alerta.
interface Alerta {
  id: number
  servidor_id: number | null
  respaldo_id: number | null
  fecha_hora: string
  tipo_alerta: string
  metrica_afectada: string | null
  valor_registrado: string | null
  nivel_alerta: string | null
  mensaje: string | null
  correo_enviado: boolean
}

// Representa la información de un servidor.
interface Servidor {
  id: number
  nombre_host: string
}

// Guarda las alertas consultadas.
const alertas = ref<Alerta[]>([])

// Guarda los servidores registrados.
const servidores = ref<Servidor[]>([])

// Controla el estado de carga.
const cargando = ref(false)

// Guarda los errores de consulta.
const error = ref('')

// Guarda los valores de los filtros.
const busqueda = ref('')
const filtroTipo = ref('Todos')
const filtroNivel = ref('Todos')
const filtroCorreo = ref('Todos')
const fechaInicial = ref('')
const fechaFinal = ref('')

// Consulta las alertas y los servidores.
async function cargarAlertas() {
  cargando.value = true
  error.value = ''

  try {
    // Consultamos ambos recursos al mismo tiempo.
    const [datosAlertas, datosServidores] = await Promise.all([
      obtenerDatos<Alerta[]>('/api/alertas/'),
      obtenerDatos<Servidor[]>('/api/servidores/'),
    ])

    alertas.value = datosAlertas
    servidores.value = datosServidores
  } catch (err) {
    // Capturamos los errores de comunicación con el backend.
    error.value =
      err instanceof Error
        ? err.message
        : 'No fue posible consultar las alertas.'
  } finally {
    cargando.value = false
  }
}

// Obtiene el nombre del servidor asociado a una alerta.
function obtenerNombreServidor(servidorId: number | null): string {
  if (servidorId === null) return 'No especificado'

  const servidor = servidores.value.find(
    (item) => item.id === servidorId
  )

  return servidor ? servidor.nombre_host : `Servidor ID ${servidorId}`
}

// Obtiene la fecha en formato AAAA-MM-DD.
function fechaCalendario(fecha: string): string {
  if (!fecha) return ''

  const normalizada = fecha.includes('T')
    ? fecha
    : fecha.replace(' ', 'T')

  const fechaObjeto = new Date(normalizada)

  if (Number.isNaN(fechaObjeto.getTime())) return ''

  const anio = fechaObjeto.getFullYear()
  const mes = String(fechaObjeto.getMonth() + 1).padStart(2, '0')
  const dia = String(fechaObjeto.getDate()).padStart(2, '0')

  return `${anio}-${mes}-${dia}`
}

// Convierte la fecha a un formato legible.
function formatearFecha(fecha: string): string {
  if (!fecha) return '—'

  const normalizada = fecha.includes('T')
    ? fecha
    : fecha.replace(' ', 'T')

  const fechaObjeto = new Date(normalizada)

  if (Number.isNaN(fechaObjeto.getTime())) return fecha

  return fechaObjeto.toLocaleString('es-MX', {
    dateStyle: 'short',
    timeStyle: 'short',
  })
}

// Obtiene los tipos de alerta disponibles.
const tiposDisponibles = computed(() => {
  return [...new Set(
    alertas.value.map((alerta) => alerta.tipo_alerta)
  )].sort((a, b) => a.localeCompare(b))
})

// Obtiene los niveles registrados.
const nivelesDisponibles = computed(() => {
  return [...new Set(
    alertas.value
      .map((alerta) => alerta.nivel_alerta)
      .filter((nivel): nivel is string => Boolean(nivel))
  )].sort((a, b) => a.localeCompare(b))
})

// Comprueba si el rango de fechas es válido.
const rangoFechasInvalido = computed(() => {
  return (
    fechaInicial.value !== '' &&
    fechaFinal.value !== '' &&
    fechaInicial.value > fechaFinal.value
  )
})

// Filtra las alertas según los criterios seleccionados.
const alertasFiltradas = computed(() => {
  const texto = busqueda.value.trim().toLowerCase()

  return alertas.value.filter((alerta) => {
    // Comprueba el tipo seleccionado.
    const coincideTipo =
      filtroTipo.value === 'Todos' ||
      alerta.tipo_alerta === filtroTipo.value

    // Comprueba el nivel seleccionado.
    const coincideNivel =
      filtroNivel.value === 'Todos' ||
      alerta.nivel_alerta === filtroNivel.value

    // Comprueba si el correo fue enviado.
    const coincideCorreo =
      filtroCorreo.value === 'Todos' ||
      (filtroCorreo.value === 'Enviado' && alerta.correo_enviado) ||
      (filtroCorreo.value === 'Pendiente' && !alerta.correo_enviado)

    // Prepara los datos que se pueden buscar.
    const datosBusqueda = [
      alerta.id,
      obtenerNombreServidor(alerta.servidor_id),
      alerta.tipo_alerta,
      alerta.metrica_afectada ?? '',
      alerta.valor_registrado ?? '',
      alerta.nivel_alerta ?? '',
      alerta.mensaje ?? '',
    ].join(' ').toLowerCase()

    const coincideBusqueda =
      !texto || datosBusqueda.includes(texto)

    // Comprueba las fechas.
    const fechaAlerta = fechaCalendario(alerta.fecha_hora)

    const coincideFechaInicial =
      !fechaInicial.value ||
      (fechaAlerta !== '' && fechaAlerta >= fechaInicial.value)

    const coincideFechaFinal =
      !fechaFinal.value ||
      (fechaAlerta !== '' && fechaAlerta <= fechaFinal.value)

    return (
      coincideTipo &&
      coincideNivel &&
      coincideCorreo &&
      coincideBusqueda &&
      coincideFechaInicial &&
      coincideFechaFinal
    )
  }).sort((a, b) => {
    // Ordena las alertas de la más reciente a la más antigua.
    return new Date(b.fecha_hora).getTime() -
      new Date(a.fecha_hora).getTime()
  })
})

// Calcula el total de alertas.
const totalAlertas = computed(() => alertas.value.length)

// Cuenta las alertas clasificadas como Advertencia.
const totalAdvertencias = computed(() => {
  return alertas.value.filter(
    (alerta) =>
      alerta.nivel_alerta?.toLowerCase() === 'advertencia'
  ).length
})

// Cuenta las alertas clasificadas como Problema.
const totalProblemas = computed(() => {
  return alertas.value.filter(
    (alerta) =>
      alerta.nivel_alerta?.toLowerCase() === 'problema'
  ).length
})

// Cuenta las alertas que todavía no tienen correo enviado.
const correosPendientes = computed(() => {
  return alertas.value.filter(
    (alerta) => !alerta.correo_enviado
  ).length
})

// Limpia todos los filtros.
function limpiarFiltros() {
  busqueda.value = ''
  filtroTipo.value = 'Todos'
  filtroNivel.value = 'Todos'
  filtroCorreo.value = 'Todos'
  fechaInicial.value = ''
  fechaFinal.value = ''
}

// Consulta los datos al abrir la vista.
onMounted(cargarAlertas)
</script>

<template>
  <section class="alertas-view">

    <!-- Encabezado del módulo. -->
    <header class="encabezado">
      <div>
        <h1>Alertas del sistema</h1>
        <p>Consulta y clasificación de eventos detectados durante el monitoreo.</p>
      </div>

      <!-- Botón para actualizar los registros. -->
      <button
        type="button"
        class="btn-actualizar"
        @click="cargarAlertas"
        :disabled="cargando"
      >
        {{ cargando ? 'Actualizando...' : 'Actualizar' }}
      </button>
    </header>

    <!-- Indicador de carga. -->
    <p v-if="cargando" class="mensaje">
      Cargando alertas...
    </p>

    <!-- Mensaje cuando ocurre un error. -->
    <p v-else-if="error" class="mensaje error">
      {{ error }}
    </p>

    <template v-else>

      <!-- Tarjetas de resumen. -->
      <section class="resumen">

        <article class="tarjeta">
          <span class="tarjeta-icono">🔔</span>
          <div>
            <p>Total de alertas</p>
            <strong>{{ totalAlertas }}</strong>
          </div>
        </article>

        <article class="tarjeta advertencia">
          <span class="tarjeta-icono">⚠️</span>
          <div>
            <p>Advertencias</p>
            <strong>{{ totalAdvertencias }}</strong>
          </div>
        </article>

        <article class="tarjeta problema">
          <span class="tarjeta-icono">🚨</span>
          <div>
            <p>Problemas</p>
            <strong>{{ totalProblemas }}</strong>
          </div>
        </article>

        <article class="tarjeta pendiente">
          <span class="tarjeta-icono">✉️</span>
          <div>
            <p>Correos pendientes</p>
            <strong>{{ correosPendientes }}</strong>
          </div>
        </article>

      </section>

      <!-- Mensaje cuando no existen alertas. -->
      <div v-if="alertas.length === 0" class="mensaje">
        No hay alertas registradas en el sistema.
      </div>

      <template v-else>

        <!-- Controles de búsqueda y filtros. -->
        <section class="filtros-contenedor">

          <div class="campo campo-busqueda">
            <label for="busqueda-alertas">Buscar alertas</label>
            <input
              id="busqueda-alertas"
              v-model="busqueda"
              type="text"
              placeholder="Servidor, métrica, mensaje, ID..."
            />
          </div>

          <div class="campo">
            <label for="filtro-tipo">Tipo</label>
            <select id="filtro-tipo" v-model="filtroTipo">
              <option value="Todos">Todos los tipos</option>
              <option
                v-for="tipo in tiposDisponibles"
                :key="tipo"
                :value="tipo"
              >
                {{ tipo }}
              </option>
            </select>
          </div>

          <div class="campo">
            <label for="filtro-nivel">Nivel</label>
            <select id="filtro-nivel" v-model="filtroNivel">
              <option value="Todos">Todos los niveles</option>
              <option
                v-for="nivel in nivelesDisponibles"
                :key="nivel"
                :value="nivel"
              >
                {{ nivel }}
              </option>
            </select>
          </div>

          <div class="campo">
            <label for="filtro-correo">Estado del correo</label>
            <select id="filtro-correo" v-model="filtroCorreo">
              <option value="Todos">Todos</option>
              <option value="Enviado">Enviado</option>
              <option value="Pendiente">Pendiente</option>
            </select>
          </div>

          <div class="campo">
            <label for="fecha-inicial">Desde</label>
            <input
              id="fecha-inicial"
              v-model="fechaInicial"
              type="date"
              :max="fechaFinal || undefined"
            />
          </div>

          <div class="campo">
            <label for="fecha-final">Hasta</label>
            <input
              id="fecha-final"
              v-model="fechaFinal"
              type="date"
              :min="fechaInicial || undefined"
            />
          </div>

          <button
            type="button"
            class="btn-limpiar"
            @click="limpiarFiltros"
          >
            Limpiar filtros
          </button>

        </section>

        <!-- Mensaje cuando el rango de fechas es inválido. -->
        <p v-if="rangoFechasInvalido" class="mensaje-error">
          La fecha inicial no puede ser posterior a la fecha final.
        </p>

        <!-- Contador de resultados. -->
        <div v-if="!rangoFechasInvalido" class="contador-resultados">
          Mostrando
          <strong>{{ alertasFiltradas.length }}</strong>
          de
          <strong>{{ alertas.length }}</strong>
          alertas
        </div>

        <!-- Tabla de alertas. -->
        <div v-if="!rangoFechasInvalido" class="tabla-contenedor">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Fecha y hora</th>
                <th>Servidor</th>
                <th>Tipo</th>
                <th>Métrica</th>
                <th>Valor</th>
                <th>Nivel</th>
                <th>Mensaje</th>
                <th>Correo</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="alerta in alertasFiltradas"
                :key="alerta.id"
              >
                <td>{{ alerta.id }}</td>
                <td>{{ formatearFecha(alerta.fecha_hora) }}</td>
                <td>{{ obtenerNombreServidor(alerta.servidor_id) }}</td>
                <td>{{ alerta.tipo_alerta }}</td>
                <td>{{ alerta.metrica_afectada || '—' }}</td>
                <td>{{ alerta.valor_registrado || '—' }}</td>

                <td>
                  <span
                    class="etiqueta-nivel"
                    :class="{
                      'nivel-advertencia':
                        alerta.nivel_alerta?.toLowerCase() === 'advertencia',
                      'nivel-problema':
                        alerta.nivel_alerta?.toLowerCase() === 'problema',
                    }"
                  >
                    {{ alerta.nivel_alerta || 'Sin clasificar' }}
                  </span>
                </td>

                <td class="mensaje-celda">
                  {{ alerta.mensaje || '—' }}
                </td>

                <td>
                  <span
                    class="estado-correo"
                    :class="alerta.correo_enviado ? 'correo-enviado' : 'correo-pendiente'"
                  >
                    {{ alerta.correo_enviado ? 'Enviado' : 'Pendiente' }}
                  </span>
                </td>
              </tr>

              <!-- Mensaje cuando ningún registro coincide con los filtros. -->
              <tr v-if="alertasFiltradas.length === 0">
                <td colspan="9" class="sin-registros">
                  No se encontraron alertas con los criterios seleccionados.
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
/* Contenedor principal de la vista. */
.alertas-view {
  width: 100%;
  padding: 24px;
  box-sizing: border-box;
  color: #1f2937;
}

/* Encabezado del módulo. */
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

/* Botón para actualizar. */
.btn-actualizar {
  background-color: #2563eb;
}

.btn-actualizar:hover:not(:disabled) {
  background-color: #1d4ed8;
}

/* Distribución de las tarjetas de resumen. */
.resumen {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

/* Tarjeta individual. */
.tarjeta {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

.tarjeta-icono {
  font-size: 26px;
}

.tarjeta p {
  margin: 0 0 6px;
  color: #64748b;
  font-size: 13px;
}

.tarjeta strong {
  font-size: 24px;
  color: #1e293b;
}

.tarjeta.advertencia {
  border-left: 4px solid #f59e0b;
}

.tarjeta.problema {
  border-left: 4px solid #ef4444;
}

.tarjeta.pendiente {
  border-left: 4px solid #64748b;
}

/* Contenedor de filtros. */
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

/* Organización de cada campo. */
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

/* Campos de búsqueda y selección. */
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

/* Botón para limpiar filtros. */
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

/* Tabla de alertas. */
table {
  width: 100%;
  min-width: 1200px;
  border-collapse: collapse;
}

th,
td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
  font-size: 13px;
  vertical-align: middle;
}

th {
  background-color: #f8fafc;
  color: #475569;
  font-weight: 600;
}

/* Etiquetas de clasificación. */
.etiqueta-nivel,
.estado-correo {
  display: inline-block;
  padding: 5px 9px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.nivel-advertencia {
  color: #92400e;
  background-color: #fef3c7;
}

.nivel-problema {
  color: #991b1b;
  background-color: #fee2e2;
}

.correo-enviado {
  color: #166534;
  background-color: #dcfce7;
}

.correo-pendiente {
  color: #475569;
  background-color: #e2e8f0;
}

/* Limita el ancho del mensaje para conservar la tabla legible. */
.mensaje-celda {
  max-width: 280px;
  min-width: 180px;
  white-space: normal;
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
  color: #c0392b;
}

.sin-registros {
  padding: 25px;
  color: #64748b;
  text-align: center;
}

/* Adaptación para pantallas pequeñas. */
@media (max-width: 1000px) {
  .resumen {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

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

  .resumen {
    grid-template-columns: 1fr;
  }
}
</style>
