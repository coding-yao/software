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
      if (!isoTime) return '未知';
      const date = new Date(isoTime);
      date.setUTCMinutes(date.getUTCMinutes() + 480); // GMT + 8小时
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },
    async updateLocationName(lat, lng) {
      const coastalCities = [
        { name: '北京', range: [39.4, 116.0, 40.2, 116.8] },
        { name: '大连', range: [38.7, 121.3, 39.2, 122.0] },
        { name: '青岛', range: [35.8, 120.1, 36.6, 120.8] },
        { name: '上海', range: [30.9, 121.2, 31.5, 121.8] },
        { name: '宁波', range: [29.5, 121.3, 30.1, 122.2] },
        { name: '舟山', range: [29.3, 121.5, 30.5, 123.5] },
        { name: '厦门', range: [24.3, 117.9, 24.8, 118.5] },
        { name: '广州', range: [22.7, 113.0, 23.4, 114.5] },
        { name: '深圳', range: [22.5, 113.7, 22.9, 114.5] },
        { name: '珠海', range: [21.8, 113.1, 22.4, 113.8] },
        { name: '海口', range: [19.9, 110.1, 20.2, 110.7] },
        { name: '三亚', range: [18.1, 108.9, 18.5, 109.7] },
        { name: '烟台', range: [37.3, 121.0, 37.8, 121.8] },
        { name: '威海', range: [37.0, 121.8, 37.6, 122.5] },
        { name: '日照', range: [35.2, 119.1, 35.6, 119.8] },
        { name: '福州', range: [25.8, 119.1, 26.2, 119.6] },
        { name: '泉州', range: [24.6, 118.3, 25.3, 119.0] },
        { name: '湛江', range: [20.8, 110.0, 21.5, 110.8] },
        { name: '北海', range: [21.2, 108.8, 21.8, 109.5] }
      ];
      
      // 尝试匹配沿海城市
      const matchedCity = coastalCities.find(city => 
        lat >= city.range[0] && lat <= city.range[2] &&
        lng >= city.range[1] && lng <= city.range[3]
      );
      
      // 如果匹配到沿海城市则显示城市名，否则显示经纬度
      this.locationName = matchedCity ? matchedCity.name : `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
    }
  }
};
</script>