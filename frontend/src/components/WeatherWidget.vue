<template>
  <div class="weather-widget" :class="{'night-mode': currentWeather.is_day !== 1}">
    <div class="widget-header">
      <h2 class="location-title">
        <i class="fas fa-map-marker-alt"></i>
        {{ locationName }}
        <span class="last-updated" v-if="!loading && !error">
          更新时间: {{ formatTime(currentWeather.time) }}
        </span>
      </h2>
    </div>

    <div v-if="loading" class="loading-state">
      <i class="fas fa-spinner fa-pulse fa-3x"></i>
      <p>正在获取天气数据...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
      <button class="retry-btn" @click="fetchWeather">重试</button>
    </div>

    <div v-else class="weather-display">
      <div class="main-weather">
        <div class="temperature-display">
          <span class="value">{{ Math.round(currentWeather.temperature) }}</span>
          <span class="unit">°C</span>
        </div>
        <div class="weather-icon">
          <i :class="getWeatherIcon(currentWeather.weathercode, currentWeather.is_day)"></i>
          <div class="weather-condition">
            {{ weatherCodeToText(currentWeather.weathercode) }}
          </div>
        </div>
      </div>

      <div class="weather-details">
        <div class="detail-item">
          <i class="fas fa-wind"></i>
          <div>
            <div class="detail-label">风速</div>
            <div class="detail-value">{{ currentWeather.windspeed }} km/h</div>
          </div>
        </div>
        <div class="detail-item">
          <i class="fas fa-compass"></i>
          <div>
            <div class="detail-label">风向</div>
            <div class="detail-value">{{ getWindDirection(currentWeather.winddirection) }}</div>
          </div>
        </div>
        <div class="detail-item">
          <i :class="currentWeather.is_day === 1 ? 'fas fa-sun' : 'fas fa-moon'"></i>
          <div>
            <div class="detail-label">昼夜</div>
            <div class="detail-value">{{ currentWeather.is_day === 1 ? '白天' : '夜晚' }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入框区域固定在底部 -->
    <div class="location-controls">
      <div class="coord-inputs" @keyup.enter="fetchWeather">
        <div class="input-group">
          <label for="latitude">纬度</label>
          <input 
            id="latitude" 
            v-model="latitude" 
            type="number" 
            step="0.0001"
            placeholder="例如: 39.9042"
          />
        </div>
        <div class="input-group">
          <label for="longitude">经度</label>
          <input 
            id="longitude" 
            v-model="longitude" 
            type="number" 
            step="0.0001"
            placeholder="例如: 116.4074"
          />
        </div>
      </div>
      <button class="refresh-btn" @click="fetchWeather" :disabled="loading">
        <i class="fas" :class="loading ? 'fa-spinner fa-pulse' : 'fa-sync-alt'"></i>
        {{ loading ? '加载中...' : '更新天气' }}
      </button>
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
        
        if (!response.data) {
          throw new Error('API返回空响应');
        }
        
        const weatherData = response.data;
        
        if (!weatherData.current_weather) {
          console.warn('API响应缺少current_weather字段', weatherData);
          throw new Error('天气服务返回的数据结构异常');
        }
        
        const requiredFields = ['temperature', 'windspeed', 'weathercode'];
        const missingFields = requiredFields.filter(
          field => !(field in weatherData.current_weather)
        );
        
        if (missingFields.length > 0) {
          throw new Error(`缺少必需字段: ${missingFields.join(', ')}`);
        }
        
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
    
    getWeatherIcon(code, isDay) {
      const icons = {
        0: isDay === 1 ? 'fas fa-sun' : 'fas fa-moon',
        1: isDay === 1 ? 'fas fa-cloud-sun' : 'fas fa-cloud-moon',
        2: 'fas fa-cloud',
        3: 'fas fa-cloud',
        45: 'fas fa-smog',
        48: 'fas fa-smog',
        51: 'fas fa-cloud-rain',
        53: 'fas fa-cloud-rain',
        55: 'fas fa-cloud-showers-heavy',
        56: 'fas fa-icicles',
        57: 'fas fa-icicles',
        61: 'fas fa-cloud-rain',
        63: 'fas fa-cloud-showers-heavy',
        65: 'fas fa-cloud-showers-heavy',
        66: 'fas fa-icicles',
        67: 'fas fa-icicles',
        71: 'fas fa-snowflake',
        73: 'fas fa-snowflake',
        75: 'fas fa-snowflake',
        77: 'fas fa-snowflake',
        80: 'fas fa-cloud-rain',
        81: 'fas fa-cloud-showers-heavy',
        82: 'fas fa-poo-storm',
        85: 'fas fa-snowflake',
        86: 'fas fa-snowflake',
        95: 'fas fa-bolt',
        96: 'fas fa-bolt',
        99: 'fas fa-bolt'
      };
      return icons[code] || 'fas fa-question';
    },
    
    weatherCodeToText(code) {
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
    
    getWindDirection(degrees) {
      if (degrees === null || degrees === undefined) return '未知';
      const directions = ['北', '东北', '东', '东南', '南', '西南', '西', '西北'];
      const index = Math.round((degrees % 360) / 45) % 8;
      return `${directions[index]} (${degrees}°)`;
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
      
      const matchedCity = coastalCities.find(city => 
        lat >= city.range[0] && lat <= city.range[2] &&
        lng >= city.range[1] && lng <= city.range[3]
      );
      
      this.locationName = matchedCity ? matchedCity.name : `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
    }
  }
};
</script>

<style scoped>
.weather-widget {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  background: linear-gradient(135deg, #72b5f7 0%, #4a90e2 100%);
  color: white;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 400px;
}

.weather-widget.night-mode {
  background: linear-gradient(135deg, #1a2a6c 0%, #3a3a7a 100%);
}

.widget-header {
  margin-bottom: 15px;
}

.location-title {
  display: flex;
  align-items: center;
  margin: 0 0 10px 0;
  font-size: 1.5rem;
  flex-wrap: wrap;
}

.location-title i {
  margin-right: 10px;
  font-size: 1.2em;
}

.last-updated {
  margin-left: auto;
  font-size: 0.8rem;
  opacity: 0.8;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 0;
  gap: 15px;
  flex-grow: 1;
}

.loading-state p {
  margin: 0;
}

/* 错误状态 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 0;
  gap: 15px;
  text-align: center;
  flex-grow: 1;
}

.error-state i {
  font-size: 2rem;
  color: #ff6b6b;
}

.retry-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.3);
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-btn:hover {
  background-color: rgba(255, 255, 255, 0.4);
}

/* 天气显示区域 */
.weather-display {
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex-grow: 1;
}

.main-weather {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
}

.temperature-display {
  display: flex;
  align-items: flex-start;
  line-height: 1;
}

.temperature-display .value {
  font-size: 4.5rem;
  font-weight: 300;
}

.temperature-display .unit {
  font-size: 2rem;
  margin-top: 5px;
}

.weather-icon {
  text-align: center;
}

.weather-icon i {
  font-size: 3.5rem;
  margin-bottom: 5px;
}

.weather-condition {
  font-size: 1.2rem;
  font-weight: 500;
}

/* 天气详情 */
.weather-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
  background-color: rgba(255, 255, 255, 0.1);
  padding: 15px;
  border-radius: 10px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.detail-item i {
  font-size: 1.5rem;
  opacity: 0.8;
}

.detail-label {
  font-size: 0.8rem;
  opacity: 0.8;
}

.detail-value {
  font-size: 1rem;
  font-weight: 500;
}

/* 输入框区域 */
.location-controls {
  margin-top: auto;
  padding-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.coord-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group label {
  margin-bottom: 6px;
  font-size: 0.9rem;
  opacity: 0.9;
}

.input-group input {
  width: 90%;
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.input-group input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.4);
  background-color: rgba(255, 255, 255, 0.2);
}

.input-group input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.refresh-btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
}

.refresh-btn:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 响应式调整 */
@media (max-width: 600px) {
  .weather-widget {
    padding: 15px;
    min-height: auto;
  }
  
  .location-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .last-updated {
    margin-left: 0;
  }
  
  .coord-inputs {
    grid-template-columns: 1fr;
  }
  
  .input-group input {
    padding: 8px 10px;
  }
  
  .temperature-display .value {
    font-size: 3.5rem;
  }
  
  .weather-icon i {
    font-size: 2.5rem;
  }
}
</style>