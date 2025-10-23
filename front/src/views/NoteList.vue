<template>
    <div id="notes" class="d-flex">
        <main class="notes-core">
            <div class="notes-list" style="opacity: 1;">
                <Loading v-show="loading" :visible="loading" :count="3" />
                <!-- note -->
                <div v-show="!loading" v-for="post in data" :key="post.id" class="notes-item" style="margin-top: 15px;">

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
                </div>

                <Dialog v-model:visible="active" :article="currentNote"></Dialog>
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




                <Empty v-show="data.length === 0"></Empty>

            </div>
        </main>
    </div>
</template>



<script setup>
import { onMounted, ref, computed } from 'vue';
import axios from 'axios';
import Loading from '../components/Loading.vue';
import { formatTime } from '../assets/js/tools';
import { md } from '@/assets/js/marked-wrapper'
import { Fancybox } from "@fancyapps/ui/dist/fancybox/";
import Empty from '../components/Empty.vue';
import Dialog from '../components/Dialog.vue';

import "@fancyapps/ui/dist/fancybox/fancybox.css";
Fancybox.bind("[data-fancybox]", {
    // Your custom options
});

const name = "笔记";

// 数据相关
const loading = ref(false)
const loadingMore = ref(false)
const data = ref([])

// 分页相关
const currentPage = ref(1)
const total_page = ref(1)
const total = ref(0)


// dialog相关
const active = ref(false)
const currentNote = ref({})

const showDialog = (note) => {
    currentNote.value = note
    active.value = true
}

// 主页的筛选器

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
const loadPage = async (page = 1, type = name) => {
    if (loadingMore.value) return

    loadingMore.value = true
    if (page === 1) {
        loading.value = true
    }

    try {
        let apiUrl = `/api/posts/?category=${name}&page=${page}&size=15`
        if (type && type !== "最新") {
            apiUrl += `&type=${type}`
        }

        const response = await axios.get(apiUrl)
        const responseData = response.data
        console.log(responseData);


        data.value = responseData.posts || []
        currentPage.value = responseData.current_page
        total_page.value = responseData.total_page
        total.value = responseData.total

        // 滚动到顶部（如果不是第一页）
        if (page > 1) {
            window.scrollTo({ top: 0, behavior: 'smooth' })
        }

    } catch (error) {
        console.error('加载数据失败:', error)
        data.value = []
    } finally {
        loading.value = false
        loadingMore.value = false
    }
}

// 跳转到指定页码
const goToPage = (page) => {
    if (page < 1 || page > total_page.value || page === currentPage.value) return
    loadPage(page)
}


function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

onMounted(() => {
    loadPage(1, name)
})
</script>

<style>
.note-body {
    padding: 0;
}

.markdown-body>h1:first-child,
.markdown-body>h2:first-child,
.markdown-body>h3:first-child,
.markdown-body>h4:first-child,
.markdown-body>h5:first-child,
.markdown-body>h6:first-child {
    margin-top: 10px;
}

/* 分页样式 */
.pagination-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 2rem;
    gap: 1rem;
}

.pagination {
    display: flex;
    list-style: none;
    padding: 0;
    margin: 0;
    gap: 4px;
}

.page-item {
    margin: 0;
}

.page-item a,
.page-item span {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 36px;
    height: 36px;
    padding: 0 8px;
    /* border: 1px solid #e1e4e8; */
    border-radius: 4px;
    color: #586069;
    text-decoration: none;
    font-size: 14px;
    transition: all 0.2s ease;
}

.page-item a:hover {
    background-color: #f6f8fa;
    border-color: #d1d5da;
}

.page-item.active a {
    background-color: #0366d6;
    border-color: #0366d6;
    color: white;
}

.page-item.disabled a,
.page-item.disabled span {
    opacity: 0.5;
    pointer-events: none;
    cursor: not-allowed;
    background-color: #f6f8fa;
}

.load-more-indicator {
    border-top: 1px solid rgba(188, 195, 206, 0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .pagination {
        flex-wrap: wrap;
        justify-content: center;
    }

    .page-item a,
    .page-item span {
        min-width: 32px;
        height: 32px;
        font-size: 12px;
    }
}
</style>