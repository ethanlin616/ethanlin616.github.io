#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 4 张微信分享封面（1200x630）：www / math / physics / chemistry
字体：华文黑体（STHeiti Medium / Light），动态累加 y 防重叠。
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "src" / "assets"
W, H = 1200, 630
MED = "/System/Library/Fonts/STHeiti Medium.ttc"
LGT = "/System/Library/Fonts/STHeiti Light.ttc"

COVERS = {
    "cover-www.png": {
        "badge": "林老师 · 北京一对一提分",
        "title": "小学数学 · 初中数物化 · 高中物理",
        "title_size": 58,
        "sub": "先诊断后上课 · 每次课后有反馈 · 错题有跟踪",
        "foot": "清华大学 3 年联合培养 · 硕士　|　4 年一线提分经验　|　家长续费率 90%",
        "url": "ethanlin616.github.io",
    },
    "cover-math.png": {
        "badge": "数学专页 · 小学 + 初中",
        "title": "把“听得懂”变成“做得对”",
        "title_size": 64,
        "sub": "应用题读题方法 · 几何辅助线思路 · 函数数形结合",
        "foot": "清华大学 3 年联合培养 · 硕士　|　首次试听半价",
        "url": "ethanlin616.github.io/math",
    },
    "cover-physics.png": {
        "badge": "物理专页 · 初中 + 高中",
        "title": "先分析过程，再套公式",
        "title_size": 64,
        "sub": "受力分析四步 · 电学动态电路 · 实验探究踩分点",
        "foot": "清华大学 3 年联合培养 · 硕士　|　首次试听半价",
        "url": "ethanlin616.github.io/physics",
    },
    "cover-chemistry.png": {
        "badge": "化学专页 · 初中",
        "title": "不靠背，靠推导",
        "title_size": 64,
        "sub": "化合价推化学式 · 反应类型推方程式 · 酸碱盐知识网络",
        "foot": "清华大学 3 年联合培养 · 硕士　|　首次试听半价",
        "url": "ethanlin616.github.io/chemistry",
    },
}


def gradient():
    c1 = np.array([30, 58, 138], dtype=float)
    c2 = np.array([37, 99, 235], dtype=float)
    c3 = np.array([14, 165, 233], dtype=float)
    y, x = np.mgrid[0:H, 0:W]
    t = (x / W * 0.55 + y / H * 0.45)
    arr = np.zeros((H, W, 3))
    for ch in range(3):
        arr[:, :, ch] = np.where(
            t < 0.6,
            c1[ch] + (c2[ch] - c1[ch]) * (t / 0.6),
            c2[ch] + (c3[ch] - c2[ch]) * ((t - 0.6) / 0.4),
        )
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGB")


def fit_font(text, path, size, max_w, min_size=22):
    """按最大宽度自动缩小字号"""
    while size > min_size:
        f = ImageFont.truetype(path, size)
        bb = ImageFont.truetype(path, size).getbbox(text)
        if bb[2] - bb[0] <= max_w:
            return f
        size -= 2
    return ImageFont.truetype(path, min_size)


def draw_cover(cfg, out):
    img = gradient().convert("RGBA")
    ov = Image.new("RGBA", img.size, (255, 255, 255, 0))
    d = ImageDraw.Draw(ov)

    x = 80
    maxw = W - x * 2

    f_badge = ImageFont.truetype(MED, 28)
    f_title = fit_font(cfg["title"], MED, cfg["title_size"], maxw, 40)
    f_sub = fit_font(cfg["sub"], LGT, 34, maxw, 22)
    f_foot = fit_font(cfg["foot"], LGT, 27, maxw, 18)
    f_url = ImageFont.truetype(LGT, 24)

    y = 84

    # 胶囊标签
    bb = d.textbbox((0, 0), cfg["badge"], font=f_badge)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad_x, pad_y = 22, 12
    d.rounded_rectangle([x, y, x + tw + pad_x * 2, y + th + pad_y * 2 + 6],
                        radius=(th + pad_y * 2 + 6) // 2, fill=(255, 255, 255, 46))
    d.text((x + pad_x, y + pad_y + 1), cfg["badge"], font=f_badge, fill=(255, 255, 255, 245))
    y += th + pad_y * 2 + 6 + 46

    # 主标题
    bb = d.textbbox((0, 0), cfg["title"], font=f_title)
    d.text((x, y - bb[1]), cfg["title"], font=f_title, fill=(255, 255, 255, 255))
    y += (bb[3] - bb[1]) + 40

    # 分割线
    d.rectangle([x, y, x + 96, y + 4], fill=(255, 255, 255, 150))
    y += 30

    # 副标题
    bb = d.textbbox((0, 0), cfg["sub"], font=f_sub)
    d.text((x, y - bb[1]), cfg["sub"], font=f_sub, fill=(255, 255, 255, 232))
    y += (bb[3] - bb[1]) + 34

    # 底部信息
    d.text((x, H - 108), cfg["foot"], font=f_foot, fill=(255, 255, 255, 225))
    # 右下角网址
    bb = d.textbbox((0, 0), cfg["url"], font=f_url)
    d.text((W - 80 - (bb[2] - bb[0]), H - 66), cfg["url"], font=f_url, fill=(255, 255, 255, 190))

    img = Image.alpha_composite(img, ov).convert("RGB")
    img.save(out, quality=95)
    print(f"[ok] {out.name}  {img.size}")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for name, cfg in COVERS.items():
        draw_cover(cfg, ASSETS / name)
    # 主域封面同步到仓库根，替换旧 cover.png
    import shutil
    shutil.copy2(ASSETS / "cover-www.png", ROOT / "cover.png")
    print("[ok] cover.png 已更新")


if __name__ == "__main__":
    main()
