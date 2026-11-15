
<script setup lang="ts">
// Importamos los componentes que formarán la estructura principal.
import Sidebar from './components/layout/Sidebar.vue'
import Header from './components/layout/Header.vue'
</script>

<template>
  <!-- Contenedor general de toda la aplicación -->
  <div class="app-layout">

    <!-- Menú lateral de navegación -->
    <Sidebar />

    <!-- Área principal de contenido -->
    <div class="main-container">

      <!-- Encabezado superior -->
      <Header />

      <!-- Aquí aparecerán las diferentes páginas del sistema -->
      <main class="main-content">
        <RouterView />
      </main>

    </div>
  </div>
</template>

<style>
/* Eliminamos los márgenes predeterminados del navegador */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: "Segoe UI", Arial, Helvetica, sans-serif;
  background-color: #f1f5f9;
}

/* Distribución general: menú lateral y contenido */
.app-layout {
  display: flex;
  min-height: 100vh;
}

/* Contenedor de la parte derecha */
.main-container {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

/* Área donde se mostrarán las páginas */
.main-content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
}
</style>
