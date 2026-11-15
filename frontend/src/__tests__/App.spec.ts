import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'

import App from '../App.vue'

describe('App', () => {
  it('muestra la estructura principal del sistema', async () => {
    const router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<p>Inicio de prueba</p>' } },
      ],
    })

    const wrapper = mount(App, {
      global: {
        plugins: [createPinia(), router],
      },
    })

    await router.isReady()

    expect(wrapper.text()).toContain('Bitácora de Soporte')
    expect(wrapper.text()).toContain('Dashboard')
  })
})
