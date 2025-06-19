import csv
import mysql.connector
from datetime import datetime

# 配置数据库连接
config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'projectdatabase',
    'raise_on_warnings': True
}

# 连接数据库
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

# 读取CSV并插入数据
with open('Fish.csv', 'r', encoding='utf-8') as f:
    csv_reader = csv.DictReader(f)
    insert_query = """INSERT INTO fish_fish (
        fisher_id, species, weight, length1, length2, length3,
        height, width, added_at, is_alive, died_at
      ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    batch_data = []
    for row in csv_reader:
        # 数据清洗：跳过无效记录
        if float(row['Weight(g)']) <= 0:
            continue

        # 构造数据元组
        data = (
            int(row['fisher']),  # fisher_id
            row['Species'],
            float(row['Weight(g)']),
            float(row['Length1(cm)']),
            float(row['Length2(cm)']),
            float(row['Length3(cm)']),
            float(row['Height(cm)']),
            float(row['Width(cm)']),
            datetime.now(),  # added_at使用当前时间
            True,   # is_alive默认为True
            None    # died_at默认为NULL
        )
        batch_data.append(data)

    # 批量插入
    cursor.executemany(insert_query, batch_data)
    conn.commit()

print(f"成功插入 {cursor.rowcount} 条数据")

# 关闭连接
cursor.close()
conn.close()