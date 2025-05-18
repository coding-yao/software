<template>
  <div class="weather-widget">
    <h2>当前天气 - {{ locationName }}</h2>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="weather-info">
      <div class="temperature">
        <span class="value">{{ currentWeather.temperature }}</span>
        <span class="unit">°C</span>
      </div>
      <div class="details">
        <div>天气状况: {{ weatherCodeToText(currentWeather.weathercode) }}</div>
        <div>风速: {{ currentWeather.windspeed }} km/h</div>
        <div>风向: {{ currentWeather.winddirection }}°</div>
        <div>更新时间: {{ formatTime(currentWeather.time) }}</div>
        <div v-if="currentWeather.is_day === 1">白天</div>
        <div v-else>夜晚</div>
      </div>
    </div>
    <div class="location-input">
      <input v-model="latitude" placeholder="纬度" type="number" step="0.0001" />
      <input v-model="longitude" placeholder="经度" type="number" step="0.0001" />
      <button @click="fetchWeather">更新天气</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'WeatherWidget',
  data() {
    return {
      loading: false,
      error: null,
      currentWeather: {},
      latitude: '39.9042',  // 默认北京
      longitude: '116.4074', // 默认北京
      locationName: '北京'
    };
  },
  created() {
    this.fetchWeather();
  },
  methods: {
    async fetchWeather() {
      this.loading = true;
      this.error = null;
      
      try {
        const params = {
          latitude: this.latitude || '39.9042',
          longitude: this.longitude || '116.4074'
        };
        
        const response = await axios.get('http://localhost:8000/api/smarthub/weather/', { params });
        console.log('完整API响应:', response);  // 调试用
        
        // 更健壮的响应验证
        if (!response.data) {
          throw new Error('API返回空响应');
        }
        
        const weatherData = response.data;
        
        // 检查是否存在current_weather字段
        if (!weatherData.current_weather) {
          console.warn('API响应缺少current_weather字段', weatherData);
          throw new Error('天气服务返回的数据结构异常');
        }
        
        // 检查必需字段
        const requiredFields = ['temperature', 'windspeed', 'weathercode'];
        const missingFields = requiredFields.filter(
          field => !(field in weatherData.current_weather)
        );
        
        if (missingFields.length > 0) {
          throw new Error(`缺少必需字段: ${missingFields.join(', ')}`);
        }
        
        // 数据有效，更新状态
        this.currentWeather = weatherData.current_weather;
        this.updateLocationName(params.latitude, params.longitude);
        
      } catch (err) {
        this.error = `获取天气失败: ${err.message}`;
        console.error('API请求错误详情:', {
          error: err,
          response: err.response?.data
        });
      } finally {
        this.loading = false;
      }
    },
    weatherCodeToText(code) {
      // 扩展天气代码描述
      const weatherCodes = {
        0: '晴朗',
        1: '大部分晴朗',
        2: '局部多云',
        3: '阴天',
        45: '雾',
        48: '冻雾',
        51: '细雨',
        53: '中雨',
        55: '密集细雨',
        56: '冻雨',
        57: '密集冻雨',
        61: '小雨',
        63: '中雨',
        65: '大雨',
        66: '冻雨',
        67: '密集冻雨',
        71: '小雪',
        73: '中雪',
        75: '大雪',
        77: '雪粒',
        80: '小雨',
        81: '中雨',
        82: '暴雨',
        85: '小雪',
        86: '大雪',
        95: '雷暴',
        96: '雷暴伴小雨',
        99: '雷暴伴大雨'
      };
      return weatherCodes[code] || `未知天气代码: ${code}`;
    },
    formatTime(isoTime) {
      return new Date(isoTime).toLocaleString();
    },
    async updateLocationName(lat, lng) {
      // 先检查常见城市缓存
      const commonCities = [
        { name: '北京', range: [39.4, 116.0, 40.2, 116.8] },
        { name: '上海', range: [30.9, 121.2, 31.5, 121.8] },
        { name: '广州', range: [22.7, 113.0, 23.4, 114.5] },
        { name: '深圳', range: [22.5, 113.7, 22.9, 114.5] },
        { name: '成都', range: [30.3, 102.5, 31.0, 104.2] },
        { name: '杭州', range: [29.8, 119.5, 30.4, 120.6] },
        { name: '重庆', range: [29.1, 105.9, 30.1, 107.1] },
        { name: '天津', range: [38.8, 116.8, 39.4, 117.7] },
        { name: '武汉', range: [30.3, 113.9, 30.9, 114.8] },
        { name: '西安', range: [34.1, 108.5, 34.5, 109.2] },
        { name: '南京', range: [31.8, 118.2, 32.3, 119.1] },
        { name: '沈阳', range: [41.4, 123.1, 42.0, 123.9] },
        { name: '大连', range: [38.7, 121.3, 39.2, 122.0] },
        { name: '青岛', range: [35.8, 120.1, 36.6, 120.8] },
        { name: '厦门', range: [24.3, 117.9, 24.8, 118.5] },
        { name: '长沙', range: [28.0, 112.6, 28.5, 113.3] }
        // 添加其他城市...
      ];
      
      const matchedCity = commonCities.find(city => 
        lat >= city.range[0] && lat <= city.range[2] &&
        lng >= city.range[1] && lng <= city.range[3]
      );
      
      if (matchedCity) {
        this.locationName = matchedCity.name;
        // 继续获取更精确的位置（不阻塞UI）
        this.fetchPreciseLocation(lat, lng);
      } else {
        // 非常见区域直接获取精确位置
        await this.fetchPreciseLocation(lat, lng);
      }
    },

    async fetchPreciseLocation(lat, lng) {
      try {
        // 使用Nominatim作为后备方案
        const nominatimResponse = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`,
          { headers: { 'User-Agent': 'YourAppName' } }
        );
        
        const data = await nominatimResponse.json();
        if (data.address) {
          const preciseName = [
            data.address.city || data.address.town,
            data.address.road
          ].filter(Boolean).join(' · ');
          
          if (preciseName) {
            this.locationName = preciseName;
          }
        }
      } catch (error) {
        console.error('获取精确位置失败:', error);
      }
    }
  }
};
</script>