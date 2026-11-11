"""飞书推送模块 — 读取当周周报文件，推送到飞书群"""
import os
import re
import sys
import requests
from datetime import datetime
from pathlib import Path

MAX_UNITS = 5000


def count_units(text: str) -> int:
    """汉字逐字计 1，英文/数字连续串计 1 词；URL、标点、空白、Markdown 符号不计。"""
    text = re.sub(r"https?://\S+", " ", text)
    cjk = len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]", text))
    words = len(re.findall(r"[A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*", text))
    return cjk + words


def main():
    today = os.environ.get("BRIEFING_DATE", datetime.now().strftime("%Y-%m-%d"))
    filepath = Path(f"ctf-training/周报/{today}.md")

    if not filepath.exists():
        print(f"❌ 周报文件不存在: {filepath}")
        sys.exit(1)

    content = filepath.read_text(encoding="utf-8")

    if len(content.strip()) < 50:
        print(f"❌ 周报内容过短 ({len(content)} chars)，可能是生成失败")
        sys.exit(1)

    units = count_units(content)
    if units > MAX_UNITS:
        print(f"⚠️ 周报超出字数上限: {units} > {MAX_UNITS}（汉字+单词，照常推送，请检查提示词）")
    else:
        print(f"ℹ️ 字数检查通过: {units} / {MAX_UNITS}（汉字+单词）")

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
        print(f"✅ 周报已推送到飞书 ({len(content)} chars, {units} 汉字+单词)")
    else:
        print(f"❌ 飞书推送失败: {result}")
        sys.exit(1)


if __name__ == "__main__":
    main()
