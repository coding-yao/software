<template>
  <NavBar current-page="main" />
  <div class="main-content">
    <div class="dashboard-row">
      <div class="dashboard-panel">
        <div class="panel-header">
          <h3>数据统计</h3>
        </div>
        <div class="panel-content">
          <div class="status-item">
            <span class="label">今日数据量：</span>
            <span class="value">1,440条</span>
          </div>
          <div class="status-item">
            <span class="label">本周数据量：</span>
            <span class="value">10,080条</span>
          </div>
          <div class="status-item">
            <span class="label">本月数据量：</span>
            <span class="value">43,200条</span>
          </div>
          <div class="status-item">
            <span class="label">数据完整率：</span>
            <span class="value">99.8%</span>
          </div>
        </div>
      </div>

      <div class="dashboard-panel">
        <div class="panel-header">
          <h3>水文气象</h3>
        </div>
        <div class="panel-content">
          <div class="status-item">
            <span class="label">电池电压 (V)</span>
            <div class="progress-bar">
              <div class="progress" :style="{ width: hydroMeteorological.voltage + '%' }"></div>
            </div>
            <span class="value">{{ hydroMeteorological.voltage }}</span>
          </div>
          <div class="status-item">
            <span class="label">盐度 (‰)</span>
            <div class="progress-bar">
              <div class="progress" :style="{ width: hydroMeteorological.salinity + '%' }"></div>
            </div>
            <span class="value">{{ hydroMeteorological.salinity }}</span>
          </div>
          <div class="status-item">
            <span class="label">溶解氧 (mg/L)</span>
            <div class="progress-bar">
              <div class="progress" :style="{ width: hydroMeteorological.dissolved_oxygen + '%' }"></div>
            </div>
            <span class="value">{{ hydroMeteorological.dissolved_oxygen }}</span>
          </div>
          <div class="status-item">
            <span class="label">浊度 (NTU)</span>
            <div class="progress-bar">
              <div class="progress" :style="{ width: hydroMeteorological.turbidity + '%' }"></div>
            </div>
            <span class="value">{{ hydroMeteorological.turbidity }}</span>
          </div>
          <div class="status-item">
            <span class="label">pH值</span>
            <div class="progress-bar">
              <div class="progress" :style="{ width: hydroMeteorological.ph + '%' }"></div>
            </div>
            <span class="value">{{ hydroMeteorological.ph }}</span>
          </div>
          <div class="status-item">
            <span class="label">温度 (℃)</span>
            <div class="progress-bar">
              <div class="progress" :style="{ width: hydroMeteorological.temperature + '%' }"></div>
            </div>
            <span class="value">{{ hydroMeteorological.temperature }}</span>
          </div>
        </div>
      </div>

      <div class="dashboard-panel">
        <div class="panel-header">
          <h3>设备状态</h3>
          <div class="tab-nav">
            <div 
              v-for="tab in tabs" 
              :key="tab.name"
              :class="['tab-item', { active: activeTab === tab.name }]"
              @click="activeTab = tab.name"
            >
              {{ tab.label }}
            </div>
          </div>
        </div>
        <div class="panel-content">
          <div v-show="activeTab === 'main'" class="tab-content">
            <div class="status-item">
              <span class="label">设备ID：</span>
              <span class="value">{{ deviceStatus.device_id }}</span>
            </div>
            <div class="status-item">
              <span class="label">主控状态：</span>
              <span class="value">
                版本：{{ deviceStatus.main_control.version }}
                <br>
                温度：{{ deviceStatus.main_control.temperature }}℃
              </span>
            </div>
            <div class="status-item">
              <span class="label">次控状态：</span>
              <span class="value" :class="{ 'disconnected': deviceStatus.secondary_control.connection_status === '断开' }">
                {{ deviceStatus.secondary_control.connection_status }}
              </span>
            </div>
          </div>
          <div v-show="activeTab === 'calibration'" class="tab-content">
            <div class="status-item">
              <span class="label">最后校准时间：</span>
              <span class="value">{{ deviceStatus.last_calibration }}</span>
            </div>
            <div class="status-item">
              <span class="label">校准状态：</span>
              <span class="value" :class="{ 'warning': isCalibrationExpired }">
                {{ calibrationStatus }}
              </span>
            </div>
            <div class="status-item">
              <span class="label">下次校准时间：</span>
              <span class="value">{{ nextCalibrationTime }}</span>
            </div>
            <div class="status-item">
              <span class="label">校准周期：</span>
              <span class="value">30天</span>
            </div>
          </div>
          <div v-show="activeTab === 'channel'" class="tab-content">
            <div class="channel-grid">
              <div class="channel-item" v-for="channel in channels" :key="channel.id">
                <div class="channel-header">
                  <span class="channel-name">{{ channel.name }}</span>
                  <span class="channel-status" :class="channel.status">{{ channel.statusText }}</span>
                </div>
                <div class="channel-info">
                  <div class="info-item">
                    <span class="label">采样率：</span>
                    <span class="value">{{ channel.samplingRate }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">数据量：</span>
                    <span class="value">{{ channel.dataCount }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-show="activeTab === 'alarm'" class="tab-content">
            <div class="alarm-list">
              <div class="alarm-item" v-for="alarm in alarms" :key="alarm.id" :class="alarm.level">
                <div class="alarm-header">
                  <span class="alarm-time">{{ alarm.time }}</span>
                  <span class="alarm-level">{{ alarm.levelText }}</span>
                </div>
                <div class="alarm-content">
                  <div class="alarm-title">{{ alarm.title }}</div>
                  <div class="alarm-desc">{{ alarm.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="data-panel">
      <h3 class="panel-title">水质历史数据</h3>
      <div class="control-panel">
        <div class="search-row">
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
      </div>
      
      <div v-if="showNoDataMessage" class="no-data-message">
        未找到符合条件的数据，请尝试其他查询条件
      </div>
      
      <div class="chart-container" ref="chartContainer"></div>
    </div>
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
      showNoDataMessage: false,
      activeTab: 'main',
      deviceStatus: {
        device_id: '',
        main_control: {
          version: '',
          temperature: 0
        },
        secondary_control: {
          connection_status: ''
        },
        last_calibration: ''
      },
      tabs: [
        { name: 'main', label: '主控' },
        { name: 'calibration', label: '时间校准' },
        { name: 'channel', label: '通道' },
        { name: 'alarm', label: '告警' }
      ],
      channels: [
        {
          id: 1,
          name: '通道1',
          status: 'normal',
          statusText: '正常',
          samplingRate: '1次/分钟',
          dataCount: '1,440条/天'
        },
        {
          id: 2,
          name: '通道2',
          status: 'warning',
          statusText: '警告',
          samplingRate: '1次/分钟',
          dataCount: '1,440条/天'
        },
        {
          id: 3,
          name: '通道3',
          status: 'error',
          statusText: '异常',
          samplingRate: '1次/分钟',
          dataCount: '1,440条/天'
        },
        {
          id: 4,
          name: '通道4',
          status: 'normal',
          statusText: '正常',
          samplingRate: '1次/分钟',
          dataCount: '1,440条/天'
        }
      ],
      alarms: [
        {
          id: 1,
          time: '2024-03-20 15:30:00',
          level: 'error',
          levelText: '严重',
          title: '通道3数据异常',
          description: '通道3连续10分钟未收到数据，请检查设备连接'
        },
        {
          id: 2,
          time: '2024-03-20 14:20:00',
          level: 'warning',
          levelText: '警告',
          title: '通道2采样率降低',
          description: '通道2采样率低于正常值，可能影响数据准确性'
        },
        {
          id: 3,
          time: '2024-03-20 10:00:00',
          level: 'info',
          levelText: '提示',
          title: '设备校准提醒',
          description: '设备距离上次校准已超过25天，建议及时校准'
        }
      ],
      hydroMeteorological: {
        voltage: 25.9,
        salinity: 34.16,
        dissolved_oxygen: 0.0,
        turbidity: 2.05,
        ph: 8.37,
        temperature: 15.0,
      },
    }
  },
  computed: {
    canSearch() {
      return this.selectedProvince && 
             this.selectedBasin && 
             this.selectedStation && 
             this.startDate && 
             this.endDate
    },
    isCalibrationExpired() {
      const lastCalibration = new Date(this.deviceStatus.last_calibration)
      const now = new Date()
      const daysDiff = Math.floor((now - lastCalibration) / (1000 * 60 * 60 * 24))
      return daysDiff > 25
    },
    calibrationStatus() {
      return this.isCalibrationExpired ? '需要校准' : '正常'
    },
    nextCalibrationTime() {
      const lastCalibration = new Date(this.deviceStatus.last_calibration)
      const nextCalibration = new Date(lastCalibration)
      nextCalibration.setDate(nextCalibration.getDate() + 30)
      return nextCalibration.toLocaleString()
    },
    normalizeValue(value, min, max) {
      const clamped = Math.max(min, Math.min(max, value));
      return ((clamped - min) / (max - min)) * 100;
    },
  },
  mounted() {
    // 设置默认日期范围
    this.startDate = '2020-05-10'
    this.endDate = '2020-05-17'
    
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

    // 获取设备状态
    this.fetchDeviceStatus()
    this.fetchHydroMeteorological()
  },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$refs.chartContainer)
      const option = {
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
    },

    async fetchDeviceStatus() {
      try {
        const response = await axios.get('http://localhost:8000/api/main_info/device_status')
        if (response.data.status === 200) {
          this.deviceStatus = response.data.data
        }
      } catch (error) {
        console.error('获取设备状态失败:', error)
      }
    },

    async fetchHydroMeteorological() {
      try {
        const response = await axios.get('http://localhost:8000/api/main_info/hydro_meteorological')
        if (response.data.status === 200) {
          this.hydroMeteorological = response.data.data
        }
      } catch (error) {
        console.error('获取水文气象数据失败:', error)
      }
    }
  }
}
</script>

<style scoped>
.main-content {
  margin-top: 80px;
  padding: 20px;
}

.dashboard-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.dashboard-panel {
  flex: 1;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  height: 450px;
  display: flex;
  flex-direction: column;
}

.control-panel {
  margin-bottom: 20px;
  padding: 0;
  background: none;
  box-shadow: none;
}

.search-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.select-group {
  display: flex;
  gap: 20px;
  flex: 1;
  align-items: center;
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
  margin-bottom: 20px;
}

.date-group input[type="date"] {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.button-group {
  display: flex;
  justify-content: flex-end;
  flex: 0 0 150px;
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
  height: 600px;
  background: none;
  box-shadow: none;
  padding: 0;
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

.panel-header {
  margin-bottom: 10px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  flex-shrink: 0;
}

.panel-header h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
}

.tab-nav {
  display: flex;
  gap: 20px;
  border-bottom: 1px solid #eee;
}

.tab-item {
  padding: 8px 16px;
  cursor: pointer;
  color: #666;
  position: relative;
  transition: all 0.3s;
}

.tab-item:hover {
  color: #1890ff;
}

.tab-item.active {
  color: #1890ff;
  font-weight: bold;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #1890ff;
}

.panel-content {
  flex: 1;
  position: relative;
}

.tab-content {
  padding: 10px 0;
  height: 100%;
}

.status-item {
  margin: 15px 0;
  display: flex;
  align-items: center;
}

.status-item .label {
  font-weight: bold;
  min-width: 100px;
  color: #666;
}

.status-item .value {
  color: #333;
}

.status-item .value.disconnected {
  color: #f56c6c;
}

.channel-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  padding: 10px 0;
}

.channel-item {
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 12px;
}

.channel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.channel-name {
  font-weight: bold;
  color: #333;
}

.channel-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.channel-status.normal {
  background-color: #e6f7ff;
  color: #1890ff;
}

.channel-status.warning {
  background-color: #fff7e6;
  color: #fa8c16;
}

.channel-status.error {
  background-color: #fff1f0;
  color: #f5222d;
}

.channel-info {
  font-size: 13px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
}

.alarm-list {
  padding: 10px 0;
}

.alarm-item {
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 10px;
}

.alarm-item.error {
  border-left: 4px solid #f5222d;
}

.alarm-item.warning {
  border-left: 4px solid #fa8c16;
}

.alarm-item.info {
  border-left: 4px solid #1890ff;
}

.alarm-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.alarm-time {
  color: #666;
  font-size: 13px;
}

.alarm-level {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.alarm-item.error .alarm-level {
  background-color: #fff1f0;
  color: #f5222d;
}

.alarm-item.warning .alarm-level {
  background-color: #fff7e6;
  color: #fa8c16;
}

.alarm-item.info .alarm-level {
  background-color: #e6f7ff;
  color: #1890ff;
}

.alarm-title {
  font-weight: bold;
  margin-bottom: 4px;
}

.alarm-desc {
  color: #666;
  font-size: 13px;
}

.warning {
  color: #fa8c16;
}

.data-panel {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.panel-title {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  font-weight: bold;
}

.progress-bar {
  width: 250px;
  height: 10px;
  background-color: #e9ecef;
  border-radius: 5px;
  overflow: hidden;
  margin-left: 15px; 
  margin-right: 10px;
}

.progress {
  height: 100%;
  background-color: #1890ff;
  transition: width 0.3s ease;
}
</style>