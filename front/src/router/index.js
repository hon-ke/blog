import { createRouter, createWebHistory } from 'vue-router'

import Index from '../views/Index.vue'
import Archives from '../views/Archives.vue'
import Post from '../views/Post.vue'

import Layout from '../components/Layout.vue'
import Edit from '../views/Edit.vue'
import icons from '../views/icons.vue'
import NoteList from '../views/NoteList.vue'
import PostList from '../views/PostList.vue'
import Search from '../components/Search.vue'
import Page from '../views/Page.vue'
import Links from '../views/Links.vue'

const routes = [
  // 3. 定义一个父路由，其路径为根路径 '/'，组件为 Layout
  {
    path: '/',
    component: Layout, // 所有子路由都将共享这个布局

    children: [
      // 4. 将您原有的所有路由定义移至 children 数组中
      {
        path: '', // 空路径代表默认子路由，即当访问 '/' 时显示
        name: 'index',
        component: Index,
        meta: {
          title: '首页 - 红客路上'
        },
      },
      {
        path: '/归档',
        name: 'archives',
        component: Archives,
        meta: {
          title: '归档 - 红客路上'
        },
      },
      {
        path: '/category/笔记',
        name: 'note',
        component: NoteList,
        meta: {
          title: '笔记清单 - 红客路上'
        },
      },
      {
        path: '/category/:name',
        name: 'list',
        component: PostList
      },

    ]
  },


  {
    path: '/search',
    name: 'search',
    component: Search,
    meta: {
      title: '搜索 - 红客路上'
    },
  },

  {
    path: '/post/:id',
    name: 'post',
    component: Post
  },

  {
    path: '/edit', // 空路径代表默认子路由，即当访问 '/' 时显示
    name: 'edit',
    component: Edit,
    meta: {
      title: '编辑 - 红客路上'
    },
  },
  {
    path: '/icons', // 空路径代表默认子路由，即当访问 '/' 时显示
    name: 'icons',
    component: icons,
    meta: {
      title: 'icons - 红客路上'
    },
  },
  {
    path: '/:pathMatch(.*)*',
    name: '404',
    component: Page
  },
]
const router = createRouter({
  history: createWebHistory(),
  routes
})


export default router
