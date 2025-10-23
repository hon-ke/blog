<template>
  <header id="header">
    <hgroup class="logo">
      <h1 class="fullname">
        红客路上
      </h1>
    </hgroup>

    <section class="header__right d-flex">
      <!-- <form @submit.prevent="handleSearch" class="search">
        <input v-model="searchKeyword" class="search-key btn btn-link btn-action right-btn uni-bg uni-shadow"
          placeholder="请输入关键词..." type="text" required />
        <i class="text-small czs-search-l flex-center"></i>
      </form> -->
      <a @click="showSearch = true"class="btn btn-link btn-action right-btn uni-bg uni-shadow flex-center">
        <i class="text-small czs-search-l flex-center"></i>
      </a>

      <a  class="btn btn-link btn-action right-btn uni-bg uni-shadow menu-btn off-canvas-toggle flex-center ml-2"
        href="#aside">
        <i class="text-large czs-menu-l flex-center"></i>
      </a>
    </section>
    <Search v-model="showSearch"></Search>
  </header>



</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import Search from './Search.vue';
const router = useRouter();
const searchKeyword = ref('');
const showSearch = ref(false);

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push(`/?s=${encodeURIComponent(searchKeyword.value.trim())}`);
  }
};
</script>

<style scoped>
#header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo .fullname {
  color: #66758c;
  text-decoration: none;
  margin: 0;
}
</style>
