<template>
    <NavBar current-page="smarthub" />
    <div class="main-content">
        <!-- 这里可以添加页面2的内容 -->
        <WeatherWidget />
    </div>
    <div class="bilibili-video">
    <iframe 
      :src="`//player.bilibili.com/player.html?bvid=${bvid}&page=1`"
      scrolling="no"
      border="0"
      frameborder="no"
      framespacing="0"
      allowfullscreen="true"
      width="100%"
      height="500"
    ></iframe>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import WeatherWidget from '@/components/WeatherWidget.vue';

export default {
    components: {
        NavBar,
        WeatherWidget
    },
    data() {
        return {
            bvid: "BV1Ts4y1872o"
        };
    }
}
</script>

<style scoped>
.main-content {
    margin-top: 80px; /* 为固定定位的导航栏留出空间 */
    padding: 20px;
}
</style>