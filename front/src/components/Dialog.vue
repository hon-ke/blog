<template>
    <div class="modal article-dialog" :class="{ 'active': visible }">
        <a href="javascript:void(0);" class="modal-overlay" @click="handleClose"></a>
        <div class="uni-bg uni-shadow bg-blur notes-item" :class="itemClass">
            <div class="tile d-block">
                <div class="tile-header flex-center justify-between">
                    <div class="article-header text-gray text-tiny d-flex align-center">
                        <div class="flex-center">
                            <time itemprop="datePublished" pubdate="" class="mr-2">
                                {{ formatTime(timeAgo) }}
                            </time>
                        </div>
                    </div>
                    <button href="javascript:void(0);" class="btn btn-clear" @click="handleClose"></button>
                </div>
                <div class="tile-content p-0">
                    <div class="flex-wrap d-flex">
                        <div class="article-content" v-html="md.parse(renderedContent)"></div>
                    </div>
                </div>
                <div class="tile-footer text-gray text-tiny flex-center justify-between">
                    <div class="flex-center">
                        <button class="btn btn-link btn-sm text-gray mr-2">
                            <i class="czs-talk"></i>
                            {{ article.commentsCount || 0 }}
                        </button>
                        <button class="btn btn-link btn-sm text-gray mr-2" @click="handleLike">
                            <i class="czs-heart" :class="{ 'text-primary': article.isLiked }"></i>
                            <span :class="`praise-${article.id}`">{{ article.likesCount || 0 }}</span>
                        </button>
                    </div>
                    <span class="flex-center">
                        <i class="dashicons dashicons-laptop mr-1"></i>
                        {{ article.source || 'Write from Webpage' }}
                    </span>
                </div>
            </div>
            <div class="divider"></div>
        </div>
    </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { formatTime } from '../assets/js/tools'
import { md } from '../assets/js/marked-wrapper'
// 定义 Props
const props = defineProps({
    // 是否显示模态框
    visible: {
        type: Boolean,
        default: false
    },
    // 文章对象，包含所有文章数据
    article: {
        type: Object,
        required: true,
        default: () => ({
            id: null,
            content: '',
            created_at: '',
            category: '',
            commentsCount: 0,
            likes: 0,
            source: 'Write from Webpage',
            isLiked: false
        })
    }
})

// 定义 Emits
const emit = defineEmits(['update:visible', 'close', 'like', 'update:article'])

// 响应式数据
const localArticle = ref({ ...props.article })

// 计算属性
const itemClass = computed(() => `feat-${localArticle.value.id}-9x5pu9rrpa`)

const formattedDate = computed(() => {
    const date = new Date(localArticle.value.created_at)
    return date.toISOString().replace('T', ' ').substring(0, 19)
})


const renderedContent = computed(() => {
    let content = localArticle.value.content || ''

    // 如果有分类标签，添加到内容前面
    if (localArticle.value.category) {
        const categoryHtml = `<span class="chip c-hand text-primary" data-topic="#${localArticle.value.category}">${localArticle.value.category}</span>`
        content = categoryHtml + ' ' + content
    }

    return content
})

// 方法
const handleClose = () => {
    emit('update:visible', false)
    emit('close')
}

const handleLike = () => {
    localArticle.value.isLiked = !localArticle.value.isLiked
    localArticle.value.likesCount += localArticle.value.isLiked ? 1 : -1

    // 通知父组件文章数据已更新
    emit('update:article', { ...localArticle.value })
    emit('like', {
        id: localArticle.value.id,
        liked: localArticle.value.isLiked,
        likesCount: localArticle.value.likesCount
    })
}

// 监听外部 article prop 的变化
watch(() => props.article, (newArticle) => {
    localArticle.value = { ...newArticle }
}, { deep: true, immediate: true })
</script>