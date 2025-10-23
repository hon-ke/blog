<template>
    <div>
        <Loading v-show="loading" :visible="loading" :count="3" />

        <ul class="post-list">

            <li class="post-item" v-for="x in data" :key="x.id">
                <a :href="'/post/' + x.id">
                    <div class="post-title link"><a :href="'/post/' + x.id">{{ x.title }}</a></div>

                    <div class="post-info" :class="{ 'no-cover': !x.cover }">
                        <div class="post-content">
                            <div class="excerpt">{{ x.excerpt }}</div>
                            <div class="post-meta">
                                <time class="mr-2">{{ formatTime(x.created_at) }}</time>
                                <i class="czs-talk">&#160;0</i>
                                <i class="czs-heart">&#160;{{ x.like }}</i>
                            </div>
                        </div>
                        <img class="post-cover" v-if="x.cover" :src="x.cover" alt="">
                    </div>
                </a>
            </li>


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
        </ul>

        <Empty v-show="data.length === 0"></Empty>

    </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue';
import axios from 'axios';
import { formatTime } from '@/assets/js/tools'
import Loading from '../components/Loading.vue';
import Empty from '../components/Empty.vue';
import { useRoute } from 'vue-router';

// 数据相关
const data = ref([])
const route =useRoute()
const loading = ref(false)
const loadingMore = ref(false)

// 分页相关
const currentPage = ref(1)
const total_page = ref(1)
const total = ref(0)

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
const loadPage = async (page = 1) => {
    if (loadingMore.value) return

    loadingMore.value = true
    if (page === 1) {
        loading.value = true
    }

    try {
        const response = await axios.get(`/api/posts/?page=${page}&size=20&category=${route.params.name}`)
        const responseData = response.data

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
    loadPage(1)
    document.title = route.params.name.replace("/","") + " - 红客路上"

})
</script>

<style>
/* .post-item:first-child {
    padding-top: 0px;
} */

.post-item {
    padding: 15px 0;
    border-bottom: 1px solid #eee;
}

.post-item a:hover {
    text-decoration: none;
}

.post-item:hover .post-title a {
    color: #fb6c28;
    text-decoration: none;
}

.post-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.post-title {
    margin-bottom: 15px;
    font-size: 18px;
    line-height: 24px;
}

.post-title a {
    font-size: 18px;
    line-height: 24px;
    -webkit-transition: color .35s;
    transition: color .35s;
    text-decoration: none;

    color: #333 !important;
    color: inherit;
}

.post-info {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 20px;
}

/* 没有封面时的样式 */
.post-info.no-cover {
    justify-content: flex-start;
}

.post-info.no-cover .post-content {
    width: 100%;
}


.post-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 6rem;
    /* 与图片高度保持一致 */
}

.post-cover {
    width: 10rem;
    height: 6rem;
    border-radius: 4px;
    object-fit: cover;
    flex-shrink: 0;
}

.excerpt {
    color: #909399;
    line-height: 1.6em;
    opacity: .85;
    margin-bottom: 10px;
    /* 确保摘要有合适的高度 */
    min-height: 44px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;

    font-size: 15px;
}

.post-meta {
    color: #bcc3ce !important;
    font-size: 0.7rem;
    display: flex;
    align-items: center;
    margin-top: auto;
    /* 确保元信息在底部 */
}

.post-meta time{
    margin-right: 0.7rem;
}

.post-meta i {
    margin-right: 0.7rem;
    text-align: center;
}

/* 分页样式 */

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
    border: 1px solid #e1e4e8;
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
    .post-info {
        flex-direction: column-reverse;
        gap: 10px;
    }

    .post-info.no-cover {
        justify-content: flex-start;
    }

    .post-content {
        min-height: auto;
        width: 100%;
    }

    .post-cover {
        width: 100%;
        height: auto;
        max-height: 200px;
        margin-bottom: 0;
    }

    .excerpt {
        min-height: auto;
        margin-bottom: 8px;
    }

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