<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()

const modulosPendientes = new Set(['/alertas', '/historial', '/respaldos'])

const esModuloPendiente = computed(() => modulosPendientes.has(route.path))
</script>

<template>
  <section class="no-encontrado">
    <p class="codigo">404</p>
    <h1>
      {{
        esModuloPendiente
          ? 'Esta sección todavía no está disponible'
          : 'No encontramos esta página'
      }}
    </h1>
    <p>
      {{
        esModuloPendiente
          ? 'El módulo sigue en el menú y se desarrollará en una fase posterior.'
          : 'La dirección no corresponde a ninguna pantalla del sistema.'
      }}
    </p>
    <RouterLink class="regreso" to="/">Volver al dashboard</RouterLink>
  </section>
</template>

<style scoped>
.no-encontrado {
  max-width: 560px;
  padding: 32px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

.codigo {
  margin: 0 0 8px;
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0 0 10px;
  color: #1e293b;
  font-size: 26px;
}

p {
  margin: 0;
  color: #64748b;
  line-height: 1.5;
}

.regreso {
  display: inline-block;
  margin-top: 22px;
  padding: 10px 16px;
  border-radius: 8px;
  background: #2563eb;
  color: #ffffff;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
}

.regreso:hover {
  background: #1d4ed8;
}
</style>
