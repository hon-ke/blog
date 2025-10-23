<template>
    <ul class="header_nav reset-ul uni-bg uni-shadow">
        <div class="heatmap">
            <div class="heatmap-mvp d-flex">
                <div class="heatmap-mvp__item">
                    <h5>{{ distribution?.statistics?.days|| 0 }}</h5>
                    <span>DAYS</span>
                </div>
                <div class="heatmap-mvp__item">
                    <h5>{{ distribution?.statistics?.notes|| 0  }}</h5>
                    <span>NOTES</span>
                </div>
                <div class="heatmap-mvp__item">
                    <h5>{{ distribution?.statistics?.posts || 0}}</h5>
                    <span>POSTS</span>
                </div>
            </div>

            <div class="heatmap-map d-flex">
                <div v-for="(item, index) in distribution.data" :key="index" :data-tooltip="formatTooltip(item)"
                    class="heatmap-map__item tooltip link">
                    <div class="heatmap-map__item-block">
                        <div :class="[
                            'heatmap-map__item-inner',
                            getHeatClass(item.heat),
                            { active: item.heat > 0 }
                        ]"></div>
                    </div>
                </div>
            </div>

            <!-- <Loading v-if="loading" type="heatmap" /> -->
        </div>
    </ul>

</template>

<script setup>
import { ref, onMounted, Comment } from 'vue';
import axios from 'axios';
import Loading from './Loading.vue';

const distribution = ref({ data: [] });
const loading = ref(true);

// 计算热力块类名
const getHeatClass = (heat) => {
    if (heat > 0 && heat <= 3) return 'comments';
    if (heat > 3 && heat <= 8) return 'notes';
    return '';
};

// 格式化提示信息
const formatTooltip = (data) => {

    if (!data) return '无数据';

    const { date, post = 0, share = 0, note = 0, comment = 0 } = data;
    const parts = [date || '无日期'];

    if (post > 0) parts.push(`文章: ${post}`);
    if (share > 0) parts.push(`分享: ${share}`);
    if (note > 0) parts.push(`笔记: ${note}`);
    if (comment > 0) parts.push(`评论: ${comment}`);

    return parts.join('\n');
};

onMounted(async () => {
    try {
        const response = await axios.get("/api/heatmap/type-distribution?days=60");
        distribution.value = response.data;

        // setTimeout(() => {
        //     loading.value = false;
        // }, 800);

    } catch (error) {
        console.error('获取热力图数据失败:', error);
    } finally {
        loading.value = false;
    }
});
</script>