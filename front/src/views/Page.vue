<template>
    <Layout>
        <template #main>
            <div class="page-container">
                <Loading v-show="loading" type="page" :visible="loading" :count="3" />
                <div v-show="!loading && has_page" class="markdown-body note-body" v-html="post.content"></div>
                <div v-show="!loading && notFound" class="empty-state">
                    <div class="empty-icon-container">
                        <i class="empty-icon czs-apple"></i>
                    </div>
                    <h3 class="empty-title">暂无内容 , 敬请期待</h3>
                </div>
            </div>
        </template>
    </Layout>
</template>

<script setup>
import Layout from '../components/Layout.vue';
import Loading from '../components/Loading.vue';
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';

import axios from 'axios';
import { md } from '@/assets/js/marked-wrapper'
import { Fancybox } from "@fancyapps/ui";
import "@fancyapps/ui/dist/fancybox/fancybox.css";

const route = useRoute();
const loading = ref(true)
const notFound = ref(false)
const has_page = ref(false)
const post = ref({});

Fancybox.bind("[data-fancybox]", {
    // Your custom options
});

// 提取数据加载逻辑到单独函数
const loadPageData = async (path) => {
    try {
        loading.value = true;
        notFound.value = false;
        has_page.value = false;
        
        const response = await axios.get(`/api/pages/${path}`);
        post.value = response.data;
        
        if (post.value.content) {
            post.value.content = md.parse(post.value.content);
            has_page.value = true;
        } else {
            notFound.value = true;
        }
    } catch (err) {
        console.log(err);
        notFound.value = true;
    } finally {
        // 确保加载状态正确更新
        setTimeout(() => {
            loading.value = false;
        }, 300);
    }
};

// 监听路由变化，当路径改变时重新加载数据
watch(
    () => route.path,
    (newPath, oldPath) => {
        if (newPath !== oldPath) {
            const path = newPath.replace("/", "");
            loadPageData(path);
        }
    },
    { immediate: true } // 立即执行一次，替代 onMounted
);

</script>

<style>
.page-container {
    position: relative;
    min-height: 60vh;
    display: flex;
    flex-direction: column;
}

.empty-state {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 4rem 2rem;
    color: #8c8c8c;
    width: 100%;
    max-width: 500px;
}

.empty-icon-container {
    margin-bottom: 2rem;
    opacity: 0.6;
}

.empty-icon {
    font-size: 6rem;
    color: #d9d9d9;
    transition: all 0.3s ease;
}

.empty-title {
    font-size: 16px;
    font-weight: 500;
    color: #66758c;
    margin: 0 0 1rem 0;
    line-height: 1.4;
}

/* 深色主题支持 */
@media (prefers-color-scheme: dark) {
    .empty-state {
        color: #8c8c8c;
    }

    .empty-icon {
        color: #434343;
    }

    .empty-title {
        color: #bfbfbf;
    }
}

/* 响应式设计 */
@media (max-width: 768px) {
    .empty-state {
        padding: 3rem 1rem;
        max-width: 90%;
    }

    .empty-icon {
        font-size: 4rem;
    }
}

/* 动画效果 */
@keyframes float {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-10px);
    }
}

.empty-icon {
    animation: float 3s ease-in-out infinite;
}

/* 可选：不同的图标样式变体 */
.empty-icon.primary {
    color: #1890ff;
}

.empty-icon.success {
    color: #52c41a;
}

.empty-icon.warning {
    color: #faad14;
}

.empty-icon.error {
    color: #ff4d4f;
}
</style>