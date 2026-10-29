# -*- coding: utf-8 -*-
"""
根据 gallery/manifest.json 重新生成主页「讲义与知识图谱」区块。

用法：
    python3 src/build_gallery.py

新增一张图：
    1. 把图片放进 gallery/
    2. 在 gallery/manifest.json 的 items 里加一条（pick=true 才会显示）
    3. 跑本脚本

脚本只改 index.html 里 gallery-sec 这一个 section，其他内容不动。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
MANIFEST = ROOT / "gallery" / "manifest.json"
GALLERY_DIR = ROOT / "gallery"

data = json.loads(MANIFEST.read_text(encoding="utf-8"))
items = [it for it in data["items"] if it.get("pick")]
items.sort(key=lambda x: x.get("order", 999))

if not items:
    sys.exit("manifest 里没有 pick=true 的条目")

missing = [it["file"] for it in items if not (GALLERY_DIR / it["file"]).exists()]
if missing:
    sys.exit("以下图片不存在：\n  " + "\n  ".join(missing))

cards = []
for it in items:
    stage = it.get("stage", "")
    label = f'{it["title"]} · {stage}' if stage else it["title"]
    alt = f'{it["title"]}知识图谱'
    cards.append(
        f'      <div class="gimg"><img src="gallery/{it["file"]}" alt="{alt}" loading="lazy">'
        f'<span>{label}</span></div>')

SECTION = """  <section data-page-node-id="gallery-sec">
    <div class="sec-title"><span class="dot"></span>讲义与知识图谱<small>按你孩子的教材版本备课</small></div>
    <div class="gallery">
""" + "\n".join(cards) + """
    </div>
    <div class="track">以上为节选 · 共 74 张知识图谱，覆盖初中电学 / 内能 / 高中必修一·二</div>
  </section>
"""

s = INDEX.read_text(encoding="utf-8")

# 定位 gallery 区块：从它的 <section 开始，按标签配对找到对应的 </section>
anchor = s.find('<section data-page-node-id="gallery-sec">')
if anchor < 0:
    sys.exit("找不到 gallery-sec 区块")

i, depth = anchor, 0
while True:
    nxt_open = s.find("<section", i + 1)
    nxt_close = s.find("</section>", i + 1)
    if nxt_close < 0:
        sys.exit("section 标签不闭合")
    if nxt_open != -1 and nxt_open < nxt_close:
        depth += 1
        i = nxt_open
    else:
        if depth == 0:
            end = nxt_close + len("</section>")
            break
        depth -= 1
        i = nxt_close

s = s[:anchor] + SECTION + s[end:]

# 三列改两列：缩略图 150px 太窄，中文讲义看不出结构
OLD_GRID = ".gallery{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;}"
NEW_GRID = "/* v6:gallery-2col */\n.gallery{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;}"
if OLD_GRID in s:
    s = s.replace(OLD_GRID, NEW_GRID, 1)
    print("[布局] 图谱网格 3 列 → 2 列")
elif "v6:gallery-2col" in s:
    print("[布局] 已是 2 列")
else:
    print("[布局] !! 未找到网格样式，请手动确认")

INDEX.write_text(s, encoding="utf-8")
print(f"[完成] 已写入 {len(items)} 张：")
for it in items:
    print("   ", it["order"], it["file"], "·", it["title"])
