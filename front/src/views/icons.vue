<template>
    <div class="icon-viewer">
        <!-- 固定顶部搜索栏 -->
        <div class="header">
            <div class="header-content">
                <div class="search-section">
                    <div class="search-box">
                        <i class="czs-search-l"></i>
                        <input type="text" v-model="searchQuery" placeholder="搜索图标名称...">
                    </div>
                    <div class="stats">
                        显示 {{ filteredIcons.length }} / {{ icons.length }}
                    </div>
                </div>
            </div>
        </div>

        <!-- 内容区域 -->
        <div class="content-wrapper">
            <div class="icons-grid">
                <div v-for="icon in filteredIcons" :key="icon.className" class="icon-item"
                    @click="copyClassName(icon.className)">
                    <div class="icon-wrapper">
                        <i :class="icon.className"></i>
                    </div>
                    <span class="icon-name">{{ icon.className }}</span>
                </div>
            </div>

            <div class="footer">
                <p>点击任意图标即可复制其类名到剪贴板</p>
            </div>
        </div>

        <!-- Toastify 风格 Toast -->
        <div class="toast" :class="{ 'show': showToast }">
            <i :class="selectedIcon" class="selected-icon"></i>已复制
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 使用 require 和 raw-loader 导入 CSS 内容
const cssText = require('!!raw-loader!@/assets/css/icons.css').default

// 存储图标的响应式数组
const icons = ref([])
const searchQuery = ref('')
const showToast = ref(false)
const selectedIcon = ref("")

// 过滤图标
const filteredIcons = computed(() => {
    if (!searchQuery.value) return icons.value
    return icons.value.filter(icon =>
        icon.className.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
})

// 从 CSS 文本中解析图标
const parseIconsFromCSS = (cssText) => {
    const iconList = []

    // 正则表达式匹配 .czs- 开头的类及其 content
    const regex = /\.(czs-[^\s:{]+)[^{]*\{[^}]*content:\s*["']\\([^"']+)["']/g
    let match

    while ((match = regex.exec(cssText)) !== null) {
        const className = match[1]
        const unicode = match[2]

        iconList.push({
            className: className,
            unicode: unicode
        })
    }

    // 按类名排序
    iconList.sort((a, b) => a.className.localeCompare(b.className))
    icons.value = iconList

    console.log(`找到 ${iconList.length} 个图标`)
}

// 复制类名功能
const copyClassName = async (className) => {
    try {
        await navigator.clipboard.writeText(className)
        selectedIcon.value = className
        showToast.value = true

        // 2秒后隐藏提示
        setTimeout(() => {
            showToast.value = false
        }, 3000)
    } catch (err) {
        console.error('复制失败:', err)
        // 降级方案
        const textArea = document.createElement('textarea')
        textArea.value = className
        document.body.appendChild(textArea)
        textArea.select()
        document.execCommand('copy')
        document.body.removeChild(textArea)

        showToast.value = true

        setTimeout(() => {
            showToast.value = false
        }, 3000)
    }
}

// 组件挂载时解析图标
onMounted(() => {
    parseIconsFromCSS(cssText)
})
</script>

<style scoped>
@import url(@/assets/css/icons.css);

.icon-viewer {
    background: #f8f9fa;
    min-height: 100vh;
}

/* 固定头部样式 */
.header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    background: white;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    padding: 15px 20px;
    border-bottom: 1px solid #eaecef;
}

.header-content {
    max-width: 1200px;
    margin: 0 auto;
}

.search-section {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
}

/* 简约边框搜索框样式 */
.search-box {
    position: relative;
    flex: 1;
    max-width: 500px;
}

.search-box i {
    position: absolute;
    left: 16px;
    top: 50%;
    transform: translateY(-50%);
    color: #6b7280;
    font-size: 16px;
    transition: all 0.3s ease;
}

.search-box input {
    width: 100%;
    padding: 12px 16px 12px 42px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 14px;
    transition: all 0.3s ease;
    background: white;
    color: #374151;
}

.search-box input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.search-box input:hover {
    border-color: #9ca3af;
}

.search-box input::placeholder {
    color: #9ca3af;
}

.stats {
    color: #6b7280;
    font-size: 0.85rem;
    white-space: nowrap;
    font-weight: 500;
}

/* 内容区域 */
.content-wrapper {
    max-width: 1200px;
    margin: 0 auto;
    padding: 95px 20px 20px;
}

.icons-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 16px;
    margin-bottom: 30px;
}

.icon-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 10px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    min-height: 120px;
    border: 1px solid #f3f4f6;
}

.icon-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    border-color: #e5e7eb;
}

.icon-wrapper {
    margin-bottom: 12px;
    flex-shrink: 0;
}

.icon-item i {
    font-size: 32px;
    color: #374151;
    transition: color 0.3s ease;
}

.icon-item:hover i {
    color: #3b82f6;
}

.icon-name {
    font-size: 12px;
    text-align: center;
    color: #6b7280;
    word-break: break-word;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    line-height: 1.3;
    flex-grow: 1;
    display: flex;
    align-items: center;
}

/* Toastify 风格 Toast */
.toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: #10b981;
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    display: flex;
    align-items: center;
    gap: 10px;
    transform: translateX(400px);
    opacity: 0;
    transition: all 0.3s ease;
    z-index: 1000;
    max-width: 140px;
    border: none;
}

.toast.show {
    transform: translateX(0);
    opacity: 1;
}

.toast .selected-icon{
    font-size:20px;
}
.footer {
    text-align: center;
    padding: 20px;
    color: #6b7280;
    font-size: 0.85rem;
    margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .header {
        padding: 12px 16px;
    }

    .search-section {
        gap: 15px;
    }

    .search-box input {
        padding: 10px 14px 10px 40px;
        font-size: 13px;
    }

    .stats {
        font-size: 0.8rem;
    }

    .content-wrapper {
        padding: 90px 16px 16px;
    }

    .toast {
        top: 15px;
        right: 15px;
        left: 15px;
        transform: translateY(-100px);
        text-align: center;
    }

    .toast.show {
        transform: translateY(0);
    }
}

@media (max-width: 480px) {
    .header {
        padding: 10px 12px;
    }

    .content-wrapper {
        padding: 85px 12px 12px;
    }

    .icons-grid {
        grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
        gap: 8px;
    }

    .icon-item {
        padding: 15px 5px;
        min-height: 100px;
    }

    .icon-item i {
        font-size: 24px;
    }

    .search-box input {
        padding: 8px 12px 8px 38px;
        font-size: 12px;
    }

    .stats {
        font-size: 0.75rem;
    }

    .toast {
        top: 10px;
        right: 10px;
        left: 10px;
        padding: 10px 16px;
        font-size: 13px;
    }
}
</style>