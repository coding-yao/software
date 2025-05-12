<template>
  <div class="header"> <!--页面顶端的浮动框-->
    <p class='headtext'>海洋牧场 数据可视化页面</p>
    <div class="head-links">
      <button class="ok" @click="jump1()">跳转1</button>
      <button class="ok" @click="jump2()">跳转2</button>
    </div>
  </div>

</template>

<script>
import axios from 'axios'; // 引入axios库，用于发起HTTP请求  

export default {
  data() { // data里定义数据
    return {

    };
  },// end data
  methods: {// methods里定义函数
    jump1() {
      console.log("跳转1");
    },
    jump2() {
      console.log("跳转2");
    }
  }// end methods
}// END export default
</script>

<style></style>