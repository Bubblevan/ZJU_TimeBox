import os
import json
from icalendar import Event, Calendar
from datetime import datetime, timedelta

# 目录路径
data_folder = './yunfeng'

# 创建一个新的日历
cal = Calendar()

# 遍历目录中的所有 JSON 文件
for file_name in os.listdir(data_folder):
    if file_name.endswith('.json'):
        file_path = os.path.join(data_folder, file_name)
        
        # 读取 JSON 文件
        with open(file_path, 'r', encoding='utf-8') as f:
            notice = json.load(f)
            
            # 创建一个事件
            event = Event()
            event.add('summary', notice['title'])
            event.add('description', notice['content'])
            
            # 解析日期和时间（假设时间格式为 "YYYY-MM-DD"）
            start_date = datetime.strptime(notice['date'], "%Y-%m-%d")
            
            # 假设事件持续 2 天
            end_date = start_date + timedelta(days=2)
            
            event.add('dtstart', start_date)
            event.add('dtend', end_date)
            
            # 将事件添加到日历中
            cal.add_component(event)

# 将日历保存到 ICS 文件中
with open('events.ics', 'wb') as f:
    f.write(cal.to_ical())
