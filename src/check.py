#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""上线前自检：标签闭合 / 资源引用 / og 标签 / 占位符残留 / 价格文案一致性"""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src" / "data"
SITE = json.loads((DATA / "site.json").read_text(encoding="utf-8"))
BASE = SITE["base_url"]

PAGES = {
    "主域": ROOT / "index.html",
    "数学": ROOT / "math" / "index.html",
    "物理": ROOT / "physics" / "index.html",
    "化学": ROOT / "chemistry" / "index.html",
}

VOID = {"meta", "link", "img", "br", "hr", "input", "source", "path", "circle", "rect", "polyline"}


class Checker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
        self.imgs = []
        self.links = []
        self.metas = {}
        self.title = ""

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "img":
            self.imgs.append(d.get("src", ""))
        if tag == "link":
            self.links.append(d.get("href", ""))
        if tag == "meta":
            k = d.get("property") or d.get("name")
            if k:
                self.metas[k] = d.get("content", "")
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"多余的闭合标签 </{tag}>")
            return
        if self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.errors.append(f"标签不匹配：期望 </{self.stack[-1]}>，实际 </{tag}>")
            # 尝试回退
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass


def check_page(name, path):
    print(f"\n=== {name}（{path.relative_to(ROOT)}）===")
    html = path.read_text(encoding="utf-8")
    c = Checker()
    c.feed(html)
    print(f"  体积：{len(html)/1024:.1f} KB")

    if c.stack:
        print(f"  [问题] 未闭合标签：{c.stack}")
    elif c.errors:
        print(f"  [问题] {c.errors[:5]}")
    else:
        print("  [ok] 标签闭合正常")

    t = re.search(r"<title>(.*?)</title>", html, re.S)
    print(f"  title：{t.group(1) if t else '[缺失]'}")

    # og
    for k in ["description", "og:title", "og:description", "og:image", "og:url"]:
        v = c.metas.get(k, "")
        if not v:
            print(f"  [缺失] {k}")
        else:
            print(f"  {k}：{v[:78]}")

    # 占位符残留
    leftovers = re.findall(r"\$[a-z_]{3,}", html)
    bad = [x for x in set(leftovers) if not x.startswith("$0")]
    if bad:
        print(f"  [问题] 模板占位符残留：{bad}")
    else:
        print("  [ok] 无模板占位符残留")

    # 图片资源
    for src in c.imgs:
        if src.startswith("http") or src.startswith("data:"):
            kind = "内联 base64" if src.startswith("data:") else "外链"
            print(f"  图片 {kind}：跳过本地校验（{len(src)//1024 if len(src) > 1024 else len(src)}{'KB' if len(src) > 1024 else 'B'}）")
            continue
        p = path.parent / src
        print(f"  图片 {src}：{'存在' if p.exists() else '[缺失!]'} {p.stat().st_size//1024 if p.exists() else ''} KB")

    # 站内链接
    hrefs = re.findall(r'href="(/[^"]*)"', html)
    for h in sorted(set(hrefs)):
        target = ROOT / h.lstrip("/")
        ok = (target / "index.html").exists() or (h == "/" )
        print(f"  链接 {h} → {'ok' if ok else '[目标不存在!]'}")

    return html


def check_prices():
    print("\n=== 价格与文案交叉核对 ===")
    expect = {
        "数学": {
            "file": DATA / "math.json",
            "rows": [(180, 140), (250, 160)],
            "trial": [90, 125],
        },
        "物理": {
            "file": DATA / "physics.json",
            "rows": [(250, 160), (320, 200)],
            "trial": [125, 160],
        },
        "化学": {
            "file": DATA / "chemistry.json",
            "rows": [(250, 160)],
            "trial": [125],
        },
    }
    for name, cfg in expect.items():
        j = json.loads(cfg["file"].read_text(encoding="utf-8"))
        rows = [(r["price"], r["form"]) for r in j["pricing_rows"]]
        prices = [r["price"] for r in j["pricing_rows"]]
        want = sorted([p for pair in cfg["rows"] for p in pair])
        trial = [r["price"] for r in j["trial_rows"]]
        ok1 = sorted(prices) == want
        ok2 = trial == cfg["trial"]
        print(f"  {name}正价 {prices} 期望 {want} → {'ok' if ok1 else '[不一致!]'}")
        print(f"  {name}试听 {trial} 期望 {cfg['trial']} → {'ok' if ok2 else '[不一致!]'}")

    # 与 site.json 总表比对
    p = SITE["prices"]
    print(f"  site.json 总表：小学 {p['primary']['one']}/{p['primary']['group']}　"
          f"初中 {p['junior']['one']}/{p['junior']['group']}　"
          f"高中 {p['senior']['one']}/{p['senior']['group']}　冲刺 {p['sprint']['one']}")
    # 主页硬编码价格是否仍一致
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    for key, label in [("180 元/课时", "小学数学一对一"), ("250 元/课时", "初中一对一"),
                       ("320 元/课时", "高中物理一对一"), ("160 元/人/课时", "初中小班"),
                       ("200 元/人/课时", "高中小班"), ("90/初中125/高中160", "试听价")]:
        print(f"  主页包含 '{key}'：{'ok' if key in home else '[缺失!]'}")


def check_contact():
    print("\n=== 联系方式一致性 ===")
    ph = SITE["contact"]["phone"]
    disp = SITE["contact"]["phone_display"]
    for name, path in PAGES.items():
        html = path.read_text(encoding="utf-8")
        has_disp = disp in html
        has_tel = f"tel:{ph}" in html
        print(f"  {name}：显示 {disp} {'ok' if has_disp else '[缺失!]'}　"
              f"tel 链接 {'ok' if has_tel else '[缺失!]'}")


def main():
    for name, path in PAGES.items():
        if not path.exists():
            print(f"[错误] 页面不存在：{path}")
            continue
        check_page(name, path)
    check_prices()
    check_contact()
    print("\n检查完成。")


if __name__ == "__main__":
    main()
