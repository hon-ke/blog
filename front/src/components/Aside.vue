<template>
  <aside id="aside" class="off-canvas-sidebar">
    <div class="probes"></div>

    <section class="sticky">
      <Heatmap></Heatmap>

      <ul class="header_nav reset-ul uni-bg uni-shadow">
        <li
          class="czs-home-l menu-item"
          :class="{ 'current-menu-item': isCurrentRoute('/') }"
        >
          <router-link to="/" @click="setCurrentMenu('/')">首页</router-link>
        </li>
        <li
          v-for="x in categories"
          class="menu-item"
          :class="[
            x.icon,
            { 'current-menu-item': isCurrentRoute('/category/' + x.name) },
          ]"
        >
          <router-link
            :to="'/category/' + x.name"
            @click="setCurrentMenu('/category/' + x.name)"
            >{{ x.name }}</router-link
          >
        </li>
      </ul>

      <ul
        v-if="pagesData.length > 0"
        class="footer_nav reset-ul uni-bg uni-shadow"
      >
        <li
          v-for="x in pagesData"
          class="page-nav menu-item"
          :class="[
            x.icon,
            { 'current-menu-item': isCurrentRoute('/' + x.title) },
          ]"
        >
          <router-link
            :to="'/' + x.title"
            @click="setCurrentMenu('/' + x.title)"
            >{{ x.title }}</router-link
          >
        </li>
      </ul>

      <div class="reset-ul uni-bg uni-shadow flex-center widget_block">
        <ul
          class="wp-block-social-links is-style-default is-content-justification-center is-layout-flex"
        >
          <li class="wp-social-link wp-social-link-github wp-block-social-link">
            <a
              rel="noopener nofollow"
              target="_blank"
              href="https://github.com/hon-ke"
              class="wp-block-social-link-anchor"
            >
              <i class="czs-github-logo"></i>
            </a>
          </li>
        </ul>
      </div>
    </section>
  </aside>
  <a href="#close" class="off-canvas-overlay"></a>
</template>

<script setup>
import { useRoute } from "vue-router";
import Heatmap from "./Heatmap.vue";
import { ref, onMounted, computed, watch } from "vue";
import axios from "axios";

const route = useRoute();

const categories = ref([]);
const pagesData = ref([]);
const currentMenu = ref("");

// 从 localStorage 获取当前菜单
const getCurrentMenu = () => {
  return localStorage.getItem("current_menu") || "";
};

// 设置当前菜单到 localStorage
const setCurrentMenu = (path) => {
  currentMenu.value = path;
  localStorage.setItem("current_menu", path);
};

// 监听路由变化，自动更新当前菜单
watch(
  () => route.path,
  (newPath) => {
    currentMenu.value = newPath;
    localStorage.getItem("current_menu", newPath);
  }
);

// 判断当前路由是否匹配的方法
const isCurrentRoute = (path) => {
  return currentMenu.value === path;
};

// 或者为每个分类分配图标
const assignIconsToCategories = (categories) => {
  const categoryIconList = [
    "czs-cup-l",
    "czs-code-l",
    "czs-heart-l",
    "czs-chemistry-l",
    "czs-commed2-l",
    "czs-dashboard-l",
    "czs-crown-l",
    "czs-folder-l",
    "czs-fingerprint-l",
    "czs-moments",
  ];
  return categories.map((category, index) => {
    const icon = categoryIconList[index % categoryIconList.length];
    return {
      name: category,
      icon: icon,
    };
  });
};

onMounted(() => {
  // 从 localStorage 恢复当前菜单
  currentMenu.value = getCurrentMenu();

  // 如果当前没有菜单状态，使用当前路由
  if (!currentMenu.value && route.path) {
    currentMenu.value = route.path;
  }

  // 分类
  axios
    .get("/api/posts/categories")
    .then((res) => {
      categories.value = assignIconsToCategories(res.data);
    })
    .catch((err) => {
      categories.value = [];
    });

  // 获取页面
  axios
    .get("/api/pages/")
    .then((res) => {
      pagesData.value = res.data;
    })
    .catch((err) => {
      pagesData.value = [];
    });
});
</script>

<style>
.page-nav::before {
  top: 11px !important;
}

.wp-block-social-links {
  list-style: none;
  margin: 0 !important;
}

.wp-block-social-links a i {
  font-size: 30px;
  color: #66758c;
}

.wp-block-social-links a i:hover {
  color: #3366ff;
}
</style>
