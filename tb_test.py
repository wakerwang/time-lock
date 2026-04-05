import requests

# 替换为你的 OpenRouter API Key
OPENROUTER_API_KEY = "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"

BASE_URL = "https://openrouter.ai/api/v1"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "nvidia/nemotron-3-super-120b-a12b:free",
    "messages": [
        {"role": "user", "content": "你好！请简单回复一句话，验证我能调用模型"}
    ],
    "temperature": 0.7
}

try:
    response = requests.post(BASE_URL, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    reply = result["choices"][0]["message"]["content"]
    print("模型回复：", reply)
except Exception as e:
    print("发生错误：", str(e))
    if 'response' in locals():
        print("原始响应：", response.text)