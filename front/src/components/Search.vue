<template>
    <div v-if="modelValue" class="search-page" @click.self="handleBackgroundClick">
        <!-- 半透明全屏背景 -->
        <div class="mask active" @click="close"></div>

        <!-- 内容区域 -->
        <div class="search-container">
            <div class="search-card">
                <div class="header-section">
                    <h1 class="title" v-if="title.length > 0">{{ title }}</h1>
                    <p class="subtitle" v-if="subtitle.length > 0">{{ subtitle }}</p>
                </div>

                <!-- 搜索框 -->
                <div class="search-box">
                    <div class="input-container">
                        <input v-model="searchQuery" type="text" :placeholder="placeholder" class="search-input"
                            @input="handleSearch" ref="searchInput">
                        <span class="search-icon">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M11 19C15.4183 19 19 15.4183 19 11C19 6.58172 15.4183 3 11 3C6.58172 3 3 6.58172 3 11C3 15.4183 6.58172 19 11 19Z"
                                    stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" />
                                <path d="M21 21L16.65 16.65" stroke="currentColor" stroke-width="2"
                                    stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                        </span>
                    </div>
                </div>

                <!-- 搜索状态 -->
                <div class="search-status">
                    <div v-if="isSearching" class="loading-indicator">
                        <div class="spinner"></div>
                        <span>正在搜索中...</span>
                    </div>

                    <div v-else-if="searchQuery && searchResults.length === 0" class="no-results">
                        <p>没有找到与 <strong>{{ searchQuery }}</strong> 相关的结果</p>
                    </div>
                </div>

                <!-- 搜索结果 -->
                <div v-if="searchResults.length > 0" class="results-container">
                    <h3 class="results-title">搜索结果 ({{ searchResults.length }})</h3>
                    <div class="results-list">
                        <a v-for="(result, index) in searchResults" :key="result.id" :href="`/post/${result.id}`"
                            class="result-item" :style="{ animationDelay: `${index * 0.05}s` }">
                            <div class="result-icon">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                                    xmlns="http://www.w3.org/2000/svg">
                                    <path
                                        d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z"
                                        stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                        stroke-linejoin="round" />
                                    <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2"
                                        stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                            </div>
                            <div class="result-content">
                                <h4>result</h4>
                                <!-- <p v-if="result.excerpt" v-html="result.excerpt"></p> -->
                                <p  class="markdown-body search-content"
                                    v-html="md.parse(result.content)"></p>

                            </div>
                        </a>
                    </div>
                </div>

                <!-- 热门搜索 -->
                <div v-if="!searchQuery" class="popular-searches">
                    <h3 class="popular-title">热门搜索</h3>
                    <div class="popular-tags">
                        <span v-for="(tag, index) in popularTags" :key="index" class="popular-tag-item"
                            @click="selectTag(tag)">
                            {{ tag }}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import axios from 'axios'
import { formatTime } from '@/assets/js/tools'
import { md } from '@/assets/js/marked-wrapper'

// 定义组件属性
const props = defineProps({
    modelValue: {
        type: Boolean,
        default: false
    },
    title: {
        type: String,
        default: '搜索文章'
    },
    subtitle: {
        type: String,
        default: '搜索你感兴趣的内容'
    },
    placeholder: {
        type: String,
        default: '请输入搜索内容...'
    },
    tags: {
        type: Array,
        default: () => ['Python', 'JavaScript', 'Vue', 'React', 'CSS', 'Node.js']
    },
    closeOnBackdrop: {
        type: Boolean,
        default: true
    }
})

// 定义组件事件
const emit = defineEmits(['update:modelValue', 'close', 'search', 'select'])

// 响应式数据
const searchQuery = ref('')
const isSearching = ref(false)
const searchInput = ref(null)
const searchResults = ref([])

const popularTags = computed(() => props.tags)

// 搜索功能
let searchTimeout

const handleSearch = async () => {
    clearTimeout(searchTimeout)

    if (!searchQuery.value) {
        isSearching.value = false
        searchResults.value = []
        return
    }

    isSearching.value = true

    searchTimeout = setTimeout(async () => {
        try {
            const response = await axios.get(`/api/posts/search?q=${encodeURIComponent(searchQuery.value)}`)
            searchResults.value = response.data
            console.log(searchResults.value);

            emit('search', searchQuery.value)
        } catch (error) {
            console.error('搜索失败:', error)
            searchResults.value = []
        } finally {
            isSearching.value = false
        }
    }, 600)
}

// 选择热门标签
const selectTag = (tag) => {
    searchQuery.value = tag
    emit('select', tag)
}

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

// 监听显示状态变化，自动聚焦搜索框
watch(() => props.modelValue, (newVal) => {
    if (newVal) {
        nextTick(() => {
            searchInput.value?.focus()
        })
    } else {
        // 关闭时清空搜索
        searchQuery.value = ''
        isSearching.value = false
        searchResults.value = []
    }
})

// 组件挂载后自动聚焦搜索框
onMounted(() => {
    if (props.modelValue) {
        nextTick(() => {
            searchInput.value?.focus()
        })
    }
})
</script>

<style scoped>
.mask.slideout {
    z-index: 6;
}

.mask.active {
    visibility: visible;
    opacity: 1;
}

.mask {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 2;
    background: rgba(48, 55, 66, 0.5);
    -webkit-backdrop-filter: blur(8px);
    backdrop-filter: blur(8px);
    opacity: 0;
    visibility: hidden;
    -webkit-transition: visibility .35s, opacity .35s;
    transition: visibility .35s, opacity .35s;
}

.search-page {
    --radius-wrap: 8px;
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

.search-container {
    width: 100%;
    z-index: 12138;
    max-width: 900px;
    position: relative;
    font-size: 16px;
}

.search-card {
    border-radius: var(--radius-wrap);
    padding: 40px;
    color: white;
    position: relative;
    max-height: 90vh;
    overflow-y: auto;
    animation: slideUp 0.35s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
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

.header-section {
    position: relative;
    margin-bottom: 20px;
}

.title {
    font-size: 2.5rem;
    margin-bottom: 10px;
    text-align: center;
    font-weight: 700;
}

.subtitle {
    text-align: center;
    margin-bottom: 30px;
    opacity: 0.8;
    font-size: 1.1rem;
}

.search-box {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    gap: 10px;
}

.input-container {
    position: relative;
    flex: 1;
}

.search-input {
    width: 100%;
    padding: 15px 50px 15px 20px;
    border-radius: var(--radius-wrap);
    border: none;
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    color: white;
    font-size: 1rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.search-input::placeholder {
    color: rgba(255, 255, 255, 0.7);
}

.search-input:focus {
    outline: none;
    background: rgba(255, 255, 255, 0.25);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.search-icon {
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
    color: rgba(255, 255, 255, 0.7);
}

.search-status {
    min-height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
}

.loading-indicator {
    display: flex;
    align-items: center;
    gap: 10px;
}

.spinner {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.no-results {
    text-align: center;
    padding: 10px;
}

.no-results strong::before,
.no-results strong::after {
    content: '"';
    display: inline-block;
}

.results-container {
    margin-top: 20px;
}

.results-title {
    margin-bottom: 15px;
    font-size: 1.3rem;
}

.results-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}


.result-item {
    display: flex;
    align-items: flex-start;
    position:relative;
    gap: 15px;
    padding: 15px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-wrap);
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    animation: fadeIn 0.5s ease forwards;
    opacity: 0;
    text-decoration: none;
    color: inherit;
    transition: all 0.3s ease;
}

.result-item:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateY(-2px);
}

.result-item *{
    max-width:100%;
}
.result-icon {
    margin-top: 3px;
    flex-shrink: 0;
}

.result-content {
    flex: 1;
}

.result-content h4 {
    margin: 0 0 8px 0;
    font-size: 1.1rem;
    line-height: 1.4;
}

.result-content p {
    margin: 0 0 8px 0;
    opacity: 0.8;
    font-size: 0.9rem;
    line-height: 1.4;
}

.search-content {
    color: white;
}



.result-meta {
    display: flex;
    gap: 15px;
    font-size: 0.8rem;
    opacity: 0.7;
}

.result-meta .category {
    background: rgba(255, 255, 255, 0.2);
    padding: 2px 8px;
    border-radius: 4px;
}

.popular-searches {
    margin-top: 30px;
}

.popular-title {
    margin-bottom: 15px;
    font-size: 1.3rem;
}

.popular-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.popular-tag-item {
    background: rgba(255, 255, 255, 0.2);
    padding: 8px 15px;
    border-radius: var(--radius-wrap);
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.3s ease;
    backdrop-filter: blur(5px);
}

.popular-tag-item:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .search-card {
        padding: 25px;
    }

    .title {
        font-size: 2rem;
    }

    .search-input {
        padding: 12px 45px 12px 15px;
    }

    .popular-tags {
        justify-content: center;
    }

    .result-meta {
        flex-direction: column;
        gap: 5px;
    }
}

@media (max-width: 480px) {
    .search-card {
        padding: 20px;
    }

    .title {
        font-size: 1.8rem;
    }

    .search-box {
        flex-direction: column;
        align-items: stretch;
    }
}
</style>
