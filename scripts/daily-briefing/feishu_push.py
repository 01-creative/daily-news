"""飞书推送模块 — 读取当日早报文件，推送到飞书群"""
import os
import sys
import requests
from datetime import datetime
from pathlib import Path


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = Path(f"ctf-training/日报/{today}.md")

    if not filepath.exists():
        print(f"❌ 早报文件不存在: {filepath}")
        sys.exit(1)

    content = filepath.read_text(encoding="utf-8")

    if len(content.strip()) < 50:
        print(f"❌ 早报内容过短 ({len(content)} chars)，可能是生成失败")
        sys.exit(1)

    webhook = os.environ.get("FEISHU_WEBHOOK")
    if not webhook:
        print("❌ 未设置 FEISHU_WEBHOOK 环境变量")
        sys.exit(1)

    resp = requests.post(
        webhook,
        json={"msg_type": "text", "content": {"text": content}},
        timeout=30,
    )
    result = resp.json()
    if result.get("code") == 0:
        print(f"✅ 早报已推送到飞书 ({len(content)} chars)")
    else:
        print(f"❌ 飞书推送失败: {result}")
        sys.exit(1)


if __name__ == "__main__":
    main()
