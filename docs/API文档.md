# 水产养殖监控系统 API 文档

## 1. 主要信息

### 1.1 水文气象数据

- **URL**: `/api/main_info/hydro-meteorological/`
- **Method**: `GET`
- **权限**: 所有用户
- **参数**:
  - `start_date`: 开始日期 (YYYY-MM-DD)
  - `end_date`: 结束日期 (YYYY-MM-DD)
  - `device_id`: 设备ID (可选)
- **响应**:

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "device_id": "DEV001",
      "salinity": 35.2,
      "dissolved_oxygen": 8.5,
      "turbidity": 12.3,
      "ph": 7.8,
      "water_temperature": 25.5,
      "record_time": "2025-05-12T12:00:00Z"
    }
  ]
}
```

### 1.2 设备状态

- **URL**: `/api/main_info/device-status/`
- **Method**: `GET`
- **权限**: 所有用户
- **参数**:
  - `device_id`: 设备ID (可选)
- **响应**:

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "device_id": "DEV001",
      "main_controller": {
        "version": "v1.2.3",
        "temperature": 30.2
      },
      "sub_controller": {
        "connection_status": "connected"
      },
      "time_calibration": "2025-05-12T12:00:00Z",
      "alerts": ["温度异常"]
    }
  ]
}
```

### 1.3 历史记录查询

- **URL**: `/api/main_info/historical-data/`
- **Method**: `GET`
- **权限**: 所有用户
- **参数**:
  - `data_type`: 数据类型 (hydro_meteorological, device_status, fish_population)
  - `start_date`: 开始日期 (YYYY-MM-DD)
  - `end_date`: 结束日期 (YYYY-MM-DD)
  - `device_id`: 设备ID (可选)
- **响应**:

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "data_type": "hydro_meteorological",
      "data": {
        "salinity": 35.2,
        "dissolved_oxygen": 8.5
      },
      "record_time": "2025-05-12T12:00:00Z"
    }
  ]
}
```

## 2. 水下系统

### 2.1 鱼群信息

- **URL**: `/api/underwater-sys/fish-population/`
- **Method**: `GET`
- **权限**: 所有用户
- **参数**:
  - `start_date`: 开始日期 (YYYY-MM-DD)
  - `end_date`: 结束日期 (YYYY-MM-DD)
  - `device_id`: 设备ID (可选)
- **响应**:

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "device_id": "DEV001",
      "total_fish": 1000,
      "new_fish_today": 50,
      "dead_fish_today": 10,
      "fish_species_count": 5,
      "fry_count": 200,
      "record_time": "2025-05-12T12:00:00Z"
    }
  ]
}
```

### 2.2 设备信息

- **URL**: `/api/underwater-sys/underwater-devices/`
- **Method**: `GET`
- **权限**: 所有用户
- **响应**:

```json
{
  "status": "success",
  "data": {
    "camera_count": 5,
    "pan_tilt_count": 3,
    "sonar_count": 2,
    "cage_info": [
      {
        "id": "CAGE001",
        "location": "位置A",
        "status": "active"
      }
    ],
    "water_quality": {
      "device_id": "DEV001",
      "salinity": 35.2,
      "dissolved_oxygen": 8.5
    }
  }
}
```

## 3. 智能中心

### 3.1 气象数据

- **URL**: `/api/underwater-sys/weather-data/`
- **Method**: `GET`
- **权限**: 所有用户
- **参数**:
  - `start_date`: 开始日期 (YYYY-MM-DD)
  - `end_date`: 结束日期 (YYYY-MM-DD)
- **响应**:

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "temperature": 28.5,
      "light_intensity": 80000,
      "wind_speed": 3.2,
      "wind_direction": "NE",
      "humidity": 75.0,
      "aqi": 50,
      "record_time": "2025-05-12T12:00:00Z"
    }
  ]
}
```

### 3.2 鱼群数据

- **URL**: `/api/underwater-sys/fish-data/`
- **Method**: `GET`
- **权限**: 所有用户
- **参数**:
  - `fish_id`: 鱼ID (可选)
  - `cage_id`: 网箱ID (可选)
- **响应**:

```json
{
  "status": "success",
  "data": {
    "individual_fish": [
      {
        "id": "FISH001",
        "species": "鲤鱼",
        "length": 25.5,
        "weight": 1.2,
        "health_status": "健康",
        "abnormalities": [],
        "track": [
          {"x": 10, "y": 20, "time": "2025-05-12T12:00:00Z"},
          {"x": 15, "y": 25, "time": "2025-05-12T12:01:00Z"}
        ]
      }
    ],
    "cage_data": [
      {
        "id": "CAGE001",
        "fish_count": 500,
        "water_quality": {
          "temperature": 25.5,
          "ph": 7.8
        }
      }
    ]
  }
}
```

### 3.3 AI决策

- **URL**: `/api/underwater-sys/ai-decision/`
- **Method**: `GET`
- **权限**: 所有用户
- **参数**:
  - `device_id`: 设备ID (可选)
  - `cage_id`: 网箱ID (可选)
- **响应**:

```json
{
  "status": "success",
  "data": {
    "optimal_conditions": {
      "water_temperature": {"min": 24, "max": 26},
      "ph": {"min": 7.5, "max": 8.5},
      "dissolved_oxygen": {"min": 6.0, "max": 10.0}
    },
    "environment_score": 85,
    "warnings": [
      {
        "type": "temperature_high",
        "level": "warning",
        "message": "水温偏高，请注意监测",
        "timestamp": "2025-05-12T12:00:00Z"
      }
    ]
  }
}
```

## 4. 管理界面

### 4.1 用户管理

- **URL**: `/api/user/list/`
- **Method**: `GET` (获取用户列表)
- **权限**: 管理员
- **响应**:

```json
{
  "status": "success",
  "user_list": [
    {
      "user_id": 1,
      "account": "user1",
      "is_approved": false,
      "role": "user",
      "create_time": "2025-05-16T14:22:41Z"
    }
    {
      "user_id": 2,
      "account": "user2",
      "is_approved": true,
      "role": "user",
      "create_time": "2025-05-16T14:22:41Z"
    }
  ]
}
```

- **URL**: `/api/user/info/<int:user_id>/`
- **Method**: `GET`(获取用户信息)
- **权限**: `IsApproved`
- **响应**:

```json
{
  "status": "success",
  "user": {
    "user_id": 1,
    "account": "user1",
    "is_approved": true,
    "role": "user",
    "created_at": "2025-05-10T10:00:00Z"
  }
}
```

- **URL**: `/api/user/update/{user_id}/`
- **Method**: `PUT` (更新用户信息)
- **权限**: 管理员
- **请求体**:(可选，但是至少包含一条修改内容)

```json
{
  "account": "newaccount",
  "password": "newpassword",
  "is_approved": true,
  "role": "admin",
}
```

- **响应**:

```json
{
  "status": "success",
  "message": "update success",
  "user": {
    "user_id": 1,
    "account": "newaccount",
    "is_approved": true,
    "role": "role"
  }
}
```

### 4.2 系统管理

- **URL**: `/api/system-settings/`
- **Method**: `GET` (获取系统设置)
- **权限**: 管理员
- **响应**:

```json
{
  "status": "success",
  "data": {
    "system_name": "水产养殖监控系统",
    "version": "v1.0.0",
    "maintenance_mode": false,
    "last_backup": "2025-05-12T02:00:00Z"
  }
}
```

## 5. 认证接口

### 5.1 用户注册

- **URL**: `/api/user/register/`
- **Method**: `POST`
- **权限**: 公开
- **请求体**:

```json
{
  "account": "newuser",
  "password": "password123",
  "role": "user"
}
```

- **响应**:

```json
{
  "status": "success",
  "message": "register success",
  "user": {
    "user_id": 2,
    "account": "newuser",
    "role": "user"
  },
  "access": "access-token",
  "refresh": "refresh-token"
}
```

### 5.2 用户登录

- **URL**: `/api/user/login/`
- **Method**: `POST`
- **权限**: 公开
- **请求体**:

```json
{
  "account": "newuser",
  "password": "password123"
}
```

- **响应**:

```json
{
  "status": "success",
  "message": "登录成功",
  "user": {
    "user_id": 1,
    "account": "user1",
    "role": "user"
  },
  "access": "access-token",
  "refresh": "refresh-token"
}
```

### 5.3 刷新令牌

- **URL**: `/api/user/access/`
- **Method**: `POST`
- **权限**: `IsApproved`
- **请求**:

```json
{
  "user_id": 1,
  "refresh": "refresh-token"
}
```

- **响应**:

```json
{
  "status": "success",
  "access": "new-auth-token"
}
```

### 5.4 渔民注册

- **URL**: `/api/user/register_fisher/`
- **Method**: `POST`
- **权限**: `IsApproved`
- **请求**:

```json
```

- **响应**:

```json
```

## 错误处理

所有API返回统一格式的错误响应：

```json
{
"status": "error",
"code": "invalid_request",
"message": "无效请求",
"details": {
    "field": "错误字段",
    "reason": "错误原因"
    }
}
```

常见错误码：

- `unauthorized`: 未授权访问
- `permission_denied`: 权限不足
- `invalid_request`: 无效请求
- `not_found`: 资源不存在
- `server_error`: 服务器内部错误
