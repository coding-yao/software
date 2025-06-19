import os
import json
import mysql.connector
from datetime import datetime

'''
如果MySQL版本低于8.0.20
替换 line76 的插入语法如下：
insert_query = """
INSERT INTO environment_waterdata (
    location, province, domain, time, water_type, temperature, 
    ph, oxygen, conductivity, turbidity, kmno4, nh4, 
    all_p, all_n, iaa_alpha, cells, status
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
ON DUPLICATE KEY UPDATE
    water_type=VALUES(water_type),
    temperature=VALUES(temperature),
    ph=VALUES(ph),
    oxygen=VALUES(oxygen),
    conductivity=VALUES(conductivity),
    turbidity=VALUES(turbidity),
    kmno4=VALUES(kmno4),
    nh4=VALUES(nh4),
    all_p=VALUES(all_p),
    all_n=VALUES(all_n),
    iaa_alpha=VALUES(iaa_alpha),
    cells=VALUES(cells),
    status=VALUES(status)
"""

'''


# 数据库配置
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'projectdatabase',
    'raise_on_warnings': True
}

def parse_value(value, default=None):
    """处理数值数据，包括HTML标签和特殊值"""
    if isinstance(value, str):
        if value == '--' or value == '*' or value == '':
            return default
        if '<' in value and '>' in value:
            # 提取tooltip中的原始值
            if 'title=' in value and '原始值：' in value:
                try:
                    return float(value.split('原始值：')[1].split("'")[0])
                except:
                    pass
            # 否则提取显示值
            value = value.split('>')[-2].split('<')[0]
        try:
            return float(value)
        except ValueError:
            # 尝试处理水质类别（如'Ⅱ'）
            if value in ['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ', '劣Ⅴ']:
                return {'Ⅰ': 1, 'Ⅱ': 2, 'Ⅲ': 3, 'Ⅳ': 4, 'Ⅴ': 5, '劣Ⅴ': 6}.get(value)
            return default
    return value if value is not None else default

def import_water_data(data_dir):
    """导入水质数据到数据库"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 更新后的SQL插入语句 - 使用新的语法
        insert_query = """
        INSERT INTO environment_waterdata (
            location, province, domain, time, water_type, temperature, 
            ph, oxygen, conductivity, turbidity, kmno4, nh4, 
            all_p, all_n, iaa_alpha, cells, status
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) AS new
        ON DUPLICATE KEY UPDATE
            water_type=new.water_type,
            temperature=new.temperature,
            ph=new.ph,
            oxygen=new.oxygen,
            conductivity=new.conductivity,
            turbidity=new.turbidity,
            kmno4=new.kmno4,
            nh4=new.nh4,
            all_p=new.all_p,
            all_n=new.all_n,
            iaa_alpha=new.iaa_alpha,
            cells=new.cells,
            status=new.status
        """
        
        total_imported = 0
        batch_data = []
        batch_size = 1000  # 批量插入的大小
        
        # 遍历所有月份文件夹
        for month_dir in os.listdir(data_dir):
            month_path = os.path.join(data_dir, month_dir)
            if os.path.isdir(month_path):
                # 遍历该月所有数据文件
                for file_name in os.listdir(month_path):
                    if file_name.endswith('.json'):
                        file_path = os.path.join(month_path, file_name)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                daily_data = json.load(f)
                                if 'tbody' in daily_data:
                                    date_str = file_name.replace('.json', '')
                                    try:
                                        # 验证日期格式
                                        datetime.strptime(date_str, '%Y-%m-%d')
                                    except ValueError:
                                        print(f"跳过无效日期文件: {file_path}")
                                        continue
                                    
                                    for record in daily_data['tbody']:
                                        if len(record) >= 16:  # 根据你的JSON格式，有16个字段
                                            try:
                                                # 处理断面名称中的HTML标签
                                                domain = record[2]
                                                if '<' in domain and '>' in domain:
                                                    domain = domain.split('>')[-2].split('<')[0]
                                                
                                                # 处理监测时间
                                                record_time = record[3] if record[3] else date_str
                                                if record_time and len(record_time.split()) == 1:
                                                    # 如果只有日期没有时间，添加默认时间
                                                    record_time = f"{record_time} 00:00"
                                                elif record_time and len(record_time.split()) == 2:
                                                    # 如果有日期和时间，但日期只有月日，需要加上年份
                                                    month_day, time_part = record_time.split()
                                                    record_time = f"{date_str[:4]}-{month_day} {time_part}"
                                                
                                                # 确保water_type有默认值0而不是NULL
                                                water_type = parse_value(record[4], default=0)
                                                
                                                # 准备数据元组 - 根据模型调整字段顺序
                                                data = (
                                                    record[0],  # location (省份)
                                                    record[1],  # province (流域)
                                                    domain,     # domain (断面名称)
                                                    record_time, # time (监测时间)
                                                    water_type, # water_type
                                                    parse_value(record[5], default=None),  # temperature
                                                    parse_value(record[6], default=None),  # ph
                                                    parse_value(record[7], default=None),  # oxygen
                                                    parse_value(record[8], default=None),  # conductivity
                                                    parse_value(record[9], default=None),  # turbidity
                                                    parse_value(record[10], default=None),  # kmno4
                                                    parse_value(record[11], default=None),  # nh4
                                                    parse_value(record[12], default=None),  # all_p
                                                    parse_value(record[13], default=None),  # all_n
                                                    parse_value(record[14], default=None),  # iaa_alpha
                                                    parse_value(record[15], default=None),  # cells
                                                    record[16] if len(record) > 16 else ''  # status
                                                )
                                                
                                                batch_data.append(data)
                                                total_imported += 1
                                                
                                                # 批量插入
                                                if len(batch_data) >= batch_size:
                                                    cursor.executemany(insert_query, batch_data)
                                                    conn.commit()
                                                    print(f"已导入 {total_imported} 条记录...")
                                                    batch_data = []
                                                
                                            except Exception as e:
                                                print(f"处理记录时出错: {str(e)}, 记录: {record}")
                                                continue
                        except Exception as e:
                            print(f"读取文件 {file_path} 时出错: {str(e)}")
                            continue
        
        # 插入剩余的数据
        if batch_data:
            cursor.executemany(insert_query, batch_data)
            conn.commit()
        
        print(f"数据导入完成，共导入 {total_imported} 条记录")
        
    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    data_dir = os.path.join('water_quality_by_time')  # 替换为你的数据目录路径
    import_water_data(data_dir)