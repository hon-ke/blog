<template>
  <footer id="footer">
    <div class="d-flex flex-center justify-between flex-wrap">
      <div class="left">
        <span>&copy; 2025 <a href="/">红客路上</a></span>
      </div>
      <div class="right">
        <span>Theme by <a class="theme-name" href="https://biji.io/" target="_blank">Wing</a></span>
      </div>
    </div>
    
    <!-- 滚动工具 - 可根据需要启用 -->
    <Actions />
  </footer>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import Actions from './Actions.vue';

const showScrollTools = ref(false);

// // 监听滚动显示工具
// const handleScroll = () => {
//   showScrollTools.value = window.scrollY > 300;
// };

// onMounted(() => {
//   window.addEventListener('scroll', handleScroll);
// });

// onUnmounted(() => {
//   window.removeEventListener('scroll', handleScroll);
// });
</script>
