<template>
      <router-view />

</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { watch } from 'vue'
const route = useRoute()

// 监听路由变化，设置正确的标题
watch(
  () => route.meta?.title,
  (newTitle) => {
    if (newTitle) {
      // 解码标题
      const decodedTitle = decodeURIComponent(newTitle)
      document.title = decodedTitle
    } else {
      document.title = '红客路上'
    }
  },
  { immediate: true }
)
</script>

<style>
@import "./assets/css/style.css";
@import "./assets/css/icons.css";
@import "./assets/css/post.css";
@import "./assets/css/links.css";
@import "./assets/css/fix.css";
</style>
