#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二维码修正：修掉被压扁的显示缺陷，并把内联体积降下来。

问题：主页内联的是整张微信名片截图（200x295 竖图），但容器是 70x70 正方形，
      图片被纵向压成 0.34 倍，二维码变形；且同一张图重复内联 3 次，共 92KB。
处理：用 src/qr_tool.py 从高清原图重建出正方形二维码（360x360，2.3KB），
      替换全部内联位置，并给容器补 object-fit，避免以后再被拉伸。
幂等：靠 <!-- v6:qr --> 标记跳过。
文件名不用版本号，避免和内容轮次（v2~v6）的编号混在一起。
"""
import os
import re
import sys
import base64
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "index.html")
QR = os.path.join(ROOT, "src", "assets", "qr-square.png")

MARKER = "<!-- v6:qr -->"


def png_size(path):
    d = open(path, "rb").read()
    return struct.unpack(">II", d[16:24])


def main():
    html = open(HTML, encoding="utf-8").read()
    if MARKER in html:
        print("二维码已替换过，跳过")
        return

    if not os.path.exists(QR):
        sys.exit("缺少 src/assets/qr-square.png，请先运行 python3 src/qr_tool.py")

    new_b64 = base64.b64encode(open(QR, "rb").read()).decode()
    new_src = "data:image/png;base64," + new_b64

    # 找出所有大体积内联 PNG，确认它们都是同一张竖版名片截图
    olds = []
    for m in re.finditer(r'data:image/png;base64,([A-Za-z0-9+/=]{20000,})', html):
        b64 = m.group(1)
        if b64 not in [o[0] for o in olds]:
            raw = base64.b64decode(b64)
            w, h = struct.unpack(">II", raw[16:24])
            olds.append((b64, w, h, raw))

    if not olds:
        sys.exit("未找到需要替换的内联二维码")

    for b64, w, h, raw in olds:
        if (w, h) != (200, 295):
            sys.exit(f"发现非预期的内联大图 {w}x{h}，人工确认后再跑")
        cnt = html.count("data:image/png;base64," + b64)
        html = html.replace("data:image/png;base64," + b64, new_src)
        print(f"替换 {w}x{h} 内联图 ×{cnt} → 360x360 正方形二维码")

    # 容器补 object-fit，任何情况下都不再拉伸；尺寸略放大以便扫码
    css_old = ".hook-qr{width:70px;height:70px;border-radius:8px;background:#fff;border:1px solid #fff;flex:none;}"
    css_new = (".hook-qr{width:76px;height:76px;border-radius:8px;background:#fff;"
               "border:1px solid #fff;flex:none;object-fit:contain;}")
    assert html.count(css_old) == 1, "hook-qr 样式定位失败"
    html = html.replace(css_old, css_new)

    css_old2 = ".qr-box img{width:100%;height:100%;object-fit:contain;}"
    assert html.count(css_old2) == 1, "qr-box 样式定位失败"

    # 打标记，保证幂等
    html = html.replace("</head>", MARKER + "\n</head>", 1)

    open(HTML, "w", encoding="utf-8").write(html)

    total = len(html.encode("utf-8"))
    print(f"index.html 现有 {total/1024:.0f}KB")


if __name__ == "__main__":
    main()
