
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { obtenerDatos } from '../services/api'

// Importamos el componente reutilizable de gráficas.
import MetricChart from '../components/dashboard/MetricChart.vue'
import EstadoBadge from '../components/ui/EstadoBadge.vue'

// Estructura de los datos de cada servidor.
interface Servidor {
  id: number
  nombre_host: string
  direccion_ip: string | null
  sistema_operativo: string | null
  estado_actual: string | null
  ultima_conexion: string | null
}

// Estructura de las métricas registradas.
interface MetricaServidor {
  id: number
  servidor_id: number
  fecha_hora: string
  cpu_uso_porcentaje: number | null
  ram_uso_porcentaje: number | null
  ram_usada_mb: number | null
  disco_uso_porcentaje: number | null
  disco_libre_gb: number | null
  internet_activo: boolean | null
  latencia_ms: number | null
}

// Estructura de las alertas.
interface Alerta {
  id: number
  servidor_id: number
  respaldo_id: number | null
  fecha_hora: string
  tipo_alerta: string
  metrica_afectada: string | null
  valor_registrado: string | null
  nivel_alerta: string | null
  mensaje: string | null
  correo_enviado: boolean
}

// Variables que almacenan los datos recibidos del backend.
const servidores = ref<Servidor[]>([])
const metricas = ref<MetricaServidor[]>([])
const alertas = ref<Alerta[]>([])

// Guarda el servidor seleccionado.
const servidorSeleccionado = ref<number | null>(null)

// Guarda el periodo seleccionado para las gráficas.
const periodoSeleccionado = ref('todo')

// Controlan la carga y los errores.
const cargando = ref(false)
const errorCarga = ref('')

// Consulta los datos de FastAPI.
async function cargarDatos() {
  cargando.value = true
  errorCarga.value = ''

  try {
    // Consultamos los tres endpoints simultáneamente.
    const [datosServidores, datosMetricas, datosAlertas] = await Promise.all([
      obtenerDatos<Servidor[]>('/api/servidores/'),
      obtenerDatos<MetricaServidor[]>('/api/metricas-servidor/'),
      obtenerDatos<Alerta[]>('/api/alertas/'),
    ])

    // Guardamos los resultados recibidos.
    servidores.value = datosServidores
    metricas.value = datosMetricas
    alertas.value = datosAlertas

    // Seleccionamos el primer servidor si todavía no hay uno elegido.
    if (
      servidorSeleccionado.value === null &&
      servidores.value.length > 0
    ) {
      const primerServidor = servidores.value[0]

      if (primerServidor) {
        servidorSeleccionado.value = primerServidor.id
      }
    }
  } catch (error) {
    // Informamos si alguna consulta falla.
    console.error('Error al cargar los datos del Dashboard:', error)
    errorCarga.value = 'No fue posible cargar la información del Dashboard.'
  } finally {
    // Terminamos el estado de carga.
    cargando.value = false
  }
}

// Obtiene el servidor seleccionado.
const servidorActual = computed(() => {
  return servidores.value.find(
    servidor => servidor.id === servidorSeleccionado.value,
  ) ?? null
})

// Filtra y ordena las métricas del servidor seleccionado.
const metricasDelServidor = computed(() => {
  if (servidorSeleccionado.value === null) {
    return []
  }

  return metricas.value
    .filter(metrica => metrica.servidor_id === servidorSeleccionado.value)
    .sort((a, b) => {
      // Ordenamos por fecha y después por ID.
      const diferenciaFecha =
        new Date(b.fecha_hora).getTime() - new Date(a.fecha_hora).getTime()

      return diferenciaFecha !== 0 ? diferenciaFecha : b.id - a.id
    })
})

// Obtiene la última medición registrada.
const ultimaMetrica = computed(() => {
  return metricasDelServidor.value[0] ?? null
})

// Filtra y ordena las alertas del servidor seleccionado.
const alertasDelServidor = computed(() => {
  if (servidorSeleccionado.value === null) {
    return []
  }

  return alertas.value
    .filter(alerta => alerta.servidor_id === servidorSeleccionado.value)
    .sort((a, b) => {
      // Las alertas más recientes aparecen primero.
      const diferenciaFecha =
        new Date(b.fecha_hora).getTime() - new Date(a.fecha_hora).getTime()

      return diferenciaFecha !== 0 ? diferenciaFecha : b.id - a.id
    })
})

// Filtra las mediciones según el periodo seleccionado.
const metricasFiltradasPorPeriodo = computed(() => {
  // Obtenemos las mediciones del servidor seleccionado.
  const mediciones = metricasDelServidor.value

  // Obtenemos la fecha y hora actuales.
  const ahora = Date.now()

  // Guardará la fecha límite del periodo elegido.
  let fechaLimite: number | null = null

  if (periodoSeleccionado.value === '24h') {
    // Calculamos el inicio de las últimas 24 horas.
    fechaLimite = ahora - 24 * 60 * 60 * 1000
  } else if (periodoSeleccionado.value === '7d') {
    // Calculamos el inicio de los últimos siete días.
    fechaLimite = ahora - 7 * 24 * 60 * 60 * 1000
  }

  // Si no hay fecha límite, mostramos todo el historial.
  if (fechaLimite === null) {
    return mediciones
  }

  // Conservamos las mediciones dentro del periodo elegido.
  return mediciones.filter(metrica => {
    const fechaMedicion = new Date(metrica.fecha_hora).getTime()

    return fechaMedicion >= fechaLimite!
  })
})

// Ordena las mediciones de la más antigua a la más reciente.
const metricasParaGraficas = computed(() => {
  return [...metricasFiltradasPorPeriodo.value].reverse()
})

// Indica si el periodo visible abarca más de un día.
const periodoCruzaDia = computed(() => {
  const mediciones = metricasParaGraficas.value

  if (mediciones.length < 2) {
    return false
  }

  const inicio = new Date(mediciones[0]!.fecha_hora)
  const fin = new Date(mediciones[mediciones.length - 1]!.fecha_hora)

  return inicio.toDateString() !== fin.toDateString()
})

// En 24 horas del mismo día basta la hora. En el resto, fecha y hora.
const etiquetasIncluyenFecha = computed(() => {
  return periodoSeleccionado.value !== '24h' || periodoCruzaDia.value
})

// Genera las etiquetas del eje horizontal.
const etiquetasGraficas = computed(() => {
  return metricasParaGraficas.value.map((metrica) => {
    const fecha = new Date(metrica.fecha_hora)

    if (Number.isNaN(fecha.getTime())) {
      return metrica.fecha_hora
    }

    if (!etiquetasIncluyenFecha.value) {
      return fecha.toLocaleTimeString('es-MX', {
        hour: '2-digit',
        minute: '2-digit',
      })
    }

    return fecha.toLocaleString('es-MX', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  })
})

// Extrae los valores de CPU.
const valoresCPU = computed(() => {
  return metricasParaGraficas.value.map(
    metrica => metrica.cpu_uso_porcentaje,
  )
})

// Extrae los valores de RAM.
const valoresRAM = computed(() => {
  return metricasParaGraficas.value.map(
    metrica => metrica.ram_uso_porcentaje,
  )
})

// Extrae los valores de disco.
const valoresDisco = computed(() => {
  return metricasParaGraficas.value.map(
    metrica => metrica.disco_uso_porcentaje,
  )
})

// Convierte valores numéricos en texto.
function formatearValor(
  valor: number | null,
  decimales = 1,
): string {
  if (valor === null || valor === undefined) {
    return '--'
  }

  return Number(valor).toFixed(decimales)
}

// Convierte fechas a un formato legible.
function formatearFecha(fecha: string): string {
  return new Date(fecha).toLocaleString('es-MX')
}

// Clasifica el nivel sin asumir que el texto siempre existe.
function clasificarNivel(
  nivel: string | null,
): 'problema' | 'advertencia' | 'neutro' {
  const valor = (nivel ?? '').trim().toLowerCase()

  if (valor === 'problema') {
    return 'problema'
  }

  if (valor === 'advertencia') {
    return 'advertencia'
  }

  return 'neutro'
}

function textoNivel(nivel: string | null): string {
  const valor = (nivel ?? '').trim()
  return valor || 'Sin nivel'
}

// Obtiene el nombre del servidor de una alerta.
function obtenerNombreServidor(servidorId: number): string {
  return servidores.value.find(
    servidor => servidor.id === servidorId,
  )?.nombre_host ?? 'Servidor desconocido'
}

// Fecha de la última medición.
const fechaUltimaMetrica = computed(() => {
  if (!ultimaMetrica.value) {
    return 'Sin mediciones registradas'
  }

  return formatearFecha(ultimaMetrica.value.fecha_hora)
})

// Configuración de las tarjetas de métricas.
const metricCards = [
  { key: 'cpu', title: 'Uso de CPU' },
  { key: 'ram', title: 'Uso de RAM' },
  { key: 'disco', title: 'Uso de disco' },
  { key: 'internet', title: 'Conectividad' },
]

// Obtiene el valor correspondiente a cada tarjeta.
function obtenerValorTarjeta(key: string): string {
  if (!ultimaMetrica.value) {
    return '--'
  }

  switch (key) {
    case 'cpu':
      return `${formatearValor(ultimaMetrica.value.cpu_uso_porcentaje)} %`

    case 'ram':
      return `${formatearValor(ultimaMetrica.value.ram_uso_porcentaje)} %`

    case 'disco':
      return `${formatearValor(ultimaMetrica.value.disco_uso_porcentaje)} %`

    case 'internet':
      if (ultimaMetrica.value.internet_activo === null) {
        return '--'
      }

      return ultimaMetrica.value.internet_activo
        ? 'Conectado'
        : 'Desconectado'

    default:
      return '--'
  }
}

// Cargamos los datos cuando se abre el Dashboard.
onMounted(() => {
  cargarDatos()
})
</script>

<template>
  <div class="dashboard">

    <!-- Encabezado del Dashboard. -->
    <section class="dashboard-intro">
      <div>
        <h1>Resumen general</h1>
        <p>Consulta el estado y las mediciones registradas de tus servidores.</p>
      </div>

      <button
        type="button"
        class="refresh-button"
        :disabled="cargando"
        @click="cargarDatos"
      >
        {{ cargando ? 'Actualizando...' : 'Actualizar' }}
      </button>
    </section>

    <!-- Selector del servidor. -->
    <section class="selector-section">
      <label for="servidor">Servidor seleccionado:</label>

      <select
        id="servidor"
        v-model="servidorSeleccionado"
        class="server-select"
      >
        <option
          v-for="servidor in servidores"
          :key="servidor.id"
          :value="servidor.id"
        >
          {{ servidor.nombre_host }}
        </option>
      </select>
    </section>

    <!-- Carga inicial, error sin datos o aviso al actualizar. -->
    <p v-if="cargando && servidores.length === 0" class="state-card">
      Cargando información del dashboard...
    </p>

    <div
      v-else-if="errorCarga && servidores.length === 0"
      class="state-card state-card-error"
    >
      <p>{{ errorCarga }}</p>
      <button type="button" class="refresh-button" @click="cargarDatos">
        Reintentar
      </button>
    </div>

    <p v-else-if="errorCarga" class="error-message">
      {{ errorCarga }}
    </p>

    <template v-if="servidores.length > 0 || (!cargando && !errorCarga)">

      <!-- Información del servidor seleccionado. -->
      <section v-if="servidorActual" class="selected-server">
        <div>
          <h2>{{ servidorActual.nombre_host }}</h2>
          <p>{{ servidorActual.direccion_ip || 'Sin dirección IP' }}</p>
        </div>

        <EstadoBadge :estado="servidorActual.estado_actual" />
      </section>

      <!-- Tarjetas con las últimas métricas. -->
      <section class="metrics-section">
        <div class="section-heading">
          <h2>Estado del servidor</h2>
          <span class="measurement-date">
            Última medición: {{ fechaUltimaMetrica }}
          </span>
        </div>

        <div class="metrics-grid">
          <article
            v-for="card in metricCards"
            :key="card.key"
            class="metric-card"
          >
            <h3>{{ card.title }}</h3>
            <p class="metric-value">
              {{ obtenerValorTarjeta(card.key) }}
            </p>
          </article>
        </div>
      </section>

      <!-- Detalles de la última medición. -->
      <section class="details-section">
        <h2>Detalles de medición</h2>

        <div v-if="ultimaMetrica" class="details-grid">
          <div class="detail-item">
            <span>RAM utilizada</span>
            <strong>
              {{ formatearValor(ultimaMetrica.ram_usada_mb) }} MB
            </strong>
          </div>

          <div class="detail-item">
            <span>Espacio libre en disco</span>
            <strong>
              {{ formatearValor(ultimaMetrica.disco_libre_gb) }} GB
            </strong>
          </div>

          <div class="detail-item">
            <span>Latencia</span>
            <strong>
              {{ formatearValor(ultimaMetrica.latencia_ms) }} ms
            </strong>
          </div>
        </div>

        <p v-else class="empty-message">
          Este servidor todavía no tiene mediciones registradas.
        </p>
      </section>

      <!-- Gráficas de evolución de las métricas. -->
      <section class="charts-section">
        <div class="section-heading">
          <div>
            <h2>Historial de métricas</h2>
            <p>Evolución de los recursos del servidor seleccionado.</p>
          </div>

          <!-- Selector para cambiar el periodo de las gráficas. -->
          <div class="period-selector">
            <label for="periodo">Periodo:</label>

            <select
              id="periodo"
              v-model="periodoSeleccionado"
              class="period-select"
            >
              <option value="todo">Todo el historial</option>
              <option value="24h">Últimas 24 horas</option>
              <option value="7d">Últimos 7 días</option>
            </select>
          </div>
        </div>

        <!-- Mostramos las gráficas si existen mediciones en el periodo. -->
        <div
          v-if="metricasParaGraficas.length > 0"
          class="charts-grid"
        >
          <MetricChart
            titulo="Uso de CPU"
            :etiquetas="etiquetasGraficas"
            :valores="valoresCPU"
            color="#3b82f6"
          />

          <MetricChart
            titulo="Uso de RAM"
            :etiquetas="etiquetasGraficas"
            :valores="valoresRAM"
            color="#8b5cf6"
          />

          <MetricChart
            titulo="Uso de disco"
            :etiquetas="etiquetasGraficas"
            :valores="valoresDisco"
            color="#f59e0b"
          />
        </div>

        <p v-else class="empty-message">
          No hay mediciones registradas para el periodo seleccionado.
        </p>
      </section>

      <!-- Lista de servidores registrados. -->
      <section class="servers-section">
        <h2>Servidores registrados</h2>

        <div v-if="servidores.length > 0" class="servers-list">
          <article
            v-for="servidor in servidores"
            :key="servidor.id"
            class="server-item"
          >
            <div class="server-information">
              <strong>{{ servidor.nombre_host }}</strong>
              <span>{{ servidor.direccion_ip || 'Sin registro' }}</span>
              <span>{{ servidor.sistema_operativo || 'Sin registro' }}</span>
            </div>

            <EstadoBadge :estado="servidor.estado_actual" />
          </article>
        </div>

        <p v-else class="empty-message">
          No hay servidores registrados.
        </p>
      </section>

      <!-- Alertas del servidor seleccionado. -->
      <section class="alerts-section">
        <div class="section-heading">
          <div>
            <h2>Alertas recientes</h2>
            <p>Incidencias registradas para el servidor seleccionado.</p>
          </div>

          <span class="alert-count">
            {{ alertasDelServidor.length }}
            {{ alertasDelServidor.length === 1 ? 'alerta' : 'alertas' }}
          </span>
        </div>

        <div v-if="alertasDelServidor.length > 0" class="alerts-list">
          <article
            v-for="alerta in alertasDelServidor"
            :key="alerta.id"
            class="alert-item"
            :class="`nivel-${clasificarNivel(alerta.nivel_alerta)}`"
          >
            <div class="alert-information">
              <div class="alert-title">
                <strong>{{ alerta.metrica_afectada || 'Sin métrica' }}</strong>

                <span
                  class="alert-level"
                  :class="`alert-level-${clasificarNivel(alerta.nivel_alerta)}`"
                >
                  {{ textoNivel(alerta.nivel_alerta) }}
                </span>
              </div>

              <p>{{ alerta.mensaje || 'Sin mensaje' }}</p>

              <div class="alert-metadata">
                <span>{{ obtenerNombreServidor(alerta.servidor_id) }}</span>
                <span>Valor: {{ alerta.valor_registrado || 'Sin valor' }}</span>
                <span>{{ formatearFecha(alerta.fecha_hora) }}</span>
              </div>
            </div>
          </article>
        </div>

        <p v-else class="empty-message">
          No hay alertas registradas para este servidor.
        </p>
      </section>

      <!-- Aviso sobre el origen de los registros. -->
      <p class="test-data-note">
        Nota: la información mostrada corresponde a registros de prueba.
        No representa el monitoreo en tiempo real de Dulcería Atilano.
      </p>
    </template>
  </div>
</template>

<style scoped>
/* Estilos generales del Dashboard. */
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.dashboard-intro {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.dashboard-intro h1 {
  margin: 0 0 8px;
  color: #1e293b;
  font-size: 28px;
}

.dashboard-intro p {
  margin: 0;
  color: #64748b;
}

/* Selector del servidor. */
.selector-section {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.selector-section label {
  color: #334155;
  font-weight: 600;
}

.refresh-button {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  background: #2563eb;
  color: white;
  font: inherit;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.refresh-button:hover:not(:disabled) {
  background: #1d4ed8;
}

.refresh-button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.server-select,
.period-select {
  min-width: 240px;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: white;
  color: #334155;
  font-size: 14px;
}

/* Mensajes de carga y error. */
.loading-message,
.empty-message {
  color: #64748b;
}

.error-message {
  margin: 0;
  color: #991b1b;
  background: #fee2e2;
  padding: 12px 14px;
  border-radius: 8px;
}

.state-card {
  margin: 0;
  padding: 22px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  color: #64748b;
}

.state-card-error {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  color: #991b1b;
  background: #fef2f2;
  border-color: #fecaca;
}

.state-card-error p {
  margin: 0;
}

/* Información del servidor seleccionado. */
.selected-server {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  padding: 18px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

.selected-server h2 {
  margin: 0 0 5px;
  color: #1e293b;
  font-size: 18px;
}

.selected-server p {
  margin: 0;
  color: #64748b;
}

/* Encabezados de las secciones. */
.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 15px;
}

.section-heading h2,
.details-section h2,
.servers-section h2 {
  margin: 0;
  color: #1e293b;
  font-size: 19px;
}

.section-heading p {
  margin: 6px 0 0;
  color: #64748b;
  font-size: 13px;
}

.measurement-date {
  color: #64748b;
  font-size: 12px;
}

/* Tarjetas de métricas. */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 15px;
}

.metric-card {
  padding: 20px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

.metric-card h3 {
  margin: 0 0 15px;
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
}

.metric-value {
  margin: 0;
  color: #1e293b;
  font-size: 25px;
  font-weight: 700;
}

/* Detalles de las mediciones. */
.details-section,
.servers-section,
.alerts-section {
  padding: 20px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

.details-section h2,
.servers-section h2 {
  margin-bottom: 15px;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 15px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item span {
  color: #64748b;
  font-size: 13px;
}

.detail-item strong {
  color: #1e293b;
  font-size: 17px;
}

/* Organización de las gráficas. */
.charts-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 15px;
}

/* Selector de periodos de las gráficas. */
.period-selector {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.period-selector label {
  color: #334155;
  font-size: 13px;
  font-weight: 600;
}

.period-select {
  min-width: 190px;
}

/* Lista de servidores. */
.servers-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.server-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  padding: 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.server-information {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.server-information strong {
  color: #1e293b;
}

.server-information span {
  color: #64748b;
  font-size: 13px;
}

/* Lista de alertas. */
.alert-count {
  padding: 6px 10px;
  border-radius: 20px;
  background: #f1f5f9;
  color: #475569;
  font-size: 12px;
  font-weight: 600;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item {
  padding: 15px;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #f59e0b;
  border-radius: 8px;
}

.alert-information {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.alert-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.alert-title strong {
  color: #1e293b;
}

.alert-information p {
  margin: 0;
  color: #475569;
  font-size: 14px;
}

.alert-level {
  padding: 5px 9px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.alert-level-advertencia {
  background: #fef3c7;
  color: #92400e;
}

.alert-level-problema {
  background: #fee2e2;
  color: #991b1b;
}

.alert-level-neutro {
  background: #e2e8f0;
  color: #475569;
}

.nivel-problema {
  border-left-color: #dc2626;
}

.nivel-neutro {
  border-left-color: #94a3b8;
}

.alert-metadata {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 18px;
  color: #64748b;
  font-size: 12px;
}

/* Aviso sobre el origen de los registros. */
.test-data-note {
  margin: 0;
  color: #64748b;
  font-size: 12px;
  text-align: center;
}

/* Adaptación para pantallas medianas. */
@media (max-width: 900px) {
  .metrics-grid,
  .charts-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

/* Adaptación para pantallas pequeñas. */
@media (max-width: 600px) {
  .metrics-grid,
  .details-grid,
  .charts-grid {
    grid-template-columns: 1fr;
  }

  .selected-server,
  .server-item {
    align-items: flex-start;
    flex-direction: column;
  }

  .section-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .dashboard-intro,
  .state-card-error {
    align-items: flex-start;
    flex-direction: column;
  }

  .server-select,
  .period-select,
  .refresh-button {
    width: 100%;
  }
}
</style>
