<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  estado: string | null | undefined
}>()

const clave = computed(() => {
  const valor = (props.estado ?? '').trim().toLowerCase()

  if (valor === 'activo') {
    return 'activo'
  }

  if (valor === 'inactivo') {
    return 'inactivo'
  }

  return 'neutro'
})

const texto = computed(() => {
  const valor = (props.estado ?? '').trim()
  return valor || 'Sin estado'
})
</script>

<template>
  <span class="estado" :class="clave">{{ texto }}</span>
</template>

<style scoped>
.estado {
  display: inline-block;
  padding: 5px 10px;
  border-radius: 999px;
  background-color: #e2e8f0;
  color: #475569;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.activo {
  background-color: #dcfce7;
  color: #166534;
}

.inactivo {
  background-color: #fee2e2;
  color: #991b1b;
}
</style>
