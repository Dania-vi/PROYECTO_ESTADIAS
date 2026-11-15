
// Importamos las funciones necesarias de Vue Router.
import { createRouter, createWebHistory } from 'vue-router'

// Importamos la vista principal del dashboard.
import DashboardView from '../views/DashboardView.vue'

// Importamos la vista de servidores.
import ServidoresView from '../views/ServidoresView.vue'

// Importamos la vista de mantenimientos.
import MantenimientosView from '../views/MantenimientosView.vue'

// Importamos la vista del historial de actividades.
import HistorialView from '../views/HistorialView.vue'

// Importamos la vista de sucursales.
import SucursalesView from '../views/SucursalesView.vue'

// Importamos la vista de equipos.
import EquiposView from '../views/EquiposView.vue'

// Importamos la vista de técnicos.
import TecnicosView from '../views/TecnicosView.vue'

// Importamos la vista de alertas.
import AlertasView from '../views/AlertasView.vue'

// Importamos la vista de respaldos.
import RespaldosView from '../views/RespaldosView.vue'

// Importamos la vista para direcciones que no existen.
import NotFoundView from '../views/NotFoundView.vue'

// Definimos las rutas de navegación de nuestra aplicación.
const routes = [
  {
    // Página principal del sistema.
    path: '/',
    name: 'dashboard',
    component: DashboardView,
  },
  {
    // Página que muestra los servidores registrados.
    path: '/servidores',
    name: 'servidores',
    component: ServidoresView,
  },
  {
    // Página que muestra los mantenimientos registrados.
    path: '/mantenimientos',
    name: 'mantenimientos',
    component: MantenimientosView,
  },
  {
    // Página que muestra el historial de actividades.
    path: '/historial',
    name: 'historial',
    component: HistorialView,
  },
  {
    // Página para administrar las sucursales.
    path: '/sucursales',
    name: 'sucursales',
    component: SucursalesView,
  },
  {
    // Página para administrar los equipos.
    path: '/equipos',
    name: 'equipos',
    component: EquiposView,
  },
  {
    // Página para administrar los técnicos.
    path: '/tecnicos',
    name: 'tecnicos',
    component: TecnicosView,
  },
  {
    // Página para consultar y clasificar las alertas del sistema.
    path: '/alertas',
    name: 'alertas',
    component: AlertasView,
  },
  {
    // Página para consultar y registrar operaciones de respaldo.
    path: '/respaldos',
    name: 'respaldos',
    component: RespaldosView,
  },
  {
    // Cualquier otra dirección muestra la página de no encontrado.
    path: '/:pathMatch(.*)*',
    name: 'no-encontrado',
    component: NotFoundView,
  },
]

// Creamos la instancia del enrutador.
const router = createRouter({
  // Configuramos el historial de navegación del navegador.
  history: createWebHistory(import.meta.env.BASE_URL),

  // Registramos las rutas disponibles.
  routes,
})

// Exportamos el enrutador para utilizarlo en main.ts.
export default router
