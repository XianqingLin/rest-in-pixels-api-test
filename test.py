"""
一键测试 SiliconFlow 国内外两个端点
1. 连通性（GET /v1/models）
2. 取回模型列表
3. 发一条最小对话（DeepSeek-V2-Chat 为例）
"""

import os
import sys
import time
import requests

# ========== 用户唯一需要改的地方 ==========
API_KEY = "sk-voayppyfcpwacihimubbugqnkswudyrevvqvptokbfhvoyxk"  # ← 换成你的 key
# ========================================

ENDPOINTS = {
    "domestic": "https://api.siliconflow.cn/v1",
    "global": "https://api-st.siliconflow.cn/v1",
}

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

MODEL_ID = "deepseek-ai/DeepSeek-V3.2-Exp"   # 两个节点都支持


# ---------- 工具 ----------
def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")


# ---------- 工具 ----------
def test_one(region, base):
    log(f"==== 开始测试 {region} 节点  {base} ====")

    # 1. 连通性 + 模型列表
    try:
        rsp = requests.get(f"{base}/models", headers=HEADERS, timeout=10)
        if rsp.status_code != 200:
            log(f"❌ /models 返回 {rsp.status_code}  {rsp.text[:200]}")
            return
        models = [m["id"] for m in rsp.json().get("data", [])]
        log(f"✅ 模型列表拉取成功，共 {len(models)} 个模型")
    except Exception as e:
        log(f"❌ 拉取模型列表失败：{e}")
        return

    # ====== 改动 1：用局部变量 model_id ======
    model_id = MODEL_ID          # 先拿全局默认值
    if model_id not in models:
        log(f"⚠️  模型 {model_id} 不在列表中，改用列表第一个模型")
        model_id = models[0] if models else "deepseek-ai/DeepSeek-V2-Chat"

    # 2. 简单对话测试
    payload = {
        "model": model_id,       # ====== 改动 2：用局部变量 ======
        "messages": [{"role": "user", "content": "hello"}],
        "max_tokens": 20,
        "temperature": 0.3,
    }
    try:
        rsp = requests.post(f"{base}/chat/completions", json=payload, headers=HEADERS, timeout=15)
        if rsp.status_code != 200:
            log(f"❌ /chat/completions 返回 {rsp.status_code}  {rsp.text[:200]}")
            return
        reply = rsp.json()["choices"][0]["message"]["content"].strip()
        log(f"✅ 对话返回：{reply}")
    except Exception as e:
        log(f"❌ 对话失败：{e}")

    log(f"==== {region} 节点测试完成 ====\n")


# ---------- 主入口 ----------
if __name__ == "__main__":
    if API_KEY.startswith("sk-"):
        for region, base in ENDPOINTS.items():
            test_one(region, base)
        log("全部测试结束！")
    else:
        print("请先设置正确的 API_KEY！")
        sys.exit(1)
