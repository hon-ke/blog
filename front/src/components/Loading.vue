<template>
    <div v-if="internalVisible" class="loading-skeleton">
        <!-- 文章列表骨架 -->
        <div v-if="type === 'article-list'" :class="['skeleton-list', `skeleton-${animationType}`]">
            <div class="skeleton-item" v-for="n in count" :key="n">
                <div class="skeleton-thumbnail"></div>
                <div class="skeleton-content">
                    <div class="skeleton-title"></div>
                    <div class="skeleton-title"></div>
                    <div class="skeleton-abstract">
                        <p></p>
                    </div>
                    <div class="skeleton-tags">
                        <span class="skeleton-tag" v-for="n in 3" :key="n"></span>
                    </div>
                </div>
            </div>
        </div>

        <div v-else-if="type === 'heatmap'" :class="['skeleton-list', `skeleton-${animationType}`]">
            <div class="skeleton-heatmap skeleton-thumbnail"></div>
        </div>

        <!-- 文章详情骨架 -->
        <div v-else-if="type === 'article-detail'" :class="['skeleton-detail', `skeleton-${animationType}`]">
            <div class="skeleton-header">
                <div class="skeleton-title-lg"></div>
                <div class="skeleton-meta">
                    <span class="skeleton-meta-item"></span>
                    <span class="skeleton-meta-item"></span>
                    <span class="skeleton-meta-item"></span>
                </div>
            </div>
            <div class="skeleton-cover"></div>
            <div class="skeleton-content-detail">
                <div class="skeleton-paragraph" :key="n">
                    <p></p>
                    <p></p>
                    <p></p>
                </div>
            </div>

            <div class="skeleton-cover"></div>

            <div class="skeleton-tags">
                <span class="skeleton-tag" v-for="n in 3" :key="n"></span>
            </div>


        </div>

        <!-- 文章详情骨架 -->
        <div v-else-if="type === 'page'" :class="['skeleton-detail', `skeleton-${animationType}`]">
            <div class="skeleton-header">
                <div class="skeleton-title-lg"></div>
                <div class="skeleton-meta">
                    <span class="skeleton-meta-item"></span>
                    <span class="skeleton-meta-item"></span>
                    <span class="skeleton-meta-item"></span>
                </div>
            </div>
            <div class="skeleton-cover"></div>
            <div class="skeleton-content-detail">
                <div class="skeleton-paragraph">
                    <div class="skeleton-title-lg"></div>
                </div>

                <div class="skeleton-paragraph">
                    <p></p>
                    <p></p>
                    <p></p>
                </div>
            </div>
        </div>

        <!-- 卡片列表骨架 -->
        <div v-else-if="type === 'card-list'" :class="['skeleton-cards', `skeleton-${animationType}`]">
            <div class="skeleton-card" v-for="n in count" :key="n">
                <div class="skeleton-card-cover"></div>
                <div class="skeleton-card-content">
                    <div class="skeleton-card-title"></div>
                    <div class="skeleton-card-desc">
                        <p></p>
                        <p></p>
                    </div>
                    <div class="skeleton-card-footer">
                        <span class="skeleton-card-meta"></span>
                        <span class="skeleton-card-meta"></span>
                    </div>
                </div>
            </div>
        </div>






        <!-- 个人资料骨架 -->
        <div v-else-if="type === 'profile'" :class="['skeleton-profile', `skeleton-${animationType}`]">
            <div class="skeleton-profile-header">
                <div class="skeleton-avatar"></div>
                <div class="skeleton-profile-info">
                    <div class="skeleton-profile-name"></div>
                    <div class="skeleton-profile-bio">
                        <p></p>
                        <p></p>
                    </div>
                </div>
            </div>
            <div class="skeleton-stats">
                <div class="skeleton-stat" v-for="n in 3" :key="n">
                    <div class="skeleton-stat-number"></div>
                    <div class="skeleton-stat-label"></div>
                </div>
            </div>
            <div class="skeleton-tabs">
                <div class="skeleton-tab" v-for="n in 4" :key="n"></div>
            </div>
        </div>

        <!-- 评论列表骨架 -->
        <div v-else-if="type === 'comment-list'" :class="['skeleton-comments', `skeleton-${animationType}`]">
            <div class="skeleton-comment" v-for="n in count" :key="n">
                <div class="skeleton-comment-avatar"></div>
                <div class="skeleton-comment-content">
                    <div class="skeleton-comment-header">
                        <div class="skeleton-comment-author"></div>
                        <div class="skeleton-comment-time"></div>
                    </div>
                    <div class="skeleton-comment-text">
                        <p></p>
                    </div>
                    <div class="skeleton-comment-actions">
                        <span class="skeleton-comment-action"></span>
                        <span class="skeleton-comment-action"></span>
                    </div>
                </div>
            </div>
        </div>


    </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
    // 是否显示
    visible: {
        type: Boolean,
        default: true
    },
    // 显示数量
    count: {
        type: Number,
        default: 2
    },
    // 最少显示时间（毫秒）
    minDisplayTime: {
        type: Number,
        default: 2000
    },
    // 动画类型
    animationType: {
        type: String,
        default: 'default',
        validator: (value) => ['default', 'pulse', 'wave', 'bounce', 'breath'].includes(value)
    },
    // 骨架屏类型
    type: {
        type: String,
        default: 'article-list',
        validator: (value) => ['article-list', 'article-detail', 'card-list', 'profile', 'comment-list'].includes(value)
    }
})

const internalVisible = ref(props.visible)
const showStartTime = ref(null)
let minDisplayTimer = null

const closeWithMinTime = () => {
    const elapsed = Date.now() - showStartTime.value
    const remainingTime = props.minDisplayTime - elapsed

    if (remainingTime > 0) {
        minDisplayTimer = setTimeout(() => {
            internalVisible.value = false
        }, remainingTime)
    } else {
        internalVisible.value = false
    }
}

watch(() => props.visible, (newVal) => {
    if (newVal) {
        internalVisible.value = true
        showStartTime.value = Date.now()
    } else {
        closeWithMinTime()
    }
})

onMounted(() => {
    if (props.visible) {
        showStartTime.value = Date.now()
    }
})

onUnmounted(() => {
    clearTimeout(minDisplayTimer)
})

defineExpose({
    show: () => {
        internalVisible.value = true
        showStartTime.value = Date.now()
    },
    hide: closeWithMinTime,
    isVisible: internalVisible
})
</script>

<style scoped>
.loading-skeleton {
    --skeleton-bg: #f2f6fc;
    --skeleton-radius: 4px;
    --skeleton-border: #e4e7ed;
}

/* ===== 通用样式 ===== */
.skeleton-item,
.skeleton-card,
.skeleton-comment {
    width: 100%;
    padding: 15px 0;
    border-bottom: 1px solid var(--skeleton-border);
    display: flex;
    position: relative;
}

.skeleton-item:last-child,
.skeleton-card:last-child,
.skeleton-comment:last-child {
    border-bottom: none;
}

/* ===== 文章列表骨架 ===== */
.skeleton-thumbnail {
    flex-shrink: 0;
    position: relative;
    width: 210px;
    height: 140px;
    margin-right: 15px;
    background: var(--skeleton-bg);
    border-radius: var(--skeleton-radius);
}

.skeleton-content {
    flex: 1;
    min-width: 0;
}

.skeleton-title {
    height: 24px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
    margin-bottom: 15px;
}

.skeleton-heatmap {
    height: 60px;
    width: 100%;
    padding: 0;
    margin: 0;
}

.skeleton-abstract p {
    height: 18px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
    margin-bottom: 15px;
}

/* ===== 文章详情骨架 ===== */
.skeleton-header {
    margin-bottom: 20px;
}

.skeleton-title-lg {
    height: 32px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
    margin-bottom: 15px;
}

.skeleton-meta {
    display: flex;
    gap: 20px;
}

.skeleton-meta-item {
    height: 16px;
    width: 80px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
}

.skeleton-cover {
    width: 100%;
    height: 300px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
    margin-bottom: 30px;
}

.skeleton-content-detail {
    margin-bottom: 20px;
}

.skeleton-paragraph {
    margin-bottom: 20px;
}

.skeleton-paragraph p {
    height: 18px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
    margin-bottom: 8px;
}

.skeleton-paragraph p:nth-child(1) {
    width: 95%;
}

.skeleton-paragraph p:nth-child(2) {
    width: 88%;
}

.skeleton-paragraph p:nth-child(3) {
    width: 92%;
}

.skeleton-tags {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.skeleton-tag {
    height: 24px;
    width: 60px;
    border-radius: 12px;
    background: var(--skeleton-bg);
}

/* ===== 卡片列表骨架 ===== */
.skeleton-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
    padding: 20px;
}

.skeleton-card {
    border: 1px solid var(--skeleton-border);
    border-radius: 8px;
    padding: 0;
    flex-direction: column;
    border-bottom: none;
}

.skeleton-card-cover {
    width: 100%;
    height: 160px;
    border-radius: 8px 8px 0 0;
    background: var(--skeleton-bg);
}

.skeleton-card-content {
    padding: 15px;
    flex: 1;
}

.skeleton-card-title {
    height: 20px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
    margin-bottom: 10px;
}

.skeleton-card-desc p {
    height: 14px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
    margin-bottom: 6px;
}

.skeleton-card-desc p:nth-child(1) {
    width: 90%;
}

.skeleton-card-desc p:nth-child(2) {
    width: 70%;
}

.skeleton-card-footer {
    display: flex;
    justify-content: space-between;
    margin-top: 15px;
}

.skeleton-card-meta {
    height: 14px;
    width: 50px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
}

/* ===== 个人资料骨架 ===== */
.skeleton-profile {
    padding: 20px;
}

.skeleton-profile-header {
    display: flex;
    align-items: flex-start;
    margin-bottom: 30px;
}

.skeleton-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: var(--skeleton-bg);
    margin-right: 20px;
    flex-shrink: 0;
}

.skeleton-profile-info {
    flex: 1;
}

.skeleton-profile-name {
    height: 24px;
    width: 120px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
    margin-bottom: 10px;
}

.skeleton-profile-bio p {
    height: 16px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
    margin-bottom: 6px;
}

.skeleton-profile-bio p:nth-child(1) {
    width: 80%;
}

.skeleton-profile-bio p:nth-child(2) {
    width: 60%;
}

.skeleton-stats {
    display: flex;
    justify-content: space-around;
    margin-bottom: 30px;
    padding: 20px 0;
    border-top: 1px solid var(--skeleton-border);
    border-bottom: 1px solid var(--skeleton-border);
}

.skeleton-stat {
    text-align: center;
}

.skeleton-stat-number {
    height: 28px;
    width: 40px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
    margin-bottom: 8px;
}

.skeleton-stat-label {
    height: 14px;
    width: 50px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
}

.skeleton-tabs {
    display: flex;
    gap: 20px;
}

.skeleton-tab {
    height: 30px;
    width: 60px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
}

/* ===== 评论列表骨架 ===== */
.skeleton-comments {
    padding: 20px;
}

.skeleton-comment {
    padding: 15px 0;
    align-items: flex-start;
}

.skeleton-comment-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--skeleton-bg);
    margin-right: 12px;
    flex-shrink: 0;
}

.skeleton-comment-content {
    flex: 1;
}

.skeleton-comment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.skeleton-comment-author {
    height: 16px;
    width: 80px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
}

.skeleton-comment-time {
    height: 14px;
    width: 60px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
}

.skeleton-comment-text p {
    height: 16px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
    margin-bottom: 6px;
}

.skeleton-comment-text p:nth-child(1) {
    width: 95%;
}

.skeleton-comment-text p:nth-child(2) {
    width: 85%;
}

.skeleton-comment-text p:nth-child(3) {
    width: 70%;
}

.skeleton-comment-actions {
    display: flex;
    gap: 15px;
    margin-top: 10px;
}

.skeleton-comment-action {
    height: 14px;
    width: 40px;
    border-radius: var(--skeleton-radius);
    background: var(--skeleton-bg);
}

/* ===== 动画系统 ===== */
/* 默认动画 */
.skeleton-default .skeleton-thumbnail,
.skeleton-default .skeleton-cover,
.skeleton-default .skeleton-card-cover,
.skeleton-default .skeleton-avatar,
.skeleton-default .skeleton-comment-avatar {
    animation: skeleton-thumbnail-animation .5s infinite alternate;
}

.skeleton-default .skeleton-title,
.skeleton-default .skeleton-title-lg,
.skeleton-default .skeleton-card-title,
.skeleton-default .skeleton-profile-name {
    animation: skeleton-title-animation .75s infinite alternate;
}

.skeleton-default .skeleton-abstract p,
.skeleton-default .skeleton-paragraph p,
.skeleton-default .skeleton-card-desc p,
.skeleton-default .skeleton-profile-bio p,
.skeleton-default .skeleton-comment-text p {
    animation: skeleton-abstract-animation .8s infinite alternate;
}

.skeleton-default .skeleton-abstract p:nth-child(2),
.skeleton-default .skeleton-paragraph p:nth-child(2),
.skeleton-default .skeleton-card-desc p:nth-child(2),
.skeleton-default .skeleton-profile-bio p:nth-child(2),
.skeleton-default .skeleton-comment-text p:nth-child(2) {
    animation-delay: 0.2s;
}

/* 脉冲动画 */
.skeleton-pulse .skeleton-thumbnail,
.skeleton-pulse .skeleton-cover,
.skeleton-pulse .skeleton-card-cover,
.skeleton-pulse .skeleton-avatar,
.skeleton-pulse .skeleton-comment-avatar {
    animation: skeleton-pulse-thumbnail 1.2s ease-in-out infinite;
}

.skeleton-pulse .skeleton-title,
.skeleton-pulse .skeleton-title-lg,
.skeleton-pulse .skeleton-card-title,
.skeleton-pulse .skeleton-profile-name {
    animation: skeleton-pulse-title 1.5s ease-in-out infinite;
}

.skeleton-pulse .skeleton-abstract p,
.skeleton-pulse .skeleton-paragraph p,
.skeleton-pulse .skeleton-card-desc p,
.skeleton-pulse .skeleton-profile-bio p,
.skeleton-pulse .skeleton-comment-text p {
    animation: skeleton-pulse-abstract 1.8s ease-in-out infinite;
}

/* 波浪动画 */
.skeleton-wave .skeleton-thumbnail,
.skeleton-wave .skeleton-cover,
.skeleton-wave .skeleton-card-cover,
.skeleton-wave .skeleton-avatar,
.skeleton-wave .skeleton-comment-avatar {
    animation: skeleton-wave-thumbnail 1.8s ease-in-out infinite;
}

.skeleton-wave .skeleton-title,
.skeleton-wave .skeleton-title-lg,
.skeleton-wave .skeleton-card-title,
.skeleton-wave .skeleton-profile-name {
    animation: skeleton-wave-title 2s ease-in-out infinite;
}

.skeleton-wave .skeleton-abstract p,
.skeleton-wave .skeleton-paragraph p,
.skeleton-wave .skeleton-card-desc p,
.skeleton-wave .skeleton-profile-bio p,
.skeleton-wave .skeleton-comment-text p {
    animation: skeleton-wave-abstract 2.2s ease-in-out infinite;
}

/* 弹跳动画 */
.skeleton-bounce .skeleton-thumbnail,
.skeleton-bounce .skeleton-cover,
.skeleton-bounce .skeleton-card-cover,
.skeleton-bounce .skeleton-avatar,
.skeleton-bounce .skeleton-comment-avatar {
    animation: skeleton-bounce-thumbnail 1.2s ease-in-out infinite;
}

.skeleton-bounce .skeleton-title,
.skeleton-bounce .skeleton-title-lg,
.skeleton-bounce .skeleton-card-title,
.skeleton-bounce .skeleton-profile-name {
    animation: skeleton-bounce-title 1.5s ease-in-out infinite;
}

.skeleton-bounce .skeleton-abstract p,
.skeleton-bounce .skeleton-paragraph p,
.skeleton-bounce .skeleton-card-desc p,
.skeleton-bounce .skeleton-profile-bio p,
.skeleton-bounce .skeleton-comment-text p {
    animation: skeleton-bounce-abstract 1.8s ease-in-out infinite;
}

/* 呼吸动画 */
.skeleton-breath .skeleton-thumbnail,
.skeleton-breath .skeleton-cover,
.skeleton-breath .skeleton-card-cover,
.skeleton-breath .skeleton-avatar,
.skeleton-breath .skeleton-comment-avatar {
    animation: skeleton-breath-thumbnail 2s ease-in-out infinite;
}

.skeleton-breath .skeleton-title,
.skeleton-breath .skeleton-title-lg,
.skeleton-breath .skeleton-card-title,
.skeleton-breath .skeleton-profile-name {
    animation: skeleton-breath-title 2.2s ease-in-out infinite;
}

.skeleton-breath .skeleton-abstract p,
.skeleton-breath .skeleton-paragraph p,
.skeleton-breath .skeleton-card-desc p,
.skeleton-breath .skeleton-profile-bio p,
.skeleton-breath .skeleton-comment-text p {
    animation: skeleton-breath-abstract 2.4s ease-in-out infinite;
}

/* 关键帧动画（保持不变） */
@keyframes skeleton-thumbnail-animation {
    0% {
        transform: scale(.85);
    }

    to {
        transform: scale(1);
    }
}

@keyframes skeleton-title-animation {
    0% {
        width: 80%;
    }

    to {
        width: 95%;
    }
}

@keyframes skeleton-abstract-animation {
    0% {
        width: 60%;
    }

    to {
        width: 80%;
    }
}

@keyframes skeleton-pulse-thumbnail {

    0%,
    100% {
        transform: scale(0.9);
        opacity: 0.7;
    }

    50% {
        transform: scale(1.05);
        opacity: 1;
    }
}

@keyframes skeleton-pulse-title {

    0%,
    100% {
        width: 75%;
    }

    50% {
        width: 98%;
    }
}

@keyframes skeleton-pulse-abstract {

    0%,
    100% {
        width: 55%;
    }

    50% {
        width: 82%;
    }
}

@keyframes skeleton-wave-thumbnail {

    0%,
    100% {
        transform: scale(1) translateY(0);
    }

    33% {
        transform: scale(1.03) translateY(-2px);
    }

    66% {
        transform: scale(0.98) translateY(2px);
    }
}

@keyframes skeleton-wave-title {

    0%,
    100% {
        width: 82%;
    }

    33% {
        width: 95%;
    }

    66% {
        width: 88%;
    }
}

@keyframes skeleton-wave-abstract {

    0%,
    100% {
        width: 62%;
    }

    33% {
        width: 78%;
    }

    66% {
        width: 70%;
    }
}

@keyframes skeleton-bounce-thumbnail {

    0%,
    100% {
        transform: scale(1);
    }

    25% {
        transform: scale(1.08);
    }

    50% {
        transform: scale(0.95);
    }

    75% {
        transform: scale(1.03);
    }
}

@keyframes skeleton-bounce-title {

    0%,
    100% {
        width: 80%;
    }

    25% {
        width: 98%;
    }

    50% {
        width: 85%;
    }

    75% {
        width: 92%;
    }
}

@keyframes skeleton-bounce-abstract {

    0%,
    100% {
        width: 60%;
    }

    25% {
        width: 78%;
    }

    50% {
        width: 65%;
    }

    75% {
        width: 72%;
    }
}

@keyframes skeleton-breath-thumbnail {

    0%,
    100% {
        transform: scale(0.95);
        opacity: 0.8;
    }

    50% {
        transform: scale(1.02);
        opacity: 1;
    }
}

@keyframes skeleton-breath-title {

    0%,
    100% {
        width: 78%;
        opacity: 0.9;
    }

    50% {
        width: 92%;
        opacity: 1;
    }
}

@keyframes skeleton-breath-abstract {

    0%,
    100% {
        width: 58%;
        opacity: 0.8;
    }

    50% {
        width: 75%;
        opacity: 1;
    }
}

/* 响应式设计 */
@media (max-width: 768px) {

    .skeleton-item,
    .skeleton-comment {
        flex-direction: column;
    }

    .skeleton-thumbnail {
        width: 100%;
        height: 180px;
        margin-right: 0;
        margin-bottom: 12px;
    }

    .skeleton-cards {
        grid-template-columns: 1fr;
        padding: 10px;
    }

    .skeleton-profile-header {
        flex-direction: column;
        align-items: center;
        text-align: center;
    }

    .skeleton-avatar {
        margin-right: 0;
        margin-bottom: 15px;
    }

    .skeleton-stats {
        flex-direction: column;
        gap: 15px;
    }
}
</style>