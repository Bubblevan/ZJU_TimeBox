import requests
import json

# 扣子 API 的 URL 和 API 密钥
API_URL = "https://api.coze.cn/v3/chat"
API_KEY = "pat_lh9minUw0dYuu6QHFIq7rz1kY6tkFv70Iiic766T3IGNn2PuxxZijAGdOh9ZFknb"

# 请求头
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 请求体
payload = {
    "bot_id": "7435604864455442486",
    "user_id": "12313",
    "stream": True,
    "auto_save_history": True,
    "additional_messages": [
        {
            "role": "user",
            "content": "晚上好",
            "content_type": "text"
        }
    ]
}

# 发送请求
response = requests.post(API_URL, headers=headers, json=payload, stream=True)

# 处理流式响应
if response.status_code == 200:
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            if decoded_line.startswith("event:"):
                event_type = decoded_line.split(":")[1].strip()
            elif decoded_line.startswith("data:"):
                data = decoded_line.split(":", 1)[1].strip()
                try:
                    json_data = json.loads(data)
                    if event_type == "conversation.message.delta":
                        print("机器人响应:", json_data["content"])
                    elif event_type == "conversation.chat.completed":
                        print("对话历史:", json_data)
                except json.JSONDecodeError:
                    print("无法解析的响应行:", decoded_line)
else:
    print(f"请求失败: {response.status_code}")
