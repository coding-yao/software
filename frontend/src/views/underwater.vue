<template>
  <NavBar current-page="underwater" />

  <div class="figures-container">

    <!--阈值调整输入框容器-->
    <div  v-if="isModalOpen"  class="modal-overlay">
      <div class="modal-content">
          <!-- 输入框1 -->
          <div class="input-group">
              <input type="number" placeholder="设置最小长度阈值(cm)" step="0.1" ref="lowestlength">
          </div>
          <!-- 输入框2 -->
          <div class="input-group">
              <input type="number" placeholder="设置最大长度阈值(cm)" step="0.1"ref="highestlength">
          </div>
          <!-- 选择框 -->
          <div class="input-group">
              <input type="number" placeholder="重量偏离平均阈值(标准差)" step="1" ref="weight_deviation">
          </div>
          <div class="input-group">
              <input type="number" placeholder="设置死亡率阈值(%)"  step="0.1" ref="death_ratio">
          </div>

          <button @click="notdisplay()">取消</button>
          <button @click="updatethreshold()">提交</button>
      </div>
    </div>

    <div style="width: 50%;">
      <!--饼图容器-->
      <div ref="pieChart" style="height: 500px; position: relative;">
      </div>
      <!--下载按钮-->
      <button class="ok" @click="downloadChart('pie')">下载饼图</button>
      <button v-if="selectedSpecies" class="ok" @click="downloadChart('radar')">下载雷达图</button>
      <button v-if="selectedSpecies" class="ok" @click="downloadChart('boxplot')">下载箱线图</button>
      <button v-if="selectedSpecies" class="ok" @click="downloadChart('scatter')">下载散点图</button>

      <button class="ok" @click="exportAllData">下载原始数据</button>
      <!--上传文件部分-->
      <div class="upload-section">
        <input type="file" accept=".csv" @change="handleFileChange">
        <p>上传数据文件(.csv)</p>
        <p v-if="uploadMessage" >
              {{ uploadMessage }}
        </p>
        <button v-if="csvFile" class="ok" @click="uploadCsv">点击上传</button>
      </div>
      <button style="margin: 5%;" class="ok" @click="displaythresholds()">修改报警信息阈值</button>

      <div class="fish_alert_table">
        <table>
          <thead>
          <tr>
              <th>警告序号</th>
              <th>警告类型</th>
              <th>该鱼种类</th>
              <th>具体信息</th>
              <th>警告级别</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="(al, index) in alert_list" :key="index" class="user-row">
              <td>{{ index+1 }}</td>
              <td>{{ al.alert_type }}</td>
              <td>{{ al.fish_species }}</td>
              <td>{{ al.message }}</td>
              <td>{{ al.severity }}</td>
          </tr>
          </tbody>

        </table>

      </div>
    </div>


    <div v-if="selectedSpecies" class="detail-charts" style="width: 50%;">
      <div ref="radarChart" style="height: 500px;"></div>
      <div ref="boxplotChart" style="height: 500px;"></div>
      <div ref="scatterChart" style="height: 500px;"></div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import Papa from 'papaparse';
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
      scatterChart: null,

      csvFile: null,
      previewData: [],
      headers: [],
      uploadMessage: '',

      alert_list:[],
      isModalOpen:false,
    };
  },
  mounted() {
    this.fetchData();
    window.addEventListener('resize', this.resizeCharts);

    this.checkfishalert();
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
        // console.log(this.fish_data_list)
        
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
    /*以下与阈值设置和警告等相关 */
    async checkfishalert() {
      const accessToken = localStorage.getItem('accesstoken');
      try {
        const response = await axios.get(
          'http://localhost:8000/api/core/check_alert/',
          { headers: { 'Authorization': `Bearer ${accessToken}` } }
        );
        this.alert_list = response.data;
        console.log(this.alert_list);

      }catch (error) {
        console.error('警告信息获取失败:', error);
      }
    },

    displaythresholds(){
      this.isModalOpen = true;
    },
    notdisplay(){
      this.isModalOpen = false;
    },
    updatethreshold(){
      const lowestlength = parseFloat(this.$refs['lowestlength'].value); 
      const highestlength = parseFloat(this.$refs['highestlength'].value);
      const weight_deviation = parseFloat(this.$refs['weight_deviation'].value);
      const death_ratio = parseFloat(this.$refs['death_ratio'].value)/100;

      // death_ratio = death_ratio/100;
      
      const accessToken = localStorage.getItem('accesstoken');
      const new_thresholddata = { // 构建要发送到后端的数据信息
        weight_deviation_multiplier: weight_deviation,
        length_min: lowestlength,
        length_max: highestlength,
        daily_mortality_rate_threshold: death_ratio,
      };
      console.log(new_thresholddata);
      axios
      .post(
          `http://localhost:8000/api/user/update_thresholds/`, 
          new_thresholddata,
          {
              headers: {
              'Authorization': `Bearer ${accessToken}`,
              }
          }
      )
      .then((response) => {   // 接收后端发来的response 或error
          console.log(response);
          alert('修改成功');
          this.isModalOpen = false;
      })
    },
    /* 以下画图函数 */
    renderPieChart() {
      const chartDom = this.$refs.pieChart;
      const chart = echarts.init(chartDom);
      const option = {
        title: { text: '不同物种数量分布', subtext: '点击具体物种查看详情', left: 'center' },
        tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d}%)' },
        legend: { orient: 'vertical', left: 'left', data: this.speciesData.map(item => item.name) },
        grid: {
          left: '15%'
        },
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
          bottom: 5
        },
        xAxis: {
          type: 'category',
          data: ['长度1(cm)', '长度2(cm)', '长度3(cm)', '高度(cm)', '宽度(cm)'],
          boundaryGap: true,
          axisLabel: {
            rotate: 0
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
        grid: {
          right: '15%'
        },
        xAxis: {
          type: 'value',
          name: '体长3 (cm)',
          min: Math.min(...detailData.scatterData.map(([x]) => x)) - 5,
          max: Math.max(...detailData.scatterData.map(([x]) => x)) + 5,
          splitLine: {
            show: true
          },
          axisLabel: {
            formatter: function(value) {
              return value.toFixed(2); // 保留2位小数
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '重量 (g)',
          min: Math.max(Math.min(...detailData.scatterData.map(([, y]) => y)) - 100, 0),
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
    },
    // 以下解析CSV文件
    handleFileChange(event) {
      const file = event.target.files[0];
      if (!file || !file.name.endsWith('.csv')) {
        alert("请选择有效的csv文件")
        this.uploadMessage = `CSV解析错误`;
        return;
      }
      
      this.csvFile = file;
      this.parseCsv(file);
    },
    parseCsv(file) {
      this.uploadMessage = '';
      Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        dynamicTyping: true,
        complete: (results) => {
          if (results.errors.length) {
            this.uploadMessage = `CSV解析错误: ${results.errors[0].message}`;
            return;
          }
          
          if (!results.data.length) {
            this.uploadMessage = 'CSV文件为空或格式不正确';
            return;
          }
          
          // 验证必需字段
          const requiredFields = ['Species', 'Weight(g)', 'Length1(cm)', 
                                 'Length2(cm)', 'Length3(cm)', 'Height(cm)', 'Width(cm)'];
          const firstRow = results.data[0];
          const missingFields = requiredFields.filter(field => !(field in firstRow));
          
          if (missingFields.length) {
            this.uploadMessage = `缺少必需字段: ${missingFields.join(', ')}`;
            return;
          }
          
          this.headers = Object.keys(firstRow);
          this.previewData = results.data;
          this.uploadMessage = `成功解析 ${results.data.length} 条记录`;
        },
        error: (error) => {
          this.uploadMessage = `CSV解析失败: ${error.message}`;
        }
      });
    },
    // 发送文件到后端
    async uploadCsv() {
      if (!this.csvFile || !this.previewData.length) {
        this.uploadMessage = '请先选择有效的CSV文件';
        return;
      }
      this.uploadMessage = '正在上传数据...';
      
      try {
        const accessToken = localStorage.getItem('accesstoken');
        const formData = new FormData();
        formData.append('file', this.csvFile);
        
        const response = await axios.post(
          'http://localhost:8000/api/fish/upload_fish_csv/',
          formData,
          {
            headers: {
              'Authorization': `Bearer ${accessToken}`,
              // 'Content-Type': 'multipart/form-data'
            }
          }
        );
        
        this.uploadMessage = response.data.message;
        
        // 重置状态
        setTimeout(() => {
          this.csvFile = null;
          this.previewData = [];
          this.uploadMessage = '';
          document.querySelector('input[type="file"]').value = '';
        }, 3000);
        
      } catch (error) {
        console.log(error.response.data.error);
        const message = error.response?.data?.detail || '上传失败，请重试';
        this.uploadMessage = `错误: ${message}`;
      } finally{
        this.fetchData();
      }
    },
    //下载图表
    downloadChart(chartType) {
      let chartInstance = null;
      let fileName = '';
      
      switch (chartType) {
        case 'pie':
          chartInstance = this.pieChart;
          fileName = '物种分布饼图';
          break;
        case 'radar':
          chartInstance = this.radarChart;
          fileName = `${this.selectedSpecies}_形态特征雷达图`;
          break;
        case 'boxplot':
          chartInstance = this.boxplotChart;
          fileName = `${this.selectedSpecies}_体型分布箱线图`;
          break;
        case 'scatter':
          chartInstance = this.scatterChart;
          fileName = `${this.selectedSpecies}_体长3与重量关系散点图`;
          break;
        default:
          return;
      }
      
      if (!chartInstance) {
        console.error('图表实例不存在');
        return;
      }
      
      try {
        const dataURL = chartInstance.getDataURL({
          type: 'png',
          pixelRatio: 2, // 提高图片清晰度
          backgroundColor: '#fff'
        });
        
        const link = document.createElement('a');
        link.href = dataURL;
        link.download = `${fileName}_${new Date().toISOString().slice(0, 10)}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } catch (error) {
        console.error('图表导出失败:', error);
        alert('图表导出失败，请重试');
      }
    },
    //导出当前原始数据为CSV
    exportAllData() {
      if (this.fish_data_list.length === 0) {
        alert('没有可导出的数据');
        return;
      }
      
      this.exportToCSV(this.fish_data_list, '全部鱼类数据');
    },
    exportToCSV(data, fileName) {
      try {
        // 创建CSV内容
        const csv = Papa.unparse({
          fields: Object.keys(data[0]),
          data: data
        });
        
        // 创建Blob对象
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        
        // 创建下载链接
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', `${fileName}_${new Date().toISOString().slice(0, 10)}.csv`);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } catch (error) {
        console.error('CSV导出失败:', error);
        alert('数据导出失败，请重试');
      }
    },
  }
}
</script>

<style scoped>
.figures-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  margin-top: 5%;
  /* background: white; */
  margin-left: 20px;
  margin-right: 20px;

}

.detail-charts {
  display: flex;
  flex-direction: column;
  gap:80px;
  align-self: center;
}

/*上传区域*/
.upload-section {
  margin-top: 20px;
  text-align: center;
  padding: 15px;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  background-color: #f5f7fa;
  transition: border-color 0.3s;
}
/* 输入框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5); /* 半透明黑色背景 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}
.modal-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 400px;
}
.input-group {
  margin-bottom: 16px;
}

/**表格样式 */
.user-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

th {
  background-color: #f1f5f9;
  font-weight: 600;
}


</style>