<template>
    <NavBar current-page="smarthub" />
    <div class="main-content">
        <!-- 这里可以添加页面2的内容 -->
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