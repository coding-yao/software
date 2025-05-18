<template>
  <NavBar current-page="underwater" />
  <div class="figures-container">     <!-- 各种图的容器 -->
    <div ref="pieChart" style="width: 600px; height: 400px;"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import axios from 'axios';
import NavBar from '@/components/NavBar.vue';

export default {
  components: {
    NavBar
  },
  data() {
    return {
      speciesData: []  // 存储后端返回的数据
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    // 从后端获取数据
    async fetchData() {
      try {
        const response = await axios.get('http://localhost:8000/api/fishdata/get_fish_data'); //向后端的api应用里发出get请求
        console.log(response);
        // _________________________________________
        this.speciesData = response.data;
        this.renderPieChart();
      } catch (error) {
        console.error('数据获取失败:', error);
      }
    },
    // 渲染饼图
    renderPieChart() {
      const chartDom = this.$refs.pieChart;
      const chart = echarts.init(chartDom);
      
      // 配置项
      const option = {
        title: {
          text: '不同物种数量分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'  // 悬停显示数值和百分比
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: this.speciesData.map(item => item.Species)  // 图例数据
        },
        series: [{
          name: '数量',
          type: 'pie',
          radius: '55%',
          data: this.speciesData.map(item => ({
            value: item.count,
            name: item.Species
          })),
          emphasis: {  // 高亮样式
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          // 点击事件：筛选物种（需自行实现筛选逻辑）
          selectedMode: 'single',
          selectedOffset: 10
        }]
      };

      // 设置配置项
      chart.setOption(option);

      // 点击事件监听
      chart.on('click', params => {
        const selectedSpecies = params.name;
        this.$emit('species-selected', selectedSpecies);  // 向父组件传递选中物种
      });

      // 窗口大小变化时自适应
      window.addEventListener('resize', () => {
        chart.resize();
      });
    },
  }  //end methods
} // end export

</script>

<style scoped>
.figures-container {
    position: relative;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #f4f4f4;
    margin-top: 80px; /* 为固定定位的导航栏留出空间 */
}

</style>