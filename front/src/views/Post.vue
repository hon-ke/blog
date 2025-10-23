<template>
    <Layout>
        <template #core>
            <aside id="aside" class="off-canvas-sidebar">
                <div class="probes"></div>
                <section class="no-sticky">
                    <Heatmap></Heatmap>
                </section>
                <section class="sticky">
                    <ul class="header_nav reset-ul uni-bg uni-shadow">
                        <h3 class="toc-header"><i class="czs-scan-l" title="文章目录"></i>文章目录</h3>
                        <div class="toc-container" v-html="tocHtml" ref="tocContainer"></div>
                    </ul>
                </section>
            </aside>
            <a href="#close" class="off-canvas-overlay"></a>

            <!-- 文章详情 -->
            <main id="main" class="uni-bg uni-shadow off-canvas-content">

                <div class="content">
                    <Loading type="article-detail" v-if="loading" :visible="loading" />

                    <article v-show="!loading" class="article" itemscope="itemscope"
                        itemtype="http://schema.org/Article">
                        <header v-if="post.category!='笔记'" class="article-header">
                            <h1 itemprop="headline" class="article-title h2 mb-2">{{ post.title }}</h1>
                            <ul class="article-info d-flex text-gray reset-ul m-0">
                                <li>
                                    <i class="czs-time"></i>
                                    <time datetime="2019-11-07T14:55:14+08:00" itemprop="datePublished" pubdate=""
                                        title="11/7/2019, 2:55:14 PM">{{ formatTime(post.created_at) }}</time>
                                </li>
                                <li class="c-hand" @click="like(post.id)" :class="{ 'liked': isLiked }">
                                    <i class="czs-heart" :class="{ 'text-red': isLiked }"></i>
                                    <span class="praise">{{ post.like }}</span>
                                </li>
                                <li v-if="loadingLike" class="loading-like">
                                    <i class="czs-loading"></i>
                                </li>
                            </ul>
                            <div class="divider"></div>
                        </header>
                        
                        <div class="markdown-body" itemprop="articleBody" v-html="post.content" view-image=""
                            ref="articleContent">
                        </div>
                    </article>

                    <div v-show="!loading" class="comment-area">
                        <section class="affiliate">
                            <div class="card">
                                <div class="tile tile-centered">
                                    <div class="tile-icon">
                                        <figure data-initial="7" class="avatar avatar-xl">
                                            <img src="@/assets/img/clay.jpg" alt="7doger">
                                            <div class="avatar-icon s-circle">
                                                <button data-tooltip="BLOGGER"
                                                    class="btn btn-warning btn-sm s-circle flex-center tooltip">
                                                    <i class="czs-vimeo"></i>
                                                </button>
                                            </div>
                                        </figure>
                                    </div>
                                    <div class="tile-content my-2 p-0">
                                        <div class="tile-title text-ellipsis">clay</div> 
                                        <small class="text-gray d-block"></small>
                                    </div>
                                    <div class="tile-action flex-center">
                                        <button class="btn btn-action btn-link text-gray flex-center mx-1 like-btn"
                                            @click="like(post.id)" 
                                            :class="{ 'liked': isLiked, 'loading': loadingLike }"
                                            :disabled="loadingLike">
                                            <i class="czs-heart-l" :class="{ 'text-red': isLiked }"></i>
                                        </button>
                                        <div class="popover popover-top mx-1">
                                            <button class="btn btn-action btn-link text-gray flex-center">
                                                <i class="czs-qrcode-l"></i>
                                            </button>
                                            <div class="popover-container" style="width: 100px;">
                                                <div class="card uni-shadow qr-image p-2"
                                                    title="https://www.bigblog.cn/1961.html">
                                                    <canvas width="256" height="256" style="display: none;"></canvas>
                                                    <img style="display: block;" src="@/assets/img/clay.jpg">
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </section>
                    </div>
                </div>

                <Loading v-if="loading" :visible="loading" :count="5" type="comment-list" />
                <Comments v-else :postId="post_id"></Comments>

            </main>
        </template>
    </Layout>
</template>

<script setup>
import { useRoute } from 'vue-router';
import { ref, onMounted, nextTick, onUnmounted } from 'vue';
import axios from 'axios';
import { md } from '@/assets/js/marked-wrapper'
import { formatTime } from '@/assets/js/tools'
import Loading from '../components/Loading.vue';
import Heatmap from '../components/Heatmap.vue';
import Comments from '../components/Comments.vue';
import { Fancybox } from "@fancyapps/ui";
import "@fancyapps/ui/dist/fancybox/fancybox.css";
import Layout from '../components/Layout.vue';

const route = useRoute();
const post_id = route.params.id;
const tocHtml = ref('')
const post = ref({});
const loading = ref(true);
const tocContainer = ref(null);
const articleContent = ref(null);
const watermarkContainer = ref(null);
const currentActiveId = ref('');
const headingElements = ref([]);
const isScrollingToc = ref(false);
const scrollAnimationFrame = ref(null);
const isLiked = ref(false);
const loadingLike = ref(false);

// 防重复点击
let likeCooldown = false;

Fancybox.bind("[data-fancybox]", {
    // Your custom options
});

async function like(post_id) {
    // 防止重复点击
    if (likeCooldown || loadingLike.value || isLiked.value) {
        return;
    }

    // 确保 post_id 是数字
    const postId = parseInt(post_id);

    if (isNaN(postId)) {
        alert('文章ID格式错误');
        return;
    }

    loadingLike.value = true;
    likeCooldown = true;

    try {
        const response = await axios.get(`/api/posts/like?post_id=${postId}`);
        
        if (response.data && response.data.status === 200) {
            // 点赞成功
            isLiked.value = true;
            post.value.like = response.data.like_count;
            
            // 显示成功提示
            showLikeMessage('点赞成功！', 'success');
            
            // 保存点赞状态到本地存储，防止重复点赞
            localStorage.setItem(`liked_post_${postId}`, 'true');
            
        } else {
            showLikeMessage('点赞失败，请稍后重试', 'error');
        }
    } catch (error) {
        console.error('点赞错误:', error);
        
        if (error.response && error.response.status === 404) {
            showLikeMessage('文章不存在', 'error');
        } else {
            showLikeMessage('网络错误，请稍后重试', 'error');
        }
    } finally {
        loadingLike.value = false;
        // 2秒后才能再次点击
        setTimeout(() => {
            likeCooldown = false;
        }, 2000);
    }
}

// 显示点赞消息
function showLikeMessage(message, type = 'info') {
    // 这里可以替换为你喜欢的消息提示组件
    const messageEl = document.createElement('div');
    messageEl.className = `like-message like-message-${type}`;
    messageEl.textContent = message;
    messageEl.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : type === 'warning' ? '#ff9800' : '#2196f3'};
        color: white;
        padding: 12px 20px;
        border-radius: 4px;
        z-index: 10000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(messageEl);
    
    setTimeout(() => {
        messageEl.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (document.body.contains(messageEl)) {
                document.body.removeChild(messageEl);
            }
        }, 300);
    }, 2000);
}

// 检查是否已经点赞过
function checkLikeStatus() {
    const postId = parseInt(post_id);
    if (!isNaN(postId)) {
        isLiked.value = localStorage.getItem(`liked_post_${postId}`) === 'true';
    }
}

function generateToc(html) {
    const div = document.createElement('div');
    div.innerHTML = html;

    const headings = div.querySelectorAll('h2, h3');

    const tocItems = [];

    headings.forEach((heading, index) => {
        if (!heading.id) {
            heading.id = `heading-${index}`;
        }

        tocItems.push({
            id: heading.id,
            level: parseInt(heading.tagName[1]),
            text: heading.textContent
        });
    });

    let tocHtml = '';

    tocItems.forEach(item => {
        const indent = (item.level - 2) * 15;

        tocHtml += `
            <div class="toc-item link" style="margin-left: ${indent}px" data-target="${item.id}">
                ${item.text}
            </div>
        `;
    });

    return tocHtml;
}

function setupTocClickHandlers() {
    const tocItems = document.querySelectorAll('.toc-item');
    tocItems.forEach(item => {
        item.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                // 先移除所有active类
                document.querySelectorAll('.toc-item.active').forEach(el => {
                    el.classList.remove('active');
                });
                // 添加active类到当前点击的项
                this.classList.add('active');
                currentActiveId.value = targetId;

                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function setupScrollTracking() {
    let ticking = false;

    const handleScroll = () => {
        if (!ticking) {
            requestAnimationFrame(() => {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                const viewportHeight = window.innerHeight;
                // 距离顶部多少触发
                const triggerPoint = viewportHeight * 0.08;

                let activeHeading = null;

                // 从下往上找第一个在触发点以上的标题
                for (let i = headingElements.value.length - 1; i >= 0; i--) {
                    const heading = headingElements.value[i];
                    const rect = heading.getBoundingClientRect();
                    const elementTop = rect.top + scrollTop;

                    if (elementTop <= scrollTop + triggerPoint) {
                        activeHeading = heading;
                        break;
                    }
                }

                // 如果没找到，就用第一个标题
                if (!activeHeading && headingElements.value.length > 0) {
                    activeHeading = headingElements.value[0];
                }

                if (activeHeading && activeHeading.id !== currentActiveId.value) {
                    updateActiveTocItem(activeHeading.id);
                }

                ticking = false;
            });

            ticking = true;
        }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });

    // 返回清除函数
    return () => {
        window.removeEventListener('scroll', handleScroll);
    };
}

function smoothScrollTo(element, targetTop, duration = 300) {
    if (scrollAnimationFrame.value) {
        cancelAnimationFrame(scrollAnimationFrame.value);
    }

    const startTop = element.scrollTop;
    const distance = targetTop - startTop;
    const startTime = performance.now();

    function animateScroll(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // 使用easeOutCubic缓动函数
        const easeProgress = 1 - Math.pow(1 - progress, 3);

        element.scrollTop = startTop + (distance * easeProgress);

        if (progress < 1) {
            scrollAnimationFrame.value = requestAnimationFrame(animateScroll);
        } else {
            scrollAnimationFrame.value = null;
            isScrollingToc.value = false;
        }
    }

    isScrollingToc.value = true;
    scrollAnimationFrame.value = requestAnimationFrame(animateScroll);
}

function updateActiveTocItem(id) {
    // 移除所有active类
    document.querySelectorAll('.toc-item.active').forEach(el => {
        el.classList.remove('active');
    });

    // 添加active类到对应的TOC项
    const correspondingTocItem = document.querySelector(`.toc-item[data-target="${id}"]`);
    if (correspondingTocItem) {
        correspondingTocItem.classList.add('active');
        currentActiveId.value = id;

        // 确保活跃项在可视区域内
        const tocContainerEl = tocContainer.value;
        const activeItem = correspondingTocItem;

        if (tocContainerEl && activeItem && !isScrollingToc.value) {
            const containerHeight = tocContainerEl.clientHeight;
            const itemOffsetTop = activeItem.offsetTop;
            const itemHeight = activeItem.clientHeight;

            // 计算目标滚动位置，使活跃项在容器中央
            const targetScrollTop = itemOffsetTop - (containerHeight / 2) + (itemHeight / 2);

            // 确保不会滚动超出边界
            const maxScrollTop = tocContainerEl.scrollHeight - containerHeight;
            const finalScrollTop = Math.max(0, Math.min(targetScrollTop, maxScrollTop));

            // 使用自定义的平滑滚动函数
            smoothScrollTo(tocContainerEl, finalScrollTop, 400);
        }
    }
}

// 设置水印位置
const setupWatermarkPosition = () => {
    if (!watermarkContainer.value || !articleContent.value) return;
    
    const articleHeight = articleContent.value.offsetHeight;
    const viewportHeight = window.innerHeight;
    
    // 计算水印应该出现的位置（文章中间偏上）
    const watermarkPosition = Math.min(articleHeight * 0.4, viewportHeight * 0.6);
    
    watermarkContainer.value.style.top = `${watermarkPosition}px`;
};

let cleanupScrollListener = null;

onMounted(() => {
    axios.get(`/api/posts/${post_id}`).then(res => {
        post.value = res.data;

        post.value.content = md.parse(post.value.content);

        // 生成TOC
        tocHtml.value = generateToc(post.value.content);

        // 检查点赞状态
        checkLikeStatus();

        setTimeout(() => {
            loading.value = false;
        }, 300);
        // 设置TOC点击事件
        nextTick(() => {
            setupTocClickHandlers();
            // 获取所有标题元素
            headingElements.value = Array.from(document.querySelectorAll('.markdown-body h2, .markdown-body h3'));
            // 设置滚动跟踪
            cleanupScrollListener = setupScrollTracking();
            // 设置水印位置
            setupWatermarkPosition();
        });
    }).catch(err => {
        console.log(err);
    });

    document.title = post.value.title ? post.value.title :"红客路上" 

})

// 监听窗口大小变化，重新定位水印
onMounted(() => {
    window.addEventListener('resize', setupWatermarkPosition);
});

onUnmounted(() => {
    if (cleanupScrollListener) {
        cleanupScrollListener();
    }
    if (scrollAnimationFrame.value) {
        cancelAnimationFrame(scrollAnimationFrame.value);
    }
    window.removeEventListener('resize', setupWatermarkPosition);
});
</script>

<style>
@import url(@/assets/css/hljs.css);

/* 点赞相关样式 */
.c-hand.liked {
    color: #f44336;
}

.text-red {
    color: #f44336 !important;
}

.loading-like {
    display: flex;
    align-items: center;
}

.loading-like .czs-loading {
    animation: spin 1s linear infinite;
}

/* 用户头像区域的点赞按钮 */
.like-btn {
    transition: all 0.3s ease;
}

.like-btn:hover:not(.loading) {
    transform: scale(1.1);
}

.like-btn.liked {
    color: #f44336 !important;
}

.like-btn.loading {
    opacity: 0.6;
    cursor: not-allowed;
}

.like-btn.loading .czs-heart-l {
    animation: pulse 1s infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

/* 点赞消息动画 */
@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes slideOut {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}

/* 水印样式 */
.watermark-container {
    position: absolute;
    left: 0;
    right: 0;
    pointer-events: none;
    z-index: 1;
    display: flex;
    justify-content: center;
    align-items: center;
}

.watermark-logo {
    opacity: 0.03;
    transition: all 0.5s ease;
    transform: scale(1);
}

.watermark-logo i {
    font-size: 300px;
    color: #000;
}

/* 暗色主题支持 */
@media (prefers-color-scheme: dark) {
    .watermark-logo i {
        color: #fff;
    }
}

/* 文章内容区域相对定位，为水印提供定位上下文 */
.article {
    position: relative;
}

/* 确保markdown-body在水印之上 */
.markdown-body {
    position: relative;
    z-index: 2;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .watermark-logo i {
        font-size: 200px;
    }
}

@media (max-width: 480px) {
    .watermark-logo i {
        font-size: 150px;
    }
}

/* 文章代码块样式 */
pre {
    background: #fff;
    border: 1px solid #eee;
    border-radius: 5px;
    overflow-x: auto;
    margin: 25px 0;
    transition: all 0.5s;
}

/* TOC 样式 */
.toc-header {
    position: relative;
    z-index: 1;
    font-size: 16px;
    color: #66758c;
}

.toc-header i {
    position: relative;
    top: 0;
    margin-right: 8px;
    vertical-align: middle;
    font-size: 18px;
}

.toc-container {
    position: relative;
    max-height: 400px;
    overflow-y: auto;
    margin: 0;
}

.toc-item {
    text-decoration: none;
    font-size: 14px;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
    word-break: break-word;

}

.toc-item {
    padding: 6px 10px;
    margin-bottom: 3px;

    border-radius: 6px;
    position: relative;
    transition: all 0.3s ease;
    cursor: pointer;
    color: #66758c;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    line-clamp: 1;
    box-orient: vertical;
}

.toc-item:hover {
    background-color: rgba(188, 195, 206, 0.1);
}

/* 新增：active状态的TOC项样式 */
.toc-item.active {
    background-color: rgba(188, 195, 206, 0.1);
    color: #409eff;
}

/* 滚动条样式 */
.toc-container::-webkit-scrollbar {
    width: 4px;
}

.toc-container::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 2px;
}

.toc-container::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 2px;
}

.toc-container::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
}

.article-title {
    font-size: 24px;
    color: #222;
    margin-bottom: 15px;
    word-break: break-word;
}

@import url(@/assets/css/post.css);
</style>