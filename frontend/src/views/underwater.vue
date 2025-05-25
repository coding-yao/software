<template>
  <NavBar current-page="underwater" />
  <div class="figures-container">
    <div ref="pieChart" style="width: 50%; height: 500px;"></div>
    <div v-if="selectedSpecies" class="detail-charts" style="width: 50%;">
      <div ref="radarChart" style="height: 500px;"></div>
      <div ref="boxplotChart" style="height: 500px;"></div>
      <div ref="scatterChart" style="height: 500px;"></div>
    </div>
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
      fish_data_list: [],
      speciesData: [],
      selectedSpecies: null,
      radarChart: null,
      boxplotChart: null,
      scatterChart: null
    };
  },
  mounted() {
    this.fetchData();
    window.addEventListener('resize', this.resizeCharts);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.resizeCharts);
    if (this.radarChart) this.radarChart.dispose();
    if (this.boxplotChart) this.boxplotChart.dispose();
    if (this.scatterChart) this.scatterChart.dispose();
  },
  methods: {
    async fetchData() {
      const accessToken = localStorage.getItem('accesstoken');
      try {
        const response = await axios.get(
          'http://localhost:8000/api/fish/fish_list/',
          { headers: { 'Authorization': `Bearer ${accessToken}` } }
        );
        this.fish_data_list = response.data.fish_group;
        
        const speciesCount = {};
        this.fish_data_list.forEach(fish => {
          speciesCount[fish.species] = (speciesCount[fish.species] || 0) + 1;
        });
        this.speciesData = Object.keys(speciesCount).map(species => ({
          name: species,
          value: speciesCount[species]
        }));
        this.renderPieChart();
      } catch (error) {
        console.error('数据获取失败:', error);
      }
    },
    
    renderPieChart() {
      const chartDom = this.$refs.pieChart;
      const chart = echarts.init(chartDom);
      const option = {
        title: { text: '不同物种数量分布', left: 'center' },
        tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d}%)' },
        legend: { orient: 'vertical', left: 'left', data: this.speciesData.map(item => item.name) },
        series: [{
          name: '数量',
          type: 'pie',
          radius: '55%',
          data: this.speciesData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          selectedMode: 'single',
          selectedOffset: 10
        }]
      };

      chart.setOption(option);
      
      chart.on('click', params => {
        this.selectedSpecies = params.name;
        this.updateDetailCharts();
      });
    },
    
    async updateDetailCharts() {
      if (!this.selectedSpecies) return;
      
      const detailData = await this.processSpeciesData(this.selectedSpecies);
      this.renderRadarChart(detailData);
      this.renderBoxplotChart(detailData);
      this.renderScatterChart(detailData);
    },
    
    async processSpeciesData(species) {
      const filtered = this.fish_data_list.filter(fish => fish.species === species);
      
      const calcAvg = key => {
          const sum = filtered.reduce((acc, cur) => acc + cur[key], 0);
          return filtered.length ? (sum / filtered.length).toFixed(2) : 0;
      };
      
      // 提取各维度数据
      const extractData = key => filtered.map(fish => fish[key]).sort((a, b) => a - b);
      
      // 为散点图准备数据
      const scatterData = filtered.map(fish => [fish.length3, fish.weight, fish.fisher_id]);
      
      return {
        name: species,
        data: {
          avgWeight: calcAvg('weight'),
          avgLen1: calcAvg('length1'),
          avgLen2: calcAvg('length2'),
          avgLen3: calcAvg('length3'),
          avgHeight: calcAvg('height'),
          avgWidth: calcAvg('width')
        },
        maxValues: {
          weight: Math.max(...filtered.map(f => f.weight)) || 2000,
          length1: Math.max(...filtered.map(f => f.length1)) || 60,
          length2: Math.max(...filtered.map(f => f.length2)) || 65,
          length3: Math.max(...filtered.map(f => f.length3)) || 70,
          height: Math.max(...filtered.map(f => f.height)) || 20,
          width: Math.max(...filtered.map(f => f.width)) || 10
        },
        boxplotData: {
          length1: extractData('length1'),
          length2: extractData('length2'),
          length3: extractData('length3'),
          height: extractData('height'),
          width: extractData('width')
        },
        scatterData: scatterData
      };
    },
    
    renderRadarChart(detailData) {
      const radaroption = {
        title: {
          text: `${detailData.name} 形态特征雷达图`,
          left: 'center'
        },
        tooltip: {
          trigger: 'item'
        },
        radar: {
          indicator: [
            { name: '平均体重 (g)', max: detailData.maxValues.weight * 1.2 },
            { name: '平均长度1 (cm)', max: detailData.maxValues.length1 * 1.2 },
            { name: '平均长度2 (cm)', max: detailData.maxValues.length2 * 1.2 },
            { name: '平均长度3 (cm)', max: detailData.maxValues.length3 * 1.2 },
            { name: '平均高度 (cm)', max: detailData.maxValues.height * 1.2 },
            { name: '平均宽度 (cm)', max: detailData.maxValues.width * 1.2 }
          ],
          shape: 'polygon',
          splitNumber: 5,
          axisLine: {
            lineStyle: {
              color: 'rgba(100, 100, 100, 0.3)'
            }
          }
        },
        series: [{
          type: 'radar',
          data: [{
            value: [
              detailData.data.avgWeight,
              detailData.data.avgLen1,
              detailData.data.avgLen2,
              detailData.data.avgLen3,
              detailData.data.avgHeight,
              detailData.data.avgWidth
            ],
            name: detailData.name,
            areaStyle: {
              color: 'rgba(64, 158, 255, 0.4)'
            },
            lineStyle: {
              width: 2
            }
          }]
        }]
      };
      
      if (this.radarChart) this.radarChart.dispose();
      this.radarChart = echarts.init(this.$refs.radarChart);
      this.radarChart.setOption(radaroption);
    },
    
    renderBoxplotChart(detailData) {
      const calculateBoxplotData = (data) => {
        if (data.length === 0) return [0, 0, 0, 0, 0];
        
        const sorted = [...data].sort((a, b) => a - b);
        const len = sorted.length;
        
        const median = len % 2 === 0 ? 
          (sorted[len/2 - 1] + sorted[len/2]) / 2 : 
          sorted[Math.floor(len/2)];
        
        const q1Index = Math.floor(len / 4);
        const q3Index = Math.floor(len * 3 / 4);
        
        const q1 = len % 4 === 0 ? 
          (sorted[q1Index - 1] + sorted[q1Index]) / 2 : 
          sorted[q1Index];
          
        const q3 = len % 4 === 0 ? 
          (sorted[q3Index - 1] + sorted[q3Index]) / 2 : 
          sorted[q3Index];
        
        const iqr = q3 - q1;
        const lowerBound = q1 - 1.5 * iqr;
        const upperBound = q3 + 1.5 * iqr;
        
        const min = Math.max(sorted[0], lowerBound);
        const max = Math.min(sorted[len-1], upperBound);
        
        return [min, q1, median, q3, max];
      };
      
      const boxplotData = [
        calculateBoxplotData(detailData.boxplotData.length1),
        calculateBoxplotData(detailData.boxplotData.length2),
        calculateBoxplotData(detailData.boxplotData.length3),
        calculateBoxplotData(detailData.boxplotData.height),
        calculateBoxplotData(detailData.boxplotData.width)
      ];
      
      const prepareOutliers = (data, boxData) => {
        const [lower, q1, , q3, upper] = boxData;
        return data.filter(value => value < lower || value > upper)
                   .map(value => [value < lower ? -1 : 1, value]);
      };
      
      const outliers = [
        prepareOutliers(detailData.boxplotData.length1, boxplotData[0]),
        prepareOutliers(detailData.boxplotData.length2, boxplotData[1]),
        prepareOutliers(detailData.boxplotData.length3, boxplotData[2]),
        prepareOutliers(detailData.boxplotData.height, boxplotData[3]),
        prepareOutliers(detailData.boxplotData.width, boxplotData[4])
      ];
      
      const option = {
        title: {
          text: `${detailData.name} 体型分布箱线图`,
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['箱线图', '异常值'],
          left: 'center',
          bottom: 10
        },
        xAxis: {
          type: 'category',
          data: ['长度1(cm)', '长度2(cm)', '长度3(cm)', '高度(cm)', '宽度(cm)'],
          boundaryGap: true,
          axisLabel: {
            rotate: 45
          }
        },
        yAxis: {
          type: 'value',
          name: '数值',
          splitLine: {
            show: true
          }
        },
        series: [
          {
            name: '箱线图',
            type: 'boxplot',
            data: boxplotData,
            itemStyle: {
              color: '#3288bd'
            }
          },
          {
            name: '异常值',
            type: 'scatter',
            data: [
              ...outliers[0].map(v => ({name: '长度1(cm)', value: [0, v[1]]})),
              ...outliers[1].map(v => ({name: '长度2(cm)', value: [1, v[1]]})),
              ...outliers[2].map(v => ({name: '长度3(cm)', value: [2, v[1]]})),
              ...outliers[3].map(v => ({name: '高度(cm)', value: [3, v[1]]})),
              ...outliers[4].map(v => ({name: '宽度(cm)', value: [4, v[1]]}))
            ],
            symbolSize: 6,
            itemStyle: {
              color: '#d53e4f'
            }
          }
        ]
      };
      
      if (this.boxplotChart) this.boxplotChart.dispose();
      this.boxplotChart = echarts.init(this.$refs.boxplotChart);
      this.boxplotChart.setOption(option);
    },
    
    renderScatterChart(detailData) {
      // 计算回归直线
      const calculateRegressionLine = (data) => {
        const n = data.length;
        if (n < 2) return [];
        
        let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
        
        data.forEach(([x, y]) => {
          sumX += x;
          sumY += y;
          sumXY += x * y;
          sumX2 += x * x;
        });
        
        const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
        const intercept = (sumY - slope * sumX) / n;
        
        // 生成回归线上的点
        const minX = Math.min(...data.map(([x]) => x));
        const maxX = Math.max(...data.map(([x]) => x));
        const x1 = minX - 5;
        const x2 = maxX + 5;
        
        return [
          [x1, slope * x1 + intercept],
          [x2, slope * x2 + intercept]
        ];
      };
      
      const regressionLine = calculateRegressionLine(detailData.scatterData);
      
      const option = {
        title: {
          text: `${detailData.name} 体长3与重量关系散点图`,
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            const [length3, weight, id] = params.data;
            return `样本ID: ${id}<br/>体长3: ${length3}cm<br/>重量: ${weight}g`;
          }
        },
        legend: {
          data: ['样本数据', '回归趋势线'],
          left: 'center',
          bottom: 10
        },
        xAxis: {
          type: 'value',
          name: '体长3 (cm)',
          min: Math.min(...detailData.scatterData.map(([x]) => x)) - 5,
          max: Math.max(...detailData.scatterData.map(([x]) => x)) + 5,
          splitLine: {
            show: true
          }
        },
        yAxis: {
          type: 'value',
          name: '重量 (g)',
          min: Math.min(...detailData.scatterData.map(([, y]) => y)) - 100,
          max: Math.max(...detailData.scatterData.map(([, y]) => y)) + 100,
          splitLine: {
            show: true
          }
        },
        series: [
          {
            name: '样本数据',
            type: 'scatter',
            data: detailData.scatterData,
            symbolSize: 8,
            itemStyle: {
              color: '#3288bd',
              opacity: 0.8
            }
          },
          {
            name: '回归趋势线',
            type: 'line',
            data: regressionLine,
            lineStyle: {
              color: '#d53e4f',
              width: 2,
              type: 'dashed'
            },
            symbol: 'none'
          }
        ]
      };
      
      if (this.scatterChart) this.scatterChart.dispose();
      this.scatterChart = echarts.init(this.$refs.scatterChart);
      this.scatterChart.setOption(option);
    },
    
    resizeCharts() {
      if (this.radarChart) this.radarChart.resize();
      if (this.boxplotChart) this.boxplotChart.resize();
      if (this.scatterChart) this.scatterChart.resize();
    }
  }
}
</script>

<style scoped>
.figures-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  margin-top: 150px;

    /* 渐变背景 - 从浅蓝到深蓝 */
  background: linear-gradient(135deg,#38a5f8 0%, #8ccaf9 50%, #e6f7ff 100%);
  

}

.detail-charts {
  display: flex;
  flex-direction: column;
  gap:80px;
  align-self: center;
}
</style>