# -*- coding: utf-8 -*-
"""
v5：家长评价换成真实微信原话（3 条）+ 保留 2 条原有评价
真实原话来源：2026-10-29 用户提供的微信截图 3 张
"""
import sys
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "index.html"
s = P.read_text(encoding="utf-8")

# ---------------------------------------------------------------- 样式
CSS = """<style>
/* v5:wx */
.quote .wx{display:inline-block;margin-left:8px;font-size:10.5px;font-weight:700;color:#15803D;background:#DCFCE7;border-radius:999px;padding:1px 8px;vertical-align:1px;letter-spacing:.3px;}
</style>
</head>"""
if "v5:wx" not in s:
    s = s.replace("</head>", CSS, 1)
    print("[样式] 已加微信原话标记")

VOICE_START = '<section data-page-node-id="tWf2HD2f5AC2PMYwmDJWPn">'
GALLERY_START = '<section data-page-node-id="gallery-sec">'

VOICE = """<section data-page-node-id="tWf2HD2f5AC2PMYwmDJWPn">
    <div class="sec-title"><span class="dot"></span>家长怎么说<small>微信原话</small></div>

    <div class="quote">
      <p>“听了你三节课，学校考了两次试，他现在很喜欢物理。”</p>
      <span>—— 高一家长 · 物理<span class="wx">微信原话</span></span>
    </div>
    <div class="quote">
      <p>“您教的很好，不想给她换老师。我这还有朋友，也推荐给他们。”</p>
      <span>—— 初三家长 · 物理<span class="wx">微信原话</span></span>
    </div>
    <div class="quote">
      <p>“周末还有空吗？弟弟需要补物理化学。”</p>
      <span>—— 老学员家长 · 转介绍<span class="wx">微信原话</span></span>
    </div>
    <div class="quote">
      <p>“讲课思路清晰，方法实用，孩子说听懂了、会做了，这才是最重要的。”</p>
      <span>—— 六年级家长 · 数学</span>
    </div>
    <div class="quote">
      <p>“非常负责任，每次课后都有反馈，孩子在他指导下进步很大！”</p>
      <span>—— 初中家长</span>
    </div>
  </section>

  """

if "听了你三节课" not in s:
    a = s.find(VOICE_START)
    b = s.find(GALLERY_START, a)
    if a < 0 or b < 0:
        sys.exit("口碑区块定位失败")
    s = s[:a] + VOICE + s[b:]
    print("[口碑] 已换成 3 条真实微信原话 + 2 条原有评价")
else:
    print("[口碑] 已处理")

P.write_text(s, encoding="utf-8")
print("写出完成")
