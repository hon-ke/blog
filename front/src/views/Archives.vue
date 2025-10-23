<template>
    <article v-if="data" class="article archives" itemscope="" itemtype="https://schema.org/Article">
        <div class="archive" v-for="x in data">
            <div class="archive__title">
                <div class="archive__title-title">
                    <i class="czs-circle archive__title-icon"></i>
                    <span class="muted ellipsis">{{x.date}}</span>年<span class="muted ellipsis">{{x.data.length}}</span>篇
                    <span>文章</span>
                </div>
            </div>
            <ul class="archive__list" data-wow="off">
                <li class="archive-item" v-for="y in x.data">
                    <span class="post-time">{{y.time}}</span>
                    <a :href="'/post/'+y.id"><span>{{y.title}}</span></a>
                </li>
            </ul>
        </div>
    </article>
    <Empty v-else></Empty>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';

import Empty from '../components/Empty.vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const data = ref([])

watch(
    () => route.path,
    (newPath, oldPath) => {
        if (newPath !== oldPath) {

            axios.get("/api/posts/archive").then(res => {
                data.value = res.data
                
            }).catch(
                data.value = []
            )
        }
    },
    { immediate: true } // 立即执行一次，替代 onMounted
);

</script>


<style>
.archive__title {
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    height: 45px;
    line-height: 45px;
    vertical-align: middle;
    border-bottom: 1px solid #ebeef5
}

.archive__title-icon {
    margin-right: 5px;
    color: #fb6c28;
    font-size: 18px;
    vertical-align: middle
}

.archive__title-title {
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center
}

.archive__title-title .muted {
    position: relative;
    top: 0px;
    margin: 0 5px;
    color: #fb6c28;
    font-weight: 700
}

.archive__list {
    list-style: none;
    padding-left: 0;
    margin: 0;
    margin-top: 15px;
}

.archive-item {
    margin-left: 15px;
    display: flex;
    align-items: center;
    position: relative;
}

.archive-item:last-child {
    border-bottom: none;
}

.archive-item::before {
    content: "";
    display: inline-block;
    width: 6px;
    height: 6px;
    background-color: #66758c;
    border-radius: 50%;
    margin-right: 12px;
    flex-shrink: 0;
}

.archive-item .post-time {
    margin-right: 15px;
    color: #66758c;
    font-size: 15px;
    min-width: 80px;
    flex-shrink: 0;
}

body .archive-item a {
    color: #3366ff;
    text-decoration: none;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}


.archive-item a:hover{
    color: #fb6c28;
}

</style>