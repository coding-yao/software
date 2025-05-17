<template>
  <NavBar current-page="main" />
  <div class="main-content">
    <!-- 这里可以添加主页的内容 -->
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'

export default {
  components: {
    NavBar
  },
  data() {
    return {
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