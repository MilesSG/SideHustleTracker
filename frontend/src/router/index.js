import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Overview',
    component: () => import('../views/Overview.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 