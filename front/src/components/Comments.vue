<template>

    <div id="comments">
        <!-- 评论列表 -->
        <div class="comments-list-header">
            <h3>评论列表 ({{ comments.length }})</h3>
        </div>
        <div class="comments-list" v-if="comments.length > 0">

            <div class="recent-list" id="recentComments">
                <div v-for="comment in comments" :key="comment.id" class="recent-item">
                    <!-- 超级用户头像 -->
                    <div v-if="comment.is_superuser" class="superuser-avatar">
                        <div class="avatar-container link">
                            <img src="@/assets/img/clay.jpg" class="avatar-img" alt="clay">
                            <button data-tooltip="blogger" class="tooltip link vip-badge">
                                <i class="czs-vimeo"></i>
                            </button>
                        </div>
                    </div>
                    <!-- 匿名用户头像 -->
                    <div v-else-if="comment.is_anonymous" class="recent-avatar anonymous-avatar">
                        <svg t="1760298022252" class="icon anonymous-icon" viewBox="0 0 1024 1024" version="1.1"
                            xmlns="http://www.w3.org/2000/svg" p-id="14759">
                            <path
                                d="M913.954133 699.733333l-47.786666-143.36a135.031467 135.031467 0 0 0-34.133334-51.2l-88.746666-68.266666a430.2848 430.2848 0 0 0 13.653333-95.573334c0-88.746667-150.186667-238.933333-238.933333-238.933333s-238.933333 150.186667-238.933334 238.933333a296.1408 296.1408 0 0 0 17.066667 95.573334l-88.746667 68.266666a86.1184 86.1184 0 0 0-34.133333 51.2l-47.786667 143.36a100.829867 100.829867 0 0 0 23.893334 105.813334l37.546666 37.546666a30.993067 30.993067 0 0 0 23.893334 10.24h34.133333v-238.933333a100.5568 100.5568 0 0 1 102.4-102.4h61.44a247.944533 247.944533 0 0 1-54.613333-112.64 71.168 71.168 0 0 1 40.96-78.506667l98.986666-37.546666a66.56 66.56 0 0 1 51.2 0l98.986667 37.546666a69.154133 69.154133 0 0 1 40.96 78.506667 295.867733 295.867733 0 0 1-58.026667 112.64h61.44a100.5568 100.5568 0 0 1 102.4 102.4v238.933333h34.133334a30.993067 30.993067 0 0 0 23.893333-10.24l37.546667-37.546666a109.602133 109.602133 0 0 0 27.306666-105.813334z"
                                p-id="14760"></path>
                            <path
                                d="M688.674133 580.266667h-341.333333a32.256 32.256 0 0 0-34.133333 34.133333v273.066667a32.256 32.256 0 0 0 34.133333 34.133333h341.333333a32.256 32.256 0 0 0 34.133334-34.133333v-273.066667a32.256 32.256 0 0 0-34.133334-34.133333z m-170.666666 225.28a51.2 51.2 0 1 1 51.2-51.2 52.497067 52.497067 0 0 1-51.2 51.2z"
                                p-id="14761"></path>
                        </svg>
                    </div>
                    <!-- 普通用户头像 -->
                    <div v-else class="recent-avatar" :style="{ background: getAvatarColor(comment.author_name) }">
                        {{ getAvatarText(comment.author_name) }}
                    </div>
                    <div class="recent-content">
                        <div class="recent-header">
                            <div class="recent-author-info">
                                <span class="recent-author">
                                    <!-- 超级用户显示橙色名字 -->
                                    <template v-if="comment.is_superuser">
                                        <span class="superuser-name">
                                            {{ comment.author_name }}
                                        </span>
                                        <span class="superuser-badge">
                                            <svg class="crown-badge" viewBox="0 0 16 16" fill="currentColor">
                                                <path d="M8 1l2 4 4 .5-3 3 .5 4.5-3.5-2-3.5 2 .5-4.5-3-3 4-.5z" />
                                            </svg>
                                        </span>
                                    </template>
                                    <!-- 匿名用户 -->
                                    <template v-else-if="comment.is_anonymous">
                                        <span class="anonymous-user">匿名用户</span>
                                    </template>
                                    <!-- 普通用户 -->
                                    <template v-else>
                                        <a v-if="hasWebsite(comment)" :href="ensureHttp(comment.author_website)"
                                            target="_blank" class="author-link">
                                            {{ comment.author_name }}
                                        </a>
                                        <span v-else>{{ comment.author_name }}</span>
                                    </template>
                                </span>
                                <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
                            </div>
                        </div>
                        <div class="comment-text">{{ comment.content }}</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 评论触发按钮 -->
        <div class="comment-trigger" v-if="!showCommentForm">
            <button class="trigger-btn link" @click="showCommentForm = true">
                <svg t="1760235383700" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"
                    p-id="43702">
                    <path d="M521.309091 480.581818L50.036364 951.854545" fill="currentColor" p-id="43703"></path>
                    <path
                        d="M50.036364 963.490909c-3.490909 0-5.818182-1.163636-8.145455-3.490909-4.654545-4.654545-4.654545-11.636364 0-16.290909l471.272727-471.272727c4.654545-4.654545 11.636364-4.654545 16.290909 0s4.654545 11.636364 0 16.290909L58.181818 960c-2.327273 2.327273-4.654545 3.490909-8.145454 3.490909z"
                        fill="currentColor" p-id="43704"></path>
                    <path
                        d="M512 678.4c-3.490909 0-8.145455-2.327273-10.472727-5.818182-3.490909-5.818182-1.163636-12.8 3.490909-16.290909 361.890909-223.418182 434.036364-432.872727 448-512 4.654545-23.272727-4.654545-46.545455-22.109091-59.345454-60.509091-44.218182-176.872727 33.745455-178.036364 34.90909-484.072727 332.8-434.036364 542.254545-432.872727 544.581819 1.163636 5.818182-2.327273 12.8-8.145455 13.963636-5.818182 1.163636-12.8-2.327273-13.963636-8.145455-2.327273-9.309091-58.181818-225.745455 443.345455-569.018181 5.818182-3.490909 131.490909-88.436364 204.8-34.909091 24.436364 18.618182 37.236364 50.036364 31.418181 82.618182-15.127273 82.618182-88.436364 299.054545-458.472727 528.290909-2.327273 1.163636-4.654545 1.163636-6.981818 1.163636zM805.236364 966.981818c-80.290909 0-140.8-32.581818-148.945455-37.236363-216.436364-94.254545-354.909091 10.472727-356.072727 11.636363-4.654545 3.490909-12.8 3.490909-16.290909-2.327273-3.490909-4.654545-3.490909-12.8 2.327272-16.290909 5.818182-4.654545 150.109091-114.036364 380.509091-13.963636 0 0 1.163636 0 1.163637 1.163636 1.163636 1.163636 141.963636 82.618182 281.6-9.309091 5.818182-3.490909 12.8-2.327273 16.290909 3.49091 3.490909 5.818182 2.327273 12.8-3.490909 16.290909-54.690909 34.909091-109.381818 46.545455-157.090909 46.545454z"
                        fill="currentColor" p-id="43705"></path>
                </svg>
                发表评论
            </button>
        </div>

        <!-- 评论表单 -->
        <form @submit.prevent="submitComment" v-if="showCommentForm" class="comment-form">
            <div class="form-header">
                <h3>发表评论</h3>
                <button type="button" class="close-btn" @click="closeCommentForm">×</button>
            </div>

            <!-- 普通用户和匿名用户的输入框 -->
            <ul class="comments-head" v-if="userMode !== 'superuser'">
                <li><input type="text" placeholder="昵称" v-model="form.name" :disabled="userMode === 'anonymous'"></li>
                <li><input type="email" placeholder="邮箱" v-model="form.email" :disabled="userMode === 'anonymous'"></li>
                <li><input type="url" placeholder="网站" v-model="form.website" :disabled="userMode === 'anonymous'"></li>
            </ul>

            <!-- 超级用户的 API Key 输入框 -->
            <ul class="comments-head superuser-input" v-else>
                <li><input type="password" placeholder="请输入 API Key 以管理员身份评论" v-model="form.api_key"></li>
            </ul>

            <div class="comments-body">
                <!-- 模式切换头像 -->
                <div class="avatar-icon link" @click="cycleUserMode" :class="getAvatarModeClass()">
                    <!-- 普通用户图标 -->
                    <i class="czs-fingerprint-l" v-if="userMode === 'normal'"></i>
                    <!-- 匿名用户图标 -->
                    <div v-else-if="userMode === 'anonymous'"><svg data-v-5847e424="" t="1760298022252"
                            class="icon anonymous-icon" viewBox="0 0 1024 1024" version="1.1"
                            xmlns="http://www.w3.org/2000/svg" p-id="14759">
                            <path data-v-5847e424=""
                                d="M913.954133 699.733333l-47.786666-143.36a135.031467 135.031467 0 0 0-34.133334-51.2l-88.746666-68.266666a430.2848 430.2848 0 0 0 13.653333-95.573334c0-88.746667-150.186667-238.933333-238.933333-238.933333s-238.933333 150.186667-238.933334 238.933333a296.1408 296.1408 0 0 0 17.066667 95.573334l-88.746667 68.266666a86.1184 86.1184 0 0 0-34.133333 51.2l-47.786667 143.36a100.829867 100.829867 0 0 0 23.893334 105.813334l37.546666 37.546666a30.993067 30.993067 0 0 0 23.893334 10.24h34.133333v-238.933333a100.5568 100.5568 0 0 1 102.4-102.4h61.44a247.944533 247.944533 0 0 1-54.613333-112.64 71.168 71.168 0 0 1 40.96-78.506667l98.986666-37.546666a66.56 66.56 0 0 1 51.2 0l98.986667 37.546666a69.154133 69.154133 0 0 1 40.96 78.506667 295.867733 295.867733 0 0 1-58.026667 112.64h61.44a100.5568 100.5568 0 0 1 102.4 102.4v238.933333h34.133334a30.993067 30.993067 0 0 0 23.893333-10.24l37.546667-37.546666a109.602133 109.602133 0 0 0 27.306666-105.813334z"
                                p-id="14760"></path>
                            <path data-v-5847e424=""
                                d="M688.674133 580.266667h-341.333333a32.256 32.256 0 0 0-34.133333 34.133333v273.066667a32.256 32.256 0 0 0 34.133333 34.133333h341.333333a32.256 32.256 0 0 0 34.133334-34.133333v-273.066667a32.256 32.256 0 0 0-34.133334-34.133333z m-170.666666 225.28a51.2 51.2 0 1 1 51.2-51.2 52.497067 52.497067 0 0 1-51.2 51.2z"
                                p-id="14761"></path>
                        </svg></div>
                    <!-- 超级用户图标 -->
                    <i class="czs-vimeo crown-icon" v-else></i>
                </div>

                <div class="comments-textarea"
                    :class="{ 'anonymous-mode': userMode === 'anonymous', 'superuser-mode': userMode === 'superuser' }">
                    <textarea placeholder="你是我一生只会遇见一次的惊喜 ..." v-model="form.comment"></textarea>

                    <svg t="1760235383700" class="comments-textarea-beauty" viewBox="0 0 1024 1024" version="1.1"
                        xmlns="http://www.w3.org/2000/svg" p-id="43702">
                        <path d="M521.309091 480.581818L50.036364 951.854545" fill="currentColor" p-id="43703"></path>
                        <path
                            d="M50.036364 963.490909c-3.490909 0-5.818182-1.163636-8.145455-3.490909-4.654545-4.654545-4.654545-11.636364 0-16.290909l471.272727-471.272727c4.654545-4.654545 11.636364-4.654545 16.290909 0s4.654545 11.636364 0 16.290909L58.181818 960c-2.327273 2.327273-4.654545 3.490909-8.145454 3.490909z"
                            fill="currentColor" p-id="43704"></path>
                        <path
                            d="M512 678.4c-3.490909 0-8.145455-2.327273-10.472727-5.818182-3.490909-5.818182-1.163636-12.8 3.490909-16.290909 361.890909-223.418182 434.036364-432.872727 448-512 4.654545-23.272727-4.654545-46.545455-22.109091-59.345454-60.509091-44.218182-176.872727 33.745455-178.036364 34.90909-484.072727 332.8-434.036364 542.254545-432.872727 544.581819 1.163636 5.818182-2.327273 12.8-8.145455 13.963636-5.818182 1.163636-12.8-2.327273-13.963636-8.145455-2.327273-9.309091-58.181818-225.745455 443.345455-569.018181 5.818182-3.490909 131.490909-88.436364 204.8-34.909091 24.436364 18.618182 37.236364 50.036364 31.418181 82.618182-15.127273 82.618182-88.436364 299.054545-458.472727 528.290909-2.327273 1.163636-4.654545 1.163636-6.981818 1.163636zM805.236364 966.981818c-80.290909 0-140.8-32.581818-148.945455-37.236363-216.436364-94.254545-354.909091 10.472727-356.072727 11.636363-4.654545 3.490909-12.8 3.490909-16.290909-2.327273-3.490909-4.654545-3.490909-12.8 2.327272-16.290909 5.818182-4.654545 150.109091-114.036364 380.509091-13.963636 0 0 1.163636 0 1.163637 1.163636 1.163636 1.163636 141.963636 82.618182 281.6-9.309091 5.818182-3.490909 12.8-2.327273 16.290909 3.49091 3.490909 5.818182 2.327273 12.8-3.490909 16.290909-54.690909 34.909091-109.381818 46.545455-157.090909 46.545454z"
                            fill="currentColor" p-id="43705"></path>
                    </svg>
                </div>
            </div>

            <div class="comments-tools">
                <span class="char-count" :class="{ 'text-error': form.comment.length > 500 }">
                    {{ form.comment.length }}/500
                </span>
                <button class="submit-btn" type="submit" :disabled="isSubmitting || !isFormValid">
                    <svg t="1760235383700" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"
                        p-id="43702">
                        <path d="M521.309091 480.581818L50.036364 951.854545" fill="currentColor" p-id="43703"></path>
                        <path
                            d="M50.036364 963.490909c-3.490909 0-5.818182-1.163636-8.145455-3.490909-4.654545-4.654545-4.654545-11.636364 0-16.290909l471.272727-471.272727c4.654545-4.654545 11.636364-4.654545 16.290909 0s4.654545 11.636364 0 16.290909L58.181818 960c-2.327273 2.327273-4.654545 3.490909-8.145454 3.490909z"
                            fill="currentColor" p-id="43704"></path>
                        <path
                            d="M512 678.4c-3.490909 0-8.145455-2.327273-10.472727-5.818182-3.490909-5.818182-1.163636-12.8 3.490909-16.290909 361.890909-223.418182 434.036364-432.872727 448-512 4.654545-23.272727-4.654545-46.545455-22.109091-59.345454-60.509091-44.218182-176.872727 33.745455-178.036364 34.90909-484.072727 332.8-434.036364 542.254545-432.872727 544.581819 1.163636 5.818182-2.327273 12.8-8.145455 13.963636-5.818182 1.163636-12.8-2.327273-13.963636-8.145455-2.327273-9.309091-58.181818-225.745455 443.345455-569.018181 5.818182-3.490909 131.490909-88.436364 204.8-34.909091 24.436364 18.618182 37.236364 50.036364 31.418181 82.618182-15.127273 82.618182-88.436364 299.054545-458.472727 528.290909-2.327273 1.163636-4.654545 1.163636-6.981818 1.163636zM805.236364 966.981818c-80.290909 0-140.8-32.581818-148.945455-37.236363-216.436364-94.254545-354.909091 10.472727-356.072727 11.636363-4.654545 3.490909-12.8 3.490909-16.290909-2.327273-3.490909-4.654545-3.490909-12.8 2.327272-16.290909 5.818182-4.654545 150.109091-114.036364 380.509091-13.963636 0 0 1.163636 0 1.163637 1.163636 1.163636 1.163636 141.963636 82.618182 281.6-9.309091 5.818182-3.490909 12.8-2.327273 16.290909 3.49091 3.490909 5.818182 2.327273 12.8-3.490909 16.290909-54.690909 34.909091-109.381818 46.545455-157.090909 46.545454z"
                            fill="currentColor" p-id="43705"></path>
                    </svg>
                    {{ isSubmitting ? '提交中...' : '发送评论' }}
                </button>
            </div>
        </form>
    </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, defineProps } from 'vue'
import Loading from './Loading.vue';
const props = defineProps({
    postId: {
        type: Number,
        required: true
    }
})

// 响应式数据

const loading = ref(false)

const showCommentForm = ref(false)
const isSubmitting = ref(false)
const userMode = ref('normal') // 'normal', 'anonymous', 'superuser'
const comments = ref([])
const isLoading = ref(false)
const form = reactive({
    name: '',
    email: '',
    website: '',
    comment: '',
    api_key: ''
})

// 匿名用户配置
const anonymousUser = {
    name: '匿名访客',
    email: 'ghost@shadow.com',
    website: ''
}

// 监听用户模式变化
watch(userMode, (newMode) => {
    if (newMode === 'anonymous') {
        form.name = anonymousUser.name
        form.email = anonymousUser.email
        form.website = anonymousUser.website
        form.api_key = ''
    } else if (newMode === 'normal') {
        form.name = ''
        form.email = ''
        form.website = ''
        form.api_key = ''
    } else if (newMode === 'superuser') {
        form.name = ''
        form.email = ''
        form.website = ''
    }
})

// 计算属性
const isFormValid = computed(() => {
    const hasValidComment = form.comment.trim() !== '' && form.comment.length <= 500

    if (userMode.value === 'superuser') {
        return hasValidComment && form.api_key.trim() !== ''
    } else if (userMode.value === 'anonymous') {
        return hasValidComment
    } else {
        return hasValidComment &&
            form.name.trim() !== '' &&
            form.email.trim() !== ''
    }
})

// 循环切换用户模式
const cycleUserMode = () => {
    const modes = ['normal', 'anonymous', 'superuser']
    const currentIndex = modes.indexOf(userMode.value)
    const nextIndex = (currentIndex + 1) % modes.length
    userMode.value = modes[nextIndex]
}

// 获取头像模式样式类
const getAvatarModeClass = () => {
    return {
        'normal': 'normal-mode',
        'anonymous': 'anonymous-mode',
        'superuser': 'superuser-mode'
    }[userMode.value]
}

// 关闭评论表单
const closeCommentForm = () => {
    showCommentForm.value = false
    // 重置表单
    form.name = ''
    form.email = ''
    form.website = ''
    form.comment = ''
    form.api_key = ''
    userMode.value = 'normal'
}

// 检查是否有网站
const hasWebsite = (comment) => {
    return comment.author_website && comment.author_website.trim() !== ''
}

// 获取头像颜色
const getAvatarColor = (name) => {
    const colors = [
        '#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b',
        '#fa709a', '#ff6b6b', '#a8edea', '#fed6e3', '#a8edea'
    ]
    let hash = 0
    for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash)
    }
    return colors[Math.abs(hash) % colors.length]
}

// 获取头像文本
const getAvatarText = (name) => {
    return name.charAt(0).toUpperCase()
}

// 确保网址有http前缀
const ensureHttp = (url) => {
    if (!url) return ''
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        return 'https://' + url
    }
    return url
}

// 格式化时间
const formatTime = (timeString) => {
    if (!timeString) return ''

    try {
        const date = new Date(timeString)
        const now = new Date()
        const diff = now - date

        // 如果是今天内
        if (diff < 24 * 60 * 60 * 1000) {
            if (diff < 60 * 60 * 1000) {
                const minutes = Math.floor(diff / (60 * 1000))
                return minutes <= 0 ? '刚刚' : `${minutes}分钟前`
            }
            const hours = Math.floor(diff / (60 * 60 * 1000))
            return `${hours}小时前`
        }

        // 如果是今年
        if (date.getFullYear() === now.getFullYear()) {
            return `${date.getMonth() + 1}月${date.getDate()}日`
        }

        return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
    } catch (error) {
        console.error('时间格式化错误:', error)
        return timeString
    }
}

// 获取评论列表
const fetchComments = async () => {
    isLoading.value = true
    try {
        const response = await fetch(`/api/comments/post/${props.postId}`)

        if (response.ok) {
            const data = await response.json()
            comments.value = data

            // 没有评论时候默认显示评论框
            if (!comments.value) {
                showCommentForm.value = true
            }
        } else {
            console.error('获取评论失败，状态码:', response.status)
            comments.value = []
        }
    } catch (error) {
        console.error('获取评论失败:', error)
        comments.value = []
    } finally {
        isLoading.value = false
    }
}

// 提交评论函数
const submitComment = async () => {
    if (!isFormValid.value) {
        alert('请填写完整信息且评论内容不超过500字')
        return
    }

    isSubmitting.value = true

    try {
        // 构建基础评论数据
        const commentData = {
            post_id: props.postId,
            content: form.comment,
            is_anonymous: userMode.value === 'anonymous'
        }

        // 根据模式添加不同的字段
        if (userMode.value === 'superuser') {
            // 超级用户模式：发送 api_key，其他字段设为空字符串
            commentData.api_key = form.api_key
            commentData.author_name = ""  // 发送空字符串而不是 null
            commentData.author_email = "" // 发送空字符串而不是 null
            commentData.author_website = "" // 发送空字符串而不是 null
        } else {
            // 普通用户和匿名用户模式：发送完整的用户信息
            commentData.author_name = form.name
            commentData.author_email = form.email
            commentData.author_website = form.website || "" // 确保不是 null
        }

        console.log('提交的数据:', commentData) // 调试用

        const response = await fetch('/api/comments/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(commentData)
        })

        if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.detail || `提交失败，状态码: ${response.status}`)
        }

        // 重置表单但保持用户模式状态
        form.comment = ''
        if (userMode.value !== 'anonymous') {
            form.name = ''
            form.email = ''
            form.website = ''
        }
        if (userMode.value === 'superuser') {
            form.api_key = ''
        }

        // 重新加载评论列表
        await fetchComments()

        // 关闭评论表单
        closeCommentForm()

    } catch (error) {
        console.error('提交评论错误:', error)
        alert(error.message || '提交失败，请重试')
    } finally {
        isSubmitting.value = false
    }
}

// 组件挂载时获取评论
onMounted(() => {
    fetchComments()

    setTimeout(() => {
        loading.value = false;
    }, 300);
})
</script>

<style scoped>
/* 超级用户头像样式 */
.superuser-avatar {
    position: relative;
    width: 44px;
    height: 44px;
}

.avatar-container {
    position: relative;
    width: 100%;
    height: 100%;
}

.avatar-img {
    width: 100%;
    height: 100%;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    object-fit: cover;
}

.vip-badge {
    position: absolute;
    bottom: -4px;
    right: -4px;
    width: 18px;
    height: 18px;
    background: linear-gradient(135deg, #ffd700, #ff8c00);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid white;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    z-index: 10;
}

.vip-badge .czs-vimeo {
    color: white;
    font-size: 10px;
    line-height: 1;
    font-weight: bold;
}

/* VIP徽章动画效果 */
@keyframes vipPulse {

    0%,
    100% {
        transform: scale(1);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    }

    50% {
        transform: scale(1.1);
        box-shadow: 0 3px 10px rgba(255, 140, 0, 0.5);
    }
}

.vip-badge {
    animation: vipPulse 2s ease-in-out infinite;
}

/* 悬停效果 */
.recent-item:hover .vip-badge {
    animation-duration: 1s;
}

/* 超级用户名字样式 */
.superuser-name {
    color: #ff8c00;
    font-weight: 700;
    position: relative;
}

.superuser-badge {
    display: inline-flex;
    align-items: center;
    margin-left: 6px;
}

.crown-badge {
    width: 14px;
    height: 14px;
    color: #ffd700;
}

/* 超级用户输入框 */
.superuser-input {
    margin-bottom: 20px;
}

.superuser-input input {
    width: 100%;
    border-radius: 12px;
    padding: 12px 15px;
    border: 2px solid #ffd700;
    font-size: 16px;
    transition: all 0.3s ease;
    background: #fffdf0;
    color: #4a5568;
}

.superuser-input input:focus {
    outline: none;
    border-color: #ffd700;
    background: #fffdf0;
    /* box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.1); */
}

.superuser-input input::placeholder {
    color: #a0aec0;
}

/* 头像模式样式 */
.avatar-icon.normal-mode {
    background: rgb(79, 172, 254);
    box-shadow: 0 4px 12px rgba(79, 172, 254, 0.3);
    color: #fff;
    font-size: 25px;
    transition: all 0.3s ease;
}

.avatar-icon.anonymous-mode {
    background: #2d3748;
    /* border: 2px solid #2d3748; */
    /* box-shadow: 0 4px 12px rgba(45, 55, 72, 0.3); */
    transition: all 0.3s ease;
}

.avatar-icon.superuser-mode {
    background: linear-gradient(135deg, #ffd700, #ffed6a);
    border: 2px solid #ffd700;
    color: #fff;
    box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
    transition: all 0.3s ease;
}

/* 头像悬停效果 - 改为向上偏移而不是放大 */
.avatar-icon:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.avatar-icon.normal-mode:hover {
    box-shadow: 0 6px 20px rgba(79, 172, 254, 0.4);
}

.avatar-icon.anonymous-mode:hover {
    box-shadow: 0 6px 20px rgba(45, 55, 72, 0.4);
}

.avatar-icon.superuser-mode:hover {
    box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
}

/* 文本区域超级用户模式 */
.comments-textarea.superuser-mode textarea {
    background: #fffdf0;
    border: 2px solid #ffd700;
    color: #4a5568;
    transition: all 0.3s ease;
}

.comments-textarea.superuser-mode textarea:focus {
    border-color: #ffd700;
    background: #fffdf0;
    box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.1);
}

.comments-textarea.superuser-mode .comments-textarea-beauty {
    /* color: #ffd700; */
    transition: all 0.3s ease;
}

.comments-textarea.superuser-mode:hover .comments-textarea-beauty {
    /* color: #d97706; */
}

/* 皇冠图标动画 */
@keyframes crownGlow {

    0%,
    100% {
        filter: drop-shadow(0 0 2px rgba(255, 215, 0, 0.6));
    }

    50% {
        filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.9));
    }
}

.avatar-icon.superuser-mode .crown-icon {
    animation: crownGlow 2s ease-in-out infinite;
}

/* 评论列表样式 */
.comments-list {
    margin-bottom: 40px;
}

.comments-list-header {
    margin-bottom: 25px;
    padding-bottom: 15px;
    border-bottom: 2px solid #e2e8f0;
}

.comments-list-header h3 {
    color: #4a5568;
    font-size: 20px;
    font-weight: 700;
    margin: 0;
}

/* 美化后的评论列表 */
.recent-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.recent-item {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 20px;
    border-radius: 16px;
    background: white;
    border: 1px solid #f1f5f9;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    position: relative;
}

.recent-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    border-color: #e2e8f0;
}

.recent-avatar {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 16px;
    font-weight: 700;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
}

.recent-item:hover .recent-avatar {
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
    transform: translateY(-2px);
}

.recent-content {
    flex: 1;
    min-width: 0;
}

.recent-header {
    margin-bottom: 8px;
}

.recent-author-info {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.recent-author {
    font-weight: 600;
    color: #2d3748;
    font-size: 16px;
}

.author-link {
    color: #2d3748;
    text-decoration: none;
    transition: color 0.3s ease;
}

.author-link:hover {
    color: #667eea;
}

/* 匿名用户样式 */
.anonymous-user {
    color: #a0aec0;
}

/* 低调的时间样式 */
.comment-time {
    color: #a0aec0;
    font-size: 13px;
    font-weight: 400;
    opacity: 0.8;
}

.comment-text {
    color: #4a5568;
    line-height: 1.6;
    font-size: 15px;
    word-wrap: break-word;
}

/* 空状态 */
.no-comments {
    text-align: center;
    padding: 60px 20px;
    margin-bottom: 40px;
}

.empty-state {
    color: #a0aec0;
}

.empty-state i {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
}

.empty-state p {
    font-size: 16px;
    margin: 0;
    font-style: italic;
}

/* 评论触发按钮 */
.comment-trigger {
    text-align: center;
    margin: 30px 0;
}

.trigger-btn {
    background-color: transparent;
    color: #333;
    border: none;
    padding: 12px 24px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.trigger-btn:hover {
    transform: translateY(-2px);
    /* box-shadow: 0 8px 20px rgba(102, 126, 234, 0.6); */
}

.trigger-btn svg {
    width: 16px;
    height: 16px;
}

/* 评论表单 */
.comment-form {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin-top: 30px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    border: 1px solid #e2e8f0;
}

.form-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid #f1f5f9;
}

.form-header h3 {
    color: #4a5568;
    font-size: 18px;
    font-weight: 600;
    margin: 0;
}

.close-btn {
    background: none;
    border: none;
    font-size: 24px;
    color: #a0aec0;
    cursor: pointer;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.3s ease;
}

.close-btn:hover {
    background: #f7fafc;
    color: #4a5568;
}

.comments-head {
    display: flex;
    list-style: none;
    width: 100%;
    gap: 15px;
    padding-left: 0px;
    margin-left: 0px;
    margin-bottom: 20px;
    padding: 0;
}

.comments-head li {
    flex: 1;
}

.comments-head input {
    width: 100%;
    border-radius: 12px;
    padding: 12px 15px;
    border: 2px solid #e2e8f0;
    font-size: 16px;
    transition: all 0.3s ease;
    background: #f8fafc;
    color: #4a5568;
}

.comments-head input:focus {
    outline: none;
    border-color: rgb(79, 172, 254);
    background: white;
    box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.1);
}

.comments-head input:disabled {
    background: #f7fafc;
    color: #a0aec0;
    cursor: not-allowed;
    border-color: #e2e8f0;
}

.comments-body {
    display: flex;
    align-items: flex-start;
    gap: 15px;
    margin-bottom: 20px;
}

.comments-body textarea {
    flex: 1;
    border-radius: 12px;
    min-height: 120px;
    width: 100%;
    padding: 15px;
    padding-right: 50px;
    border: 2px solid #e2e8f0;
    font-size: 16px;
    line-height: 1.6;
    color: #4a5568;
    resize: vertical;
    transition: all 0.3s ease;
    background: white;
}

.comments-textarea.anonymous-mode textarea {
    background: #1a202c;
    border: 2px solid #4a5568;
    color: #e2e8f0;
}

.comments-body textarea:focus {
    outline: none;
    border-color: rgb(79, 172, 254);
    background: white;
    box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.1);
}

.comments-textarea.anonymous-mode textarea:focus {
    border-color: #2d3748;
    background: #2d3748;
    /* box-shadow: 0 0 0 3px rgba(45, 55, 72, 0.1); */
}

#comments input::placeholder,
#comments textarea::placeholder {
    color: #a0aec0;
    font-size: 15px;
}

.comments-textarea.anonymous-mode textarea::placeholder {
    color: #718096;
}

.comments-textarea {
    position: relative;
    flex: 1;
}

.comments-textarea-beauty {
    position: absolute;
    bottom: 15px;
    right: 15px;
    width: 60px;
    height: 60px;
    color: #a0aec0;
    transition: all 0.3s ease;
    z-index: 2;
}

.comments-textarea:hover .comments-textarea-beauty {
    /* color: #667eea; */
}

.comments-textarea.anonymous-mode .comments-textarea-beauty {
    /* color: #718096; */
}

.comments-textarea.anonymous-mode:hover .comments-textarea-beauty {
    /* color: #805ad5; */
}

.comments-tools {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
    gap: 15px;
}

.submit-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 12px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    display: flex;
    align-items: center;
    gap: 8px;
    white-space: nowrap;
}

.submit-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.6);
}

.submit-btn:active {
    transform: translateY(0);
}

.submit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

.submit-btn svg {
    width: 16px;
    height: 16px;
}

.avatar-icon {
    width: 50px;
    height: 50px;
    border-radius: 12px;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-shrink: 0;
    cursor: pointer;
}

.char-count {
    color: #a0aec0;
    font-size: 14px;
    flex-shrink: 0;
}

.text-error {
    color: #e53e3e;
    font-weight: 600;
}

.anonymous-avatar {
    background: linear-gradient(135deg, #4a5568, #2d3748);
    color: #fff;
    display: flex;
    justify-content: center;
    align-items: center;
}

.anonymous-icon,
.anonymous-avatar .icon {
    width: 30px;
    height: 30px;
    fill: #fff;
}

/* 幽灵图标动画 */
@keyframes ghostFloat {

    0%,
    100% {
        transform: translateY(0px);
    }

    50% {
        transform: translateY(-3px);
    }
}

.avatar-icon.anonymous-mode .ghost-icon {
    animation: ghostFloat 3s ease-in-out infinite;
}

/* 响应式设计 */
@media (max-width: 768px) {
    #comments {
        padding: 20px;
    }

    .comments-head {
        flex-direction: column;
        gap: 10px;
    }

    .comments-body {
        flex-direction: column;
    }

    .avatar-icon {
        align-self: center;
    }

    .comments-tools {
        flex-direction: column;
        gap: 15px;
        align-items: stretch;
    }

    .char-count {
        text-align: center;
    }

    .recent-item {
        padding: 16px;
        gap: 12px;
    }

    .recent-avatar {
        width: 40px;
        height: 40px;
        font-size: 14px;
    }

    .recent-author-info {
        flex-direction: column;
        align-items: flex-start;
        gap: 6px;
    }

    .comment-text {
        font-size: 14px;
    }
}
</style>