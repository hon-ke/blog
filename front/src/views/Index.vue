<template>
    <div id="notes" class="d-flex">
        <main class="notes-core">
            <!-- <div class="notes-tabbar sticky bg-blur" :class="{ active: isTabbarActive }" ref="scrollContainer">
                <ul class="tab">
                    <li v-for="tab in tabs" :key="tab.value" class="tab-item"
                        :class="{ active: menu_type === tab.value }" @click="changeMenuType(tab.value)">
                        <a>{{ tab.label }}</a>
                    </li>
                    <span class="chip text-primary" v-if="filter_type">
                        {{ filter_type }}
                        <a aria-label="Close" role="button" @click="filter_type = ''" class="btn btn-clear"></a>
                    </span>
                </ul>
            </div> -->

            <div class="notes-list" style="opacity: 1;">
                <ul class="post-list" v-for="post in loadedData" :key="post.id">

                    <!-- note -->
                    <li v-if="post.category == '笔记'" class="notes-item" style="margin-top: 15px;">

                        <a :href="'/post/' + post.id">

                            <div class="tile d-block">
                                <div class="tile-header flex-center justify-between">
                                    <div class="article-header text-gray text-tiny d-flex align-center">
                                        <!-- note的时间 -->
                                        <div class="flex-center">
                                            <time class="mr-2">{{ formatTime(post.created_at) }}</time>
                                        </div>
                                    </div>
                                </div>

                                <div class="tile-content p-0">
                                    <!-- note的内容 -->
                                    <div class="flex-wrap d-flex">
                                        <div class="note-body markdown-body" v-html="md.parse(post.content)"></div>
                                    </div>
                                </div>

                                <!-- note的info -->
                                <div class="tile-footer text-gray text-tiny flex-center justify-between">
                                    <div class="flex-center">
                                        <button class="btn btn-link btn-sm text-gray mr-2">
                                            <i class="czs-talk"></i>&#160;{{ post.comment_count || 0 }}
                                        </button>
                                        <button class="btn btn-link btn-sm text-gray mr-2">
                                            <i class="czs-heart"></i>
                                            <span class="praise-6020">&#160;{{ post.like || 0 }}</span>
                                        </button>
                                    </div>
                                    <span class="flex-center">
                                        <i class="dashicons dashicons-laptop mr-1"></i> Write from Webpage
                                    </span>
                                </div>
                            </div>
                        </a>
                        <div class="divider"></div>
                    </li>

                    <!-- post -->
                    <li v-else class="post-item" :key="post.id">
                        <a :href="'/post/' + post.id">
                            <div class="post-title link"><a :href="'/post/' + post.id">{{ post.title }}</a></div>

                            <div class="post-info" :class="{ 'no-cover': !post.cover }">
                                <div class="post-content">
                                    <div class="excerpt">{{ post.excerpt }}</div>
                                    <div class="post-meta">
                                        <time class="mr-2">{{ formatTime(post.created_at) }}</time>
                                        <i class="czs-talk">&#160;0</i>
                                        <i class="czs-heart">&#160;{{ post.like }}</i>
                                    </div>
                                </div>
                                <img class="post-cover" v-if="post.cover" :src="post.cover" alt="">
                            </div>
                        </a>
                    </li>
                </ul>


                <!-- 分页器 -->
                <div v-if="total_page > 1" class="pagination-container">
                    <ul class="pagination">
                        <!-- 上一页 -->
                        <li class="page-item" :class="{ disabled: currentPage <= 1 }">
                            <a href="javascript:void(0)" @click="goToPage(currentPage - 1)">‹</a>
                        </li>

                        <!-- 第一页 -->
                        <li v-if="currentPage > 3" class="page-item">
                            <a href="javascript:void(0)" @click="goToPage(1)">1</a>
                        </li>
                        <li v-if="currentPage > 4" class="page-item disabled">
                            <span>...</span>
                        </li>

                        <!-- 中间页码 -->
                        <li v-for="pageNum in displayedPages" :key="pageNum" class="page-item"
                            :class="{ active: pageNum === currentPage }">
                            <a href="javascript:void(0)" @click="goToPage(pageNum)">{{ pageNum }}</a>
                        </li>

                        <!-- 最后一页 -->
                        <li v-if="currentPage < total_page - 3" class="page-item disabled">
                            <span>...</span>
                        </li>
                        <li v-if="currentPage < total_page - 2" class="page-item">
                            <a href="javascript:void(0)" @click="goToPage(total_page)">{{ total_page }}</a>
                        </li>

                        <!-- 下一页 -->
                        <li class="page-item" :class="{ disabled: currentPage >= total_page }">
                            <a href="javascript:void(0)" @click="goToPage(currentPage + 1)">›</a>
                        </li>
                    </ul>
                </div>

                <!-- 加载更多指示器 -->
                <div v-if="loadingMore" class="load-more-indicator text-center py-3">
                    <div class="loading loading-lg"></div>
                    <div class="text-gray text-tiny mt-2">加载中...</div>
                </div>
            </div>

            <Empty v-if="loadedData.length === 0" />

            <!-- 初始加载指示器 -->
            <Loading v-if="loading && loadedData.length === 0" />
        </main>
    </div>
</template>

<script setup>
import Loading from '../components/Loading.vue';
import { ref, onMounted, onUnmounted, computed } from 'vue'
import axios from 'axios';
import { formatTime } from '@/assets/js/tools'
import { md } from '@/assets/js/marked-wrapper'
import { Fancybox } from "@fancyapps/ui/dist/fancybox/";
import Empty from '../components/Empty.vue';

import "@fancyapps/ui/dist/fancybox/fancybox.css";
Fancybox.bind("[data-fancybox]", {
    // Your custom options
});

const loading = ref(true)
const loadingMore = ref(false)
const isTabbarActive = ref(false)

// 分页相关
const currentPage = ref(1)
const total_page = ref(1)
const total = ref(0)

// 数据相关
const menu_type = ref("最新")
const filter_type = ref("")
const loadedData = ref([]) // 当前已加载的数据

const tabs = [
    { label: '最新', value: '最新' },
    { label: '文章', value: '文章' },
    { label: '笔记', value: '笔记' },
    { label: '朋友圈', value: '朋友圈' }
]

// 计算显示的页码
const displayedPages = computed(() => {
    const pages = []
    const totalPages = total_page.value
    const current = currentPage.value

    let startPage = Math.max(1, current - 2)
    let endPage = Math.min(totalPages, current + 2)

    // 调整起始和结束页码以确保显示5个页码（如果可能）
    if (endPage - startPage < 4) {
        if (current < 3) {
            endPage = Math.min(totalPages, 5)
        } else if (current > totalPages - 2) {
            startPage = Math.max(1, totalPages - 4)
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        pages.push(i)
    }

    return pages
})

// 加载指定页面的数据
const loadPage = async (page = 1, category = menu_type.value) => {
    if (loadingMore.value) return

    loadingMore.value = true
    if (page === 1) {
        loading.value = true
    }

    try {
        let apiUrl = `/api/posts/?page=${page}`
        if (category !== "最新") {
            apiUrl += `&category=${category}`
        }

        const response = await axios.get(apiUrl)
        const data = response.data

        const posts = data.posts || []

        // 更新数据
        loadedData.value = posts
        currentPage.value = data.current_page
        total_page.value = data.total_page
        total.value = data.total

        // 滚动到顶部
        window.scrollTo({ top: 0, behavior: 'smooth' })

    } catch (error) {
        console.error('加载数据失败:', error)
        loadedData.value = []
    } finally {
        loadingMore.value = false
        loading.value = false
    }
}

// 跳转到指定页码
const goToPage = (page) => {
    if (page < 1 || page > total_page.value || page === currentPage.value) return
    loadPage(page)
}

// 切换分类
const changeMenuType = async (value) => {
    menu_type.value = value
    currentPage.value = 1
    await loadPage(1, value)
}

function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

const handleScroll = () => {
    isTabbarActive.value = window.scrollY > 16
}

onMounted(async () => {
    // 初始加载第一页
    await loadPage(1)

    window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll)
})
</script>