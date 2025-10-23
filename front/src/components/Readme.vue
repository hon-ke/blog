<template>
  <div v-if="modelValue" class="readme-container" @click.self="handleBackgroundClick">
    <!-- 半透明遮罩层 -->
    <div class="mask" :class="{ active: modelValue }" @click="handleBackgroundClick"></div>
    
    <!-- 内容区域 -->
    <div class="readme-content">
      <div class="readme-card">
        <!-- 关闭按钮 -->
        <button class="close-btn" @click="close">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        
        <!-- README 内容 -->
        <div class="readme-header">
          <h1 class="readme-title">项目 README</h1>
          <p class="readme-subtitle">项目说明文档</p>
        </div>
        
        <div class="readme-body">
          <!-- 项目简介 -->
          <section class="readme-section">
            <h2>项目简介</h2>
            <p>这是一个基于 Vue 3 开发的现代化 Web 应用，采用了最新的前端技术和最佳实践。</p>
          </section>
          
          <!-- 功能特性 -->
          <section class="readme-section">
            <h2>功能特性</h2>
            <ul>
              <li>⚡️ 基于 Vue 3 + Vite 构建</li>
              <li>🎨 现代化 UI 设计</li>
              <li>📱 完全响应式布局</li>
              <li>🔍 智能搜索功能</li>
              <li>🎯 直观的用户界面</li>
            </ul>
          </section>
          
          <!-- 快速开始 -->
          <section class="readme-section">
            <h2>快速开始</h2>
            <div class="code-block">
              <pre><code># 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build</code></pre>
            </div>
          </section>
          
          <!-- 项目结构 -->
          <section class="readme-section">
            <h2>项目结构</h2>
            <div class="file-structure">
              <div class="file-item">📁 src/</div>
              <div class="file-item indent">📁 components/ - 可复用组件</div>
              <div class="file-item indent">📁 views/ - 页面组件</div>
              <div class="file-item indent">📁 assets/ - 静态资源</div>
              <div class="file-item indent">📁 utils/ - 工具函数</div>
            </div>
          </section>
          
          <!-- 技术栈 -->
          <section class="readme-section">
            <h2>技术栈</h2>
            <div class="tech-stack">
              <span class="tech-tag">Vue 3</span>
              <span class="tech-tag">TypeScript</span>
              <span class="tech-tag">Vite</span>
              <span class="tech-tag">ESLint</span>
            </div>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 定义组件属性
const props = defineProps({
  // 控制组件显示/隐藏
  modelValue: {
    type: Boolean,
    default: false
  },
  // 是否允许点击背景关闭
  closeOnBackdrop: {
    type: Boolean,
    default: true
  }
})

// 定义组件事件
const emit = defineEmits(['update:modelValue', 'close'])

// 关闭组件
const close = () => {
  emit('update:modelValue', false)
  emit('close')
}

// 处理背景点击
const handleBackgroundClick = () => {
  if (props.closeOnBackdrop) {
    close()
  }
}
</script>

<style scoped>
.readme-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 1000;
  transition: all .35s ease;
}

.readme-content {
  position: relative;
  z-index: 1001;
  width: 90%;
  max-width: 1000px;
  max-height: 90vh;
  animation: slideUp 0.35s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(100px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.readme-card {
  /* background: rgba(255, 255, 255, 0.15); */
  /* backdrop-filter: blur(20px);*/
  border-radius: var(--radius-wrap);
  padding: 40px;
  /* box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2); */
  color: white;
  position: relative;
  max-height: 90vh;
  overflow-y: auto;
}

.close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 10;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.readme-header {
  text-align: center;
  margin-bottom: 30px;
  padding-right: 50px; /* 为关闭按钮留出空间 */
}

.readme-title {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 10px;
}

.readme-subtitle {
  opacity: 0.8;
  font-size: 1.1rem;
}

.readme-body {
  line-height: 1.6;
}

.readme-section {
  margin-bottom: 30px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-wrap);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.readme-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.readme-section p {
  margin-bottom: 15px;
  opacity: 0.9;
}

.readme-section ul {
  margin-left: 20px;
  margin-bottom: 15px;
}

.readme-section li {
  margin-bottom: 8px;
  opacity: 0.9;
}

.code-block {
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-wrap);
  padding: 15px;
  overflow-x: auto;
  margin: 15px 0;
  backdrop-filter: blur(5px);
}

.code-block pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  opacity: 0.9;
}

.file-structure {
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-wrap);
  padding: 15px;
  font-family: 'Courier New', monospace;
  backdrop-filter: blur(5px);
}

.file-item {
  margin-bottom: 5px;
  opacity: 0.9;
}

.indent {
  margin-left: 20px;
}

.tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tech-tag {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 8px 15px;
  border-radius: var(--radius-wrap);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.tech-tag:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .readme-card {
    padding: 25px;
  }
  
  .readme-title {
    font-size: 2rem;
  }
  
  .readme-header {
    padding-right: 0;
  }
  
  .close-btn {
    position: relative;
    top: auto;
    right: auto;
    margin-bottom: 20px;
  }
}

@media (max-width: 480px) {
  .readme-card {
    padding: 20px;
  }
  
  .readme-title {
    font-size: 1.8rem;
  }
  
  .readme-section h2 {
    font-size: 1.3rem;
  }
  
  .tech-stack {
    justify-content: center;
  }
  
  .readme-section {
    padding: 15px;
  }
}
</style>