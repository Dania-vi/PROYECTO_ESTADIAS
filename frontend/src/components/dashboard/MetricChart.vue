
<script setup lang="ts">
// Importamos las herramientas necesarias de Vue.
import { computed } from 'vue'

// Importamos el componente de gráficas y su configuración.
import { Line } from 'vue-chartjs'

// Importamos los elementos de Chart.js que utilizaremos.
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
} from 'chart.js'

// Registramos los elementos necesarios para dibujar las gráficas.
ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
)

// Definimos los datos que recibirá este componente desde el Dashboard.
const props = defineProps<{
  titulo: string
  etiquetas: string[]
  valores: (number | null)[]
  color: string
}>()

// Construimos la información que utilizará Chart.js.
const datosGrafica = computed(() => ({
  labels: props.etiquetas,
  datasets: [
    {
      label: props.titulo,
      backgroundColor: props.color,
      borderColor: props.color,
      data: props.valores,
      tension: 0.3,
      fill: false,
      spanGaps: false,
      pointRadius: 4,
      pointHoverRadius: 6,
    },
  ],
}))

// Configuramos la apariencia y el comportamiento de la gráfica.
const opcionesGrafica = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    title: {
      display: false,
    },
    tooltip: {
      enabled: true,
    },
  },
  scales: {
    x: {
      ticks: {
        autoSkip: true,
        maxTicksLimit: 8,
        maxRotation: 0,
      },
    },
    y: {
      beginAtZero: true,
      min: 0,
      max: 100,
      ticks: {
        callback: (valor: string | number) => `${valor}%`,
      },
    },
  },
}
</script>

<template>
  <div class="metric-chart">
    <!-- Título de la gráfica. -->
    <h3>{{ titulo }}</h3>

    <!-- Contenedor donde se dibuja la gráfica de líneas. -->
    <div class="chart-container">
      <Line
        :data="datosGrafica"
        :options="opcionesGrafica"
      />
    </div>
  </div>
</template>

<style scoped>
/* Tarjeta que contiene cada gráfica. */
.metric-chart {
  padding: 20px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

/* Título de la gráfica. */
.metric-chart h3 {
  margin: 0 0 15px;
  color: #1e293b;
  font-size: 16px;
}

/* Área destinada a dibujar la gráfica. */
.chart-container {
  position: relative;
  width: 100%;
  height: 260px;
}
</style>
