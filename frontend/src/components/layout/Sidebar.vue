
<script setup lang="ts">
// Importamos RouterLink para navegar entre las diferentes vistas
// sin recargar toda la aplicación.
import { RouterLink } from 'vue-router'

// Definimos las opciones que aparecerán en el menú lateral.
const menuItems = [
  { name: 'Dashboard', path: '/', icon: '📊' },
  { name: 'Servidores', path: '/servidores', icon: '🖥️' },
  { name: 'Sucursales', path: '/sucursales', icon: '🏢' },
  { name: 'Equipos', path: '/equipos', icon: '💻' },
  { name: 'Técnicos', path: '/tecnicos', icon: '👨‍🔧' },
  { name: 'Alertas', path: '/alertas', icon: '🔔' },
  { name: 'Historial', path: '/historial', icon: '📋' },
  { name: 'Mantenimientos', path: '/mantenimientos', icon: '🛠️' },
  { name: 'Respaldos', path: '/respaldos', icon: '💾' },
]
</script>

<template>
  <!-- Contenedor principal del menú lateral -->
  <aside class="sidebar">

    <!-- Nombre e identificación del sistema -->
    <div class="brand">
      <div class="brand-icon">DS</div>
      <div>
        <h2>Bitácora de Soporte</h2>
        <span>Monitoreo de servidores</span>
      </div>
    </div>

    <!-- Navegación principal -->
    <nav class="navigation">
      <p class="section-title">MENÚ PRINCIPAL</p>

      <!-- Recorremos las opciones para generar los enlaces -->
      <RouterLink
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        custom
        v-slot="{ href, navigate, isActive, isExactActive }"
      >
        <a
          :href="href"
          class="nav-link"
          :class="{ active: item.path === '/' ? isExactActive : isActive }"
          @click="navigate"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span>{{ item.name }}</span>
        </a>
      </RouterLink>
    </nav>

    <!-- Información al pie del menú -->
    <div class="sidebar-footer">
      <span class="status-indicator"></span>
      <span>Sistema de soporte técnico</span>
    </div>
  </aside>
</template>

<style scoped>
/* Contenedor general de la barra lateral */
.sidebar {
  width: 260px;
  min-height: 100vh;
  background-color: #172033;
  color: #ffffff;
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  box-sizing: border-box;
}

/* Identidad visual del sistema */
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 4px 30px;
}

.brand-icon {
  width: 42px;
  height: 42px;
  background-color: #2563eb;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 15px;
}

.brand h2 {
  font-size: 14px;
  margin: 0 0 5px;
}

.brand span {
  font-size: 11px;
  color: #aab5c8;
}

/* Menú de navegación */
.navigation {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-title {
  color: #8491a7;
  font-size: 10px;
  font-weight: bold;
  letter-spacing: 1px;
  margin: 0 0 10px 10px;
}

/* Enlaces individuales */
.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  color: #cbd5e1;
  text-decoration: none;
  font-size: 13px;
  transition: background-color 0.2s;
}

/* Efecto cuando el cursor pasa sobre un enlace */
.nav-link:hover {
  background-color: #26344d;
}

/* Estilo de la sección seleccionada */
.nav-link.active {
  background-color: #2563eb;
  color: #ffffff;
}

.nav-icon {
  font-size: 17px;
}

/* Información inferior */
.sidebar-footer {
  margin-top: auto;
  padding: 16px 5px 0;
  border-top: 1px solid #344056;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #aab5c8;
  font-size: 11px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  background-color: #22c55e;
  border-radius: 50%;
}
</style>
