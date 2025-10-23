import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue'
import PostView from '../views/PostView.vue'

import CaregoryView from '@/views/CaregoryView.vue'
const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/post/:title',
    name: 'post',
    component: PostView
  }, {
    path: '/category/:name',
    name: 'category',
    component: CaregoryView
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
