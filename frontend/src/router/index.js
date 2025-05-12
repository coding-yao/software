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
      path: '/page1',
      name: 'page1',
      component: () => import('../views/page1.vue'),
    },
    {
      path: '/page2',
      name: 'page2',
      component: () => import('../views/page2.vue'),
    },

  ],
})

export default router
