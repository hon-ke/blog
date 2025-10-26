<template>
  <div class="layout">
    <Header />
    <section id="core" class="container off-canvas off-canvas-sidebar-show">
      <slot name="core">
        <Aside />
        <main id="main" class="uni-bg uni-shadow off-canvas-content">
          <slot name="main">
            <div class="content">
              <Loading v-if="loading" :visible="loading" :count="3" />
              <router-view v-show="!loading" />
            </div>

          </slot>
        </main>
      </slot>
    </section>
    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import Header from './Header.vue';
import Aside from './Aside.vue';
import Footer from './Footer.vue';
import Loading from './Loading.vue';
const route = useRoute();
const loading = ref(true);

// 路由切换加载状态
watch(() => route.path, (newPath, oldPath) => {
  if (newPath !== oldPath) {
    loading.value = true;
    // 使用 requestAnimationFrame 确保动画流畅
    requestAnimationFrame(() => {
      setTimeout(() => {
        loading.value = false;
      }, 300);
    });
  }
});

onMounted(() => {
  setTimeout(() => {
    loading.value = false;
  }, 300);
});
</script>

<style>
@import "@/assets/css/style.css";
@import "@/assets/css/icons.css";
</style>
