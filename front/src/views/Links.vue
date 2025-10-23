<template>
    <div class="friend-links-grid markdown-body" v-html="content"></div>
</template>

<script setup>
import { md } from '@/assets/js/marked-wrapper'
import { formatTime } from '@/assets/js/tools'
import axios from 'axios';
import { ref, onMounted } from 'vue';
// 图片加载错误处理
const handleImageError = (event) => {
    event.target.src = '/img/friend_404.gif';
};
const content = ref("")

onMounted(() => {
    axios.get("/api/pages/links").then(res => {

        content.value = md.parse(res.data.content)

    })
})

</script>

