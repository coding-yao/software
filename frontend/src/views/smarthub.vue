<template>
  <NavBar current-page="smarthub" />
  <div class="main-content">
    <WeatherWidget />
    <div class="video-container">
      <iframe 
        :src="`//player.bilibili.com/player.html?bvid=${bvid}&page=1`"
        scrolling="no"
        frameborder="no"
        allowfullscreen="true"
      ></iframe>
    </div>
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
            bvid: "BV1X64y1j7Ff"
        };
    }
}
</script>

<style scoped>
.main-content {
    margin-top: 80px; /* 为固定定位的导航栏留出空间 */
    padding: 20px;
    max-width: 1200px;
    margin-left: auto;
    margin-right: auto;
}

.video-container {
    margin-top: 20px;
    position: relative;
    width: 100%;
    padding-bottom: 56.25%; /* 16:9 宽高比 */
    overflow: hidden;
    border-radius: 8px;
}

.video-container iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: none;
}
</style>