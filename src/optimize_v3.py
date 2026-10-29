# -*- coding: utf-8 -*-
"""
v3：主页结构调整 + 措辞去元话术 + 案例/口碑补学段
可重复执行：已重排过则跳过重排（靠 <!-- v3:order --> 标记判断）
"""
import sys
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "index.html"
s = P.read_text(encoding="utf-8")

# ---------------------------------------------------------------- 1. 去元话术
REPL = [
    ("三道题均出自真实讲义 · 学生姓名与学校已脱敏",
     "三道题均出自真实讲义与课堂记录"),
    ("诊断报告长什么样<small>真实节选 · 已脱敏</small>",
     "诊断报告长什么样<small>真实节选</small>"),
    ("课后反馈示例<small>每课向家长同步，脱敏展示</small>",
     "课后反馈示例<small>每课向家长同步</small>"),
    ("以上案例均来自真实上课与诊断记录，姓名与地区已脱敏展示",
     "以上案例均来自真实上课与诊断记录"),
]
for old, new in REPL:
    if old in s:
        s = s.replace(old, new)
        print("[措辞] 替换:", old[:24])
    elif new in s:
        print("[措辞] 已处理:", new[:24])
    else:
        print("[措辞] !! 未找到:", old[:24])

# ---------------------------------------------------------------- 2. 口碑补高中
VOICE_ANCHOR = '<small data-page-node-id="roL6N7hQpRpdtUwVJd3yQG">口碑</small></div>'
NEW_QUOTES = VOICE_ANCHOR + """
    <div class="quote">
      <p>“孩子物理一直 50 分上下，我们本来打算让他从头再学一遍。林老师把试卷逐题拆给我们看，说丢的分大半是学过、考场上没拿出来——重学一遍还是这个结果。”</p>
      <span>—— 高一家长 · 物理</span>
    </div>
    <div class="quote">
      <p>“后边大题有的都对，而填空错。”</p>
      <span>—— 初二家长 · 数学（试课前沟通原话）</span>
    </div>"""

if "高一家长 · 物理" not in s:
    if VOICE_ANCHOR in s:
        s = s.replace(VOICE_ANCHOR, NEW_QUOTES, 1)
        print("[口碑] 已插入高中家长 + 初中数学家长原话")
    else:
        sys.exit("找不到口碑区块锚点")
else:
    print("[口碑] 已存在，跳过")

# 给原有三条补上学段/科目标签
ATTR = [
    (">—— 初三家长</span>", ">—— 初三家长 · 物理</span>"),
    (">—— 小学家长</span>", ">—— 六年级家长 · 数学</span>"),
    (">—— 初中家长</span>", ">—— 初三家长</span>"),
]
for old, new in ATTR:
    if old in s:
        s = s.replace(old, new, 1)
        print("[口碑] 标注:", new)

# ---------------------------------------------------------------- 3. 案例补初中数学 / 化学
CASE_ANCHOR = '<div class="track">以上案例均来自真实上课与诊断记录</div>'
NEW_CASES = """    <div class="case case-real">
      <div class="head"><span class="tag-pill">案例 · 初三数学</span><span class="title">琪同学（数学）</span></div>
      <div class="cmeta">八年级期末数学 <b class="lo">58</b> / 100 · 家长原话：「后边大题有的都对，而填空错」</div>
      <div class="cblock"><span class="ct">诊断</span>把 58 分拆开看：解答题 62 分能拿到 38–44（几何证明逻辑走得通、综合题方向找得到），填空 16 分只拿到 4–6——8 道错 5–6 道。<b>塌陷不在大题，在填空</b>：填空没有过程分，考的是「结论级记忆 + 一次算对」，而这恰恰是没练过的地方。</div>
      <div class="cblock"><span class="ct">我的做法</span>先补四件 P0：方差到底表示什么（不是范围）、特殊四边形充要条件对比表、多边形内角和、一次函数 k / b 的几何意义；填空改限时训练，每题 90 秒，逼「先判结论再动笔」；大题不放松，几何证明按拆分路线图写步骤，保住过程分。</div>
      <div class="cblock"><span class="ct">配套</span>四步卡 + 公式速查卡 + 每周微信反馈（哪类填空还在错，下次课先补哪块）。</div>
    </div>

    <div class="case case-real">
      <div class="head"><span class="tag-pill">案例 · 高一化学</span><span class="title">杨同学（化学）</span></div>
      <div class="cmeta">高一阶段性测试化学 79 分 · 三科里最稳的一科，但错得很集中</div>
      <div class="cblock"><span class="ct">诊断</span>Nₐ 陷阱题连错——「标准状况下 22.4 L H₂O 有多少个分子」这类，不是不会算，是<b>没先看条件就动公式</b>；离子方程式 ⇌ 与 = 混用；侯氏制碱先通 NH₃ 后通 CO₂ 的原因、恒重操作，表述写不全。</div>
      <div class="cblock"><span class="ct">我的做法</span>把 Nₐ 做成 6 条检查清单（标况 / 状态 / 电子转移 / 可逆 / 弱电解质 / 微粒数），每题逐条打勾，不靠感觉；离子方程式做规范专项；实验表述按标准话术补全，该写的沉淀、气体符号一个不漏。</div>
      <div class="cblock"><span class="ct">配套</span>化学方法思路笔记 + 酸碱盐知识网络图 + 苏教版专题讲义。</div>
    </div>

""" + CASE_ANCHOR

if "案例 · 初三数学" not in s:
    if CASE_ANCHOR in s:
        s = s.replace(CASE_ANCHOR, NEW_CASES, 1)
        print("[案例] 已插入初中数学 + 高一化学")
    else:
        sys.exit("找不到案例区块尾部锚点")
else:
    print("[案例] 已存在，跳过")

# ---------------------------------------------------------------- 4. 顶层区块重排
STARTS = {
    "hero": '<header class="hero"',
    "quick": '<div class="quick-bar"',
    "thesis": '<div class="thesis">',
    "pain": '<section data-page-node-id="9e2RbJLEXMHpiO2qgtylNg">',
    "demo": '<section id="demo">',
    "hook1": '<div class="hook-card" data-page-node-id="AmeXv3Rnsy8',
    "change": '<section data-page-node-id="D6ksySZowuPeH7J1sn2g8I">',
    "way": '<section data-page-node-id="HaLqXmvr8n9tRdbssaiQ3F">',
    "subjects": '<section>\n    <div class="sec-title"><span class="dot"></span>按科目看课程',
    "price": '<section data-page-node-id="klEhi56czevUj1YdySW43T">',
    "loop": '<section data-page-node-id="XmxiTSa1fagGxpURgsExWj">',
    "deliver": '<section id="deliver">',
    "diag": '<section id="diagnose">',
    "feedback": '<section data-page-node-id="fb-sample-sec">',
    "portrait": '<section id="portrait">',
    "cases": '<section data-page-node-id="ut8zskzISvKBcFq209J8vJ">',
    "notdo": '<section id="notdo">',
    "scarcity": '<div class="hook-card scarcity"',
    "honor": '<section data-page-node-id="Gof3ulyAzks88dmL1IkzFg">',
    "voice": '<section data-page-node-id="tWf2HD2f5AC2PMYwmDJWPn">',
    "gallery": '<section data-page-node-id="gallery-sec">',
    "cuoti": '<section data-page-node-id="cuotigj-sec">',
    "wb": '<section class="wb-intro"',
    "qr": '<div class="qr-card" id="contact"',
    "footer": '<footer',
}

# 新顺序：先讲怎么教、交付什么，再给证据与口碑，课程与价格收尾
ORDER = [
    "hero", "quick", "thesis", "pain", "demo",
    "change", "loop", "deliver", "cuoti", "diag",
    "portrait", "cases", "feedback", "voice", "gallery",
    "honor", "notdo", "hook1",
    "subjects", "way", "price", "scarcity", "wb", "qr", "footer",
]

if "<!-- v3:order -->" in s:
    print("[重排] 已重排过，跳过")
else:
    pos = {}
    for k, v in STARTS.items():
        c = s.count(v)
        if c != 1:
            sys.exit("区块标记出现 %d 次，应为 1 次: %s" % (c, k))
        pos[k] = s.find(v)

    seq = sorted(pos, key=lambda k: pos[k])
    slices = {}
    for i, k in enumerate(seq):
        st = pos[k]
        en = pos[seq[i + 1]] if i + 1 < len(seq) else len(s)
        slices[k] = s[st:en]

    if set(ORDER) != set(seq):
        sys.exit("区块集合不一致: %s" % (set(ORDER) ^ set(seq)))

    s = s[:pos["hero"]] + "  <!-- v3:order -->\n" + "".join(slices[k] for k in ORDER)
    print("[重排] 完成，新顺序：")
    for n in ORDER:
        print("   ", n)

P.write_text(s, encoding="utf-8")
print("\n写出完成:", P)
