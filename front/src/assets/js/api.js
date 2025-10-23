import axios from 'axios'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:3000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 添加认证 token
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// // 响应拦截器
// apiClient.interceptors.response.use(
//   (response) => {
//     return response.data
//   },
//   (error) => {
//     console.error('API Error:', error.response?.data || error.message)
    
//     // 处理常见 HTTP 错误
//     if (error.response?.status === 401) {
//       // 未授权，跳转到登录页
//       localStorage.removeItem('auth_token')
//       window.location.href = '/login'
//     }
    
//     return Promise.reject(error.response?.data || error)
//   }
// )

// 博客文章 API
export const postAPI = {
  /**
   * 获取文章列表
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.limit - 每页数量
   * @param {string} params.category - 分类筛选
   * @param {string} params.tag - 标签筛选
   * @param {string} params.search - 搜索关键词
   */
  getPosts(params = {}) {
    return apiClient.get('/posts', { params })
  },

  /**
   * 获取单篇文章
   * @param {string|number} id - 文章ID或slug
   */
  getPost(id) {
    return apiClient.get(`/posts/${id}`)
  },

  /**
   * 创建文章
   * @param {Object} postData - 文章数据
   */
  createPost(postData) {
    return apiClient.post('/posts', postData)
  },

  /**
   * 更新文章
   * @param {string|number} id - 文章ID
   * @param {Object} postData - 更新的文章数据
   */
  updatePost(id, postData) {
    return apiClient.put(`/posts/${id}`, postData)
  },

  /**
   * 删除文章
   * @param {string|number} id - 文章ID
   */
  deletePost(id) {
    return apiClient.delete(`/posts/${id}`)
  },

  /**
   * 获取热门文章
   * @param {number} limit - 返回数量
   */
  getPopularPosts(limit = 5) {
    return apiClient.get('/posts/popular', { params: { limit } })
  },

  /**
   * 获取相关文章
   * @param {string|number} postId - 当前文章ID
   * @param {number} limit - 返回数量
   */
  getRelatedPosts(postId, limit = 3) {
    return apiClient.get(`/posts/${postId}/related`, { params: { limit } })
  }
}

// 分类 API
export const categoryAPI = {
  /**
   * 获取所有分类
   */
  getCategories() {
    return apiClient.get('/categories')
  },

  /**
   * 获取分类详情
   * @param {string} slug - 分类slug
   */
  getCategory(slug) {
    return apiClient.get(`/categories/${slug}`)
  },

  /**
   * 创建分类
   * @param {Object} categoryData - 分类数据
   */
  createCategory(categoryData) {
    return apiClient.post('/categories', categoryData)
  }
}

// 标签 API
export const tagAPI = {
  /**
   * 获取所有标签
   */
  getTags() {
    return apiClient.get('/tags')
  },

  /**
   * 获取标签详情
   * @param {string} name - 标签名称
   */
  getTag(name) {
    return apiClient.get(`/tags/${name}`)
  }
}

// 评论 API
export const commentAPI = {
  /**
   * 获取文章评论
   * @param {string|number} postId - 文章ID
   */
  getComments(postId) {
    return apiClient.get(`/posts/${postId}/comments`)
  },

  /**
   * 添加评论
   * @param {string|number} postId - 文章ID
   * @param {Object} commentData - 评论数据
   */
  addComment(postId, commentData) {
    return apiClient.post(`/posts/${postId}/comments`, commentData)
  },

  /**
   * 删除评论
   * @param {string|number} commentId - 评论ID
   */
  deleteComment(commentId) {
    return apiClient.delete(`/comments/${commentId}`)
  }
}

// 文件上传 API
export const uploadAPI = {
  /**
   * 上传文件
   * @param {FormData} formData - 文件数据
   * @param {Function} onProgress - 上传进度回调
   */
  uploadFile(formData, onProgress = null) {
    return apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          onProgress(percentCompleted)
        }
      }
    })
  },

  /**
   * 删除文件
   * @param {string} filePath - 文件路径
   */
  deleteFile(filePath) {
    return apiClient.delete('/upload', { data: { filePath } })
  }
}

// 搜索 API
export const searchAPI = {
  /**
   * 搜索文章
   * @param {string} query - 搜索关键词
   * @param {Object} params - 其他参数
   */
  searchPosts(query, params = {}) {
    return apiClient.get('/search', {
      params: { q: query, ...params }
    })
  }
}

// 统计 API
export const statsAPI = {
  /**
   * 获取博客统计信息
   */
  getStats() {
    return apiClient.get('/stats')
  },

  /**
   * 获取文章阅读量
   * @param {string|number} postId - 文章ID
   */
  getPostViews(postId) {
    return apiClient.get(`/posts/${postId}/views`)
  },

  /**
   * 增加文章阅读量
   * @param {string|number} postId - 文章ID
   */
  incrementPostViews(postId) {
    return apiClient.post(`/posts/${postId}/views`)
  }
}

// 认证 API
export const authAPI = {
  /**
   * 用户登录
   * @param {Object} credentials - 登录凭证
   */
  login(credentials) {
    return apiClient.post('/auth/login', credentials)
  },

  /**
   * 用户注册
   * @param {Object} userData - 用户数据
   */
  register(userData) {
    return apiClient.post('/auth/register', userData)
  },

  /**
   * 获取当前用户信息
   */
  getCurrentUser() {
    return apiClient.get('/auth/me')
  },

  /**
   * 刷新 token
   */
  refreshToken() {
    return apiClient.post('/auth/refresh')
  },

  /**
   * 用户退出登录
   */
  logout() {
    return apiClient.post('/auth/logout')
  }
}

// 默认导出所有 API
export default {
  post: postAPI,
  category: categoryAPI,
  tag: tagAPI,
  comment: commentAPI,
  upload: uploadAPI,
  search: searchAPI,
  stats: statsAPI,
  auth: authAPI
}

