#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SiliconFlow 国内外双端点连通性 & 对话测试
本地运行：export SILICONFLOW_API_KEY="sk-xxx"  &&  python test_sf.py
GitHub Actions 会自动注入同名 Secret。
"""

import os
import sys
import time
import logging
import requests

# ---------- 日志同时输出到屏幕和文件 ----------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("test.log", encoding="utf-8")
    ]
)
log = logging.info

# ---------- 配置 ----------
API_KEY = os.getenv("SILICONFLOW_API_KEY") or os.getenv("API_KEY")
if not API_KEY:
    log("❌ 请先设置环境变量 SILICONFLOW_API_KEY 或 API_KEY")
    sys.exit(1)

ENDPOINTS = {
    "domestic": "https://api.siliconflow.cn/v1",
    "global": "https://api-st.siliconflow.cn/v1",
}

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

DEFAULT_MODEL = "deepseek-ai/DeepSeek-V2-Chat"   # 两个节点都支持


# ---------- 单节点测试 ----------
def test_one(region: str, base: str):
    log(f"==== 开始测试 {region} 节点  {base} ====")

    # 1. 连通性 + 模型列表
    try:
        rsp = requests.get(f"{base}/models", headers=HEADERS, timeout=15)
        rsp.raise_for_status()
        models = [m["id"] for m in rsp.json().get("data", [])]
        log(f"✅ 模型列表拉取成功，共 {len(models)} 个模型")
    except Exception as e:
        log(f"❌ 拉取模型列表失败：{e}")
        return

    # 选模型
    model_id = DEFAULT_MODEL if DEFAULT_MODEL in models else (models[0] if models else DEFAULT_MODEL)

    # 2. 最小对话
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": "hello"}],
        "max_tokens": 20,
        "temperature": 0.3,
        "stream": False
    }
    try:
        rsp = requests.post(f"{base}/chat/completions", json=payload, headers=HEADERS, timeout=15)
        rsp.raise_for_status()
        reply = rsp.json()["choices"][0]["message"]["content"].strip()
        log(f"✅ 对话返回：{reply}")
    except Exception as e:
        log(f"❌ 对话失败：{e}")

    log(f"==== {region} 节点测试完成 ====\n")


# ---------- 主入口 ----------
if __name__ == "__main__":
    for region, base in ENDPOINTS.items():
        test_one(region, base)
    log("全部测试结束！结果同时写入 test.log")
