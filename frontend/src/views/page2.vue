<template>
    <div class="header"> <!--页面顶端的浮动框-->
        <p class='headtext'>海洋牧场 某某页面(page2)</p>
        <div class="head-links">
            <button class="ok" @click="jump1()">跳转1</button>
            <button class="ok" @click="jump2()">跳转2</button>
        </div>
    </div>


</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {

        };
    },
    methods: {
        jump1() {
            console.log("跳转1");
        },
        jump2() {
            console.log("跳转2");
        }
    }  //end methods
} // end export

</script>

<style></style>