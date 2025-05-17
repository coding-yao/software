<template>
  <NavBar current-page="main" />
  <div class="main-content">
    <div class="control-panel">
      <div class="select-group">
        <select v-model="selectedProvince" @change="handleProvinceChange">
          <option value="">请选择省份</option>
          <option v-for="province in provinces" :key="province" :value="province">
            {{ province }}
          </option>
        </select>
        
        <select v-model="selectedBasin" @change="handleBasinChange" :disabled="!selectedProvince">
          <option value="">请选择流域</option>
          <option v-for="basin in basins" :key="basin" :value="basin">
            {{ basin }}
          </option>
        </select>
        
        <select v-model="selectedStation" @change="handleStationChange" :disabled="!selectedBasin">
          <option value="">请选择断面</option>
          <option v-for="station in stations" :key="station" :value="station">
            {{ station }}
          </option>
        </select>
      </div>
      
      <div class="date-group">
        <input type="date" v-model="startDate" :max="endDate">
        <span>至</span>
        <input type="date" v-model="endDate" :min="startDate">
      </div>
      
      <div class="button-group">
        <button class="search-btn" @click="fetchData" :disabled="!canSearch">
          检索数据
        </button>
      </div>
    </div>
    
    <div v-if="showNoDataMessage" class="no-data-message">
      未找到符合条件的数据，请尝试其他查询条件
    </div>
    
    <div class="chart-container" ref="chartContainer"></div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import * as echarts from 'echarts'
import axios from 'axios'

export default {
  components: {
    NavBar
  },
  data() {
    return {
      selectedProvince: '',
      selectedBasin: '',
      selectedStation: '',
      provinces: [],
      basins: [],
      stations: [],
      startDate: '',
      endDate: '',
      chart: null,
      showNoDataMessage: false
    }
  },
  computed: {
    canSearch() {
      return this.selectedProvince && 
             this.selectedBasin && 
             this.selectedStation && 
             this.startDate && 
             this.endDate
    }
  },
  mounted() {
    // 设置默认日期范围
    this.startDate = '2020-05-10'
    this.endDate = '2020-12-17'
    
    // 设置默认检索条件
    this.selectedProvince = '北京'
    
    // 初始化图表
    this.initChart()
    
    // 获取省份列表并自动获取默认流域和断面数据
    this.fetchProvinces().then(() => {
      this.handleProvinceChange().then(() => {
        this.selectedBasin = '海河流域'
        this.handleBasinChange().then(() => {
          this.selectedStation = '古北口'
          this.fetchData()
        })
      })
    })
  },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$refs.chartContainer)
      const option = {
        title: {
          text: '水质历史数据',
          left: 'center'
        },
        tooltip: {
          show: false
        },
        legend: {
          data: ['水温', 'pH值', '溶解氧'],
          top: 30
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: []
        },
        yAxis: [
          {
            type: 'value',
            name: '水温(℃)',
            position: 'left'
          },
          {
            type: 'value',
            name: 'pH值',
            position: 'right'
          },
          {
            type: 'value',
            name: '溶解氧(mg/L)',
            position: 'right',
            offset: 80
          }
        ],
        series: [
          {
            name: '水温',
            type: 'line',
            data: [],
            yAxisIndex: 0
          },
          {
            name: 'pH值',
            type: 'line',
            data: [],
            yAxisIndex: 1
          },
          {
            name: '溶解氧',
            type: 'line',
            data: [],
            yAxisIndex: 2
          }
        ]
      }
      this.chart.setOption(option)
    },
    
    async fetchProvinces() {
      try {
        const response = await axios.get('http://localhost:8000/api/main_info/get_provinces')
        this.provinces = response.data.data
      } catch (error) {
        console.error('获取省份列表失败:', error)
      }
    },
    
    async handleProvinceChange() {
      if (this.selectedProvince) {
        try {
          const response = await axios.get(`http://localhost:8000/api/main_info/get_basins?province=${this.selectedProvince}`)
          this.basins = response.data.data
          this.selectedBasin = ''
          this.selectedStation = ''
          this.stations = []
        } catch (error) {
          console.error('获取流域列表失败:', error)
        }
      }
    },
    
    async handleBasinChange() {
      if (this.selectedBasin) {
        try {
          const response = await axios.get(`http://localhost:8000/api/main_info/get_stations?province=${this.selectedProvince}&basin=${this.selectedBasin}`)
          this.stations = response.data.data
          this.selectedStation = ''
        } catch (error) {
          console.error('获取断面列表失败:', error)
        }
      }
    },
    
    async handleStationChange() {
      if (this.selectedStation) {
        // 可以在这里添加其他逻辑
      }
    },
    
    async fetchData() {
      if (!this.canSearch) return
      
      try {
        const response = await axios.get('http://localhost:8000/api/main_info/historical_data', {
          params: {
            province: this.selectedProvince,
            basin: this.selectedBasin,
            station: this.selectedStation,
            start_date: this.startDate,
            end_date: this.endDate
          }
        })
        
        const data = response.data.data
        if (data.dates.length === 0) {
          this.showNoDataMessage = true
          this.chart.setOption({
            xAxis: { data: [] },
            series: [
              { data: [] },
              { data: [] },
              { data: [] }
            ]
          })
        } else {
          this.showNoDataMessage = false
          this.updateChart(data)
        }
      } catch (error) {
        console.error('获取历史数据失败:', error)
        this.showNoDataMessage = true
      }
    },
    
    updateChart(data) {
      if (!this.chart) return
        
      this.chart.setOption({
        xAxis: {
          data: data.dates
        },
        series: [
          {
            name: '水温',
            data: data.water_temperature
          },
          {
            name: 'pH值',
            data: data.ph
          },
          {
            name: '溶解氧',
            data: data.dissolved_oxygen
          }
        ]
      })
    }
  }
}
</script>

<style scoped>
.main-content {
  margin-top: 80px;
  padding: 20px;
}

.control-panel {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.select-group {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.select-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 150px;
}

.date-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date-group input[type="date"] {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.button-group {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.search-btn {
  padding: 10px 30px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.search-btn:hover {
  background-color: #40a9ff;
}

.search-btn:disabled {
  background-color: #d9d9d9;
  cursor: not-allowed;
}

.chart-container {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  height: 600px;
}

.no-data-message {
  background-color: #fff3cd;
  color: #856404;
  padding: 15px;
  border-radius: 4px;
  margin: 20px 0;
  text-align: center;
  font-size: 16px;
  border: 1px solid #ffeeba;
}
</style>