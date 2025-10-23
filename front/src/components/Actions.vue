<template>

    <div class="scroll-tools mr-2" :class="{ show: showBackToTop }">
        <!-- 暂时不显示 -->
        <div v-show="false" hover-show="" perspective="" class="dropdown"><a href="javascript:void(0);" tabindex="0"
                class="btn btn-link btn-action uni-bg bg-blur uni-shadow dropdown-toggle flex-center"><i
                    class="czs-clothes-l"></i></a>
            <ul class="menu menu-left mode-switch uni-card uni-bg bg-blur uni-shadow text-center">
                <li class="menu-item"><a data-mode="auto" href="javascript:void(0);" class="flex-center"><i
                            class="czs-bot mr-1"></i>自动
                    </a></li>
                <li class="menu-item"><a data-mode="light" href="javascript:void(0);" class="flex-center"><i
                            class="czs-sun mr-1"></i>明亮
                    </a></li>
                <li class="menu-item"><a data-mode="dark" href="javascript:void(0);" class="flex-center"><i
                            class="czs-moon mr-1"></i>黑暗
                    </a></li>
            </ul>
        </div>
        <div style="height: 0.4rem;"></div>
        <!-- 暂时不显示 -->
        <div v-show="false" hover-show="" perspective="" class="dropdown"><a href="javascript:void(0);" tabindex="0"
                class="btn btn-link btn-action uni-bg bg-blur uni-shadow dropdown-toggle flex-center"><i
                    class="czs-earth"></i></a>
            <ul class="menu menu-left mode-switch uni-card uni-bg bg-blur uni-shadow">
                <li class="menu-item"><a data-mode="zh_CN" href="javascript:void(0);" class="flex-center"><i
                            class="mr-1"></i>🇨🇳 简体中文
                    </a></li>
                <li class="menu-item"><a data-mode="zh_TC" href="javascript:void(0);" class="flex-center"><i
                            class="mr-1"></i>🇭🇰 繁体中文
                    </a></li>
                <li class="menu-item"><a data-mode="ja" href="javascript:void(0);" class="flex-center"><i
                            class="mr-1"></i>🇯🇵 Japanese
                    </a></li>
                <li class="menu-item"><a data-mode="en" href="javascript:void(0);" class="flex-center"><i
                            class="mr-1"></i>🇺🇸 English
                    </a></li>
            </ul>
        </div>
        <div style="height: 0.4rem;"></div>
        <a href="/icons" class="btn btn-link btn-action uni-bg bg-blur uni-shadow flex-center">
            <i class="czs-dashboard-l"></i>
        </a>
        <div style="height: 0.4rem;"></div>
        <a @click="scrollToTop" class="scroll-top btn btn-link btn-action uni-bg bg-blur uni-shadow flex-center"><i
                class="czs-angle-up-l"></i></a>
    </div>

</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const showBackToTop = ref(false);

// 滚动距离阈值（超过这个距离显示按钮）
const SCROLL_THRESHOLD = 400;

const checkScrollPosition = () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    showBackToTop.value = scrollTop > SCROLL_THRESHOLD;
};

const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
};

const toggleTheme = () => {
    // 主题切换逻辑
    document.body.classList.toggle('dark');
};

// 监听滚动事件
onMounted(() => {
    window.addEventListener('scroll', checkScrollPosition, { passive: true });
    // 初始检查一次
    checkScrollPosition();
});

onUnmounted(() => {
    window.removeEventListener('scroll', checkScrollPosition);
});
</script>

<style></style>