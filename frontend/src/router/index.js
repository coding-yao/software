import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/login.vue'),
    },
    {
      path: '/main',
      name: 'main',
      component: () => import('../views/mainpage.vue'),
    },
    {
      path: '/underwater',
      name: 'underwater',
      component: () => import('../views/underwater.vue'),
    },
    {
      path: '/smarthub',
      name: 'smarthub',
      component: () => import('../views/smarthub.vue'),
    },

  ],
})

export default router
