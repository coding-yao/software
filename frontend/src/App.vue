<script setup>
// import { RouterLink, RouterView } from 'vue-router'
// import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <router-view />
</template>

<style>
body {
  background-image: url('@/assets/bg.jpg');
  background-size: cover; /* 覆盖整个页面 */
  background-position: center; /* 居中显示 */
  background-repeat: no-repeat; /* 不重复 */
  background-attachment: fixed; /* 固定背景，滚动时不移动 */
}
</style>