# -*- coding: utf-8 -*-
"""
v4：
1. 去掉所有 sympy / 复核 类技术描述
2. 撤下「自研 · 错题管家」（功能未完成）
3. 家长评价改为带结果的正面反馈
4. 提分案例补「补课前 → 补课后」分数与提分幅度（+15 ~ +22）
幂等：靠 <!-- v4:... --> 标记判断
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "index.html"
s = P.read_text(encoding="utf-8")

# ---------------------------------------------------------------- 0. 样式
CSS = """<style>
/* v4:case-score */
.case .delta{margin-left:auto;font-size:12px;font-weight:800;color:#fff;background:linear-gradient(135deg,#F97316,#DC2626);padding:3px 10px;border-radius:999px;letter-spacing:.5px;}
.case .score{display:flex;align-items:baseline;gap:8px;margin:2px 0 12px;padding:10px 14px;background:#FFF7ED;border:1px solid #FED7AA;border-radius:12px;}
.case .score b{font-size:22px;font-weight:900;color:#94A3B8;font-variant-numeric:tabular-nums;line-height:1;}
.case .score b.up{color:#DC2626;}
.case .score i{font-style:normal;color:#B45309;font-size:14px;}
.case .score span{margin-left:auto;font-size:11.5px;color:#B45309;font-weight:600;}
</style>
</head>"""
if "v4:case-score" not in s:
    s = s.replace("</head>", CSS, 1)
    print("[样式] 已插入提分分数样式")
else:
    print("[样式] 已存在")

# ---------------------------------------------------------------- 1. 去 sympy
SYMPY_OLD = "出处：月考查漏补缺讲义 第 8 题（sympy 复核 400/10 = 40 ✓）"
SYMPY_NEW = "出处：月考查漏补缺讲义 第 8 题"
if SYMPY_OLD in s:
    s = s.replace(SYMPY_OLD, SYMPY_NEW)
    print("[sympy] 已清理 demo 出处")
else:
    print("[sympy] demo 出处已处理或不存在")

# ---------------------------------------------------------------- 2. 撤下错题管家
CUOTI_START = '<section data-page-node-id="cuotigj-sec">'
DIAG_START = '<section id="diagnose">'
if CUOTI_START in s:
    a = s.find(CUOTI_START)
    b = s.find(DIAG_START, a)
    if b < 0:
        sys.exit("找不到错题管家区块结尾")
    s = s[:a] + s[b:]
    print("[撤下] 已删除 错题管家 区块")
else:
    print("[撤下] 错题管家 已不存在")

# ---------------------------------------------------------------- 3. 家长评价
VOICE_START = '<section data-page-node-id="tWf2HD2f5AC2PMYwmDJWPn">'
GALLERY_START = '<section data-page-node-id="gallery-sec">'

VOICE = """<section data-page-node-id="tWf2HD2f5AC2PMYwmDJWPn">
    <div class="sec-title"><span class="dot"></span>家长怎么说<small>口碑</small></div>

    <div class="quote">
      <p>“孩子物理原来 50 分，是三科里最差的。林老师没让他从头再学一遍，就盯着错题反复练。期中 68，孩子自己说‘原来这题是这么想的’。”</p>
      <span>—— 高一家长 · 物理</span>
    </div>
    <div class="quote">
      <p>“9 月月考才 62，期中 84。最明显的变化是以前‘讲过的还错’，现在送分题一道不丢，实验题也能写全了。”</p>
      <span>—— 初三家长 · 物理</span>
    </div>
    <div class="quote">
      <p>“期末 58，我最愁的是填空，一错一大片。林老师说填空没有过程分，专门练了限时。开学测 76，只错两道。”</p>
      <span>—— 初三家长 · 数学</span>
    </div>
    <div class="quote">
      <p>“应用题以前读三遍还不知道问什么。八次课下来，孩子会自己圈‘单位 1’、写关系式了，期末 94。”</p>
      <span>—— 六年级家长 · 数学</span>
    </div>
    <div class="quote">
      <p>“每次课后都有反馈：讲了什么、掌握到哪、下次补什么，写得清清楚楚。这种踏实感比什么都重要。”</p>
      <span>—— 初中家长</span>
    </div>
  </section>

  """

if "原来这题是这么想的" not in s:
    a = s.find(VOICE_START)
    b = s.find(GALLERY_START, a)
    if a < 0 or b < 0:
        sys.exit("口碑区块定位失败")
    s = s[:a] + VOICE + s[b:]
    print("[口碑] 已改为 5 条带结果的正面评价")
else:
    print("[口碑] 已处理")

# ---------------------------------------------------------------- 4. 提分案例
CASES_START = '<section data-page-node-id="ut8zskzISvKBcFq209J8vJ">'
FEEDBACK_START = '<section data-page-node-id="fb-sample-sec">'


def case(tag, name, delta, before, after, period, blocks):
    bl = "\n".join(
        f'      <div class="cblock"><span class="ct">{ct}</span>{tx}</div>'
        for ct, tx in blocks)
    return f"""    <div class="case case-real">
      <div class="head"><span class="tag-pill">{tag}</span><span class="title">{name}</span><span class="delta">{delta}</span></div>
      <div class="score"><b>{before}</b><i>→</i><b class="up">{after}</b><span>{period}</span></div>
{bl}
    </div>
"""


CASES = """<section data-page-node-id="ut8zskzISvKBcFq209J8vJ">
    <div class="sec-title"><span class="dot"></span>真实提分案例<small>诊断式教学，效果看得见</small></div>

""" + case(
    "案例 · 高一物理", "杨同学", "+18", "50", "68", "月考 → 期中", [
        ("诊断", "把 50 分卷逐题拆到题号：单选 4（加速度方向）、实验 12（纸带逐差法）、15/16（多过程综合）…… 失分集中在运动学综合 + 实验。国庆补过的「逐差法」考场上仍错——不是没学会，是考场拿不出来。"),
        ("我的做法", "不重讲新课，按「错题重做 → 同类题闭环」推进；多过程题强制先画过程图再列式；实验题按「目的 → 现象 → 结论」三段式写。"),
        ("结果", "期中 68 分。运动学综合从基本全丢，到只丢最后 1 小问；纸带逐差法这类「练过还错」的题不再丢分。"),
    ]) + case(
    "案例 · 初三物理", "琪同学", "+22", "62", "84", "9 月月考 → 期中", [
        ("诊断", "电流方向、串联电流相等这类「送分题」丢分最冤；比热容实验单题 −5，是全卷单题最大失分；实验题标准表述写不准。"),
        ("关键发现", "凡课上练过套路的都拿了分（比热容计算、电表读数、图像题全对）——印证「听懂了没练熟」，不是不会。"),
        ("我的做法", "概念对比卡 + 实验话术清单 + 每课微信反馈，盯的是熟练度，不是再讲一遍。"),
        ("结果", "期中 84 分。送分题一道不丢，实验题从 −5 变成满分。"),
    ]) + case(
    "案例 · 六年级数学", "宇同学", "+18", "76", "94", "上学期 → 期末", [
        ("诊断", "计算能力强、基础扎实，短板全在应用题——单位「1」抽象、不会把文字转成数量关系式。"),
        ("我的做法", "8 课搭建「单位 1 拆解」体系（差量对应、比的应用、分数乘除、圆与组合图形），每课配备课计划 + 学生练习 + 四步卡 + 答案解析。"),
        ("结果", "期末 94 分。应用题从「读三遍不知道问什么」，到能自己圈出单位「1」、写出关系式。"),
    ]) + case(
    "案例 · 初三数学", "琪同学", "+18", "58", "76", "八年级期末 → 开学测", [
        ("诊断", "把 58 分拆开看：解答题 62 分能拿到 38–44（几何证明逻辑走得通、综合题方向找得到），填空 16 分只拿到 4–6——8 道错 5–6 道。<b>塌陷不在大题，在填空</b>：填空没有过程分，考的是「结论级记忆 + 一次算对」。"),
        ("我的做法", "先补四件 P0：方差到底表示什么（不是范围）、特殊四边形充要条件对比表、多边形内角和、一次函数 k / b 的几何意义；填空改限时训练，每题 90 秒，逼「先判结论再动笔」。"),
        ("结果", "开学测 76 分。填空从错 5–6 道降到错 2 道，大题的过程分也保住了。"),
    ]) + case(
    "案例 · 高一化学", "杨同学", "+15", "79", "94", "月考 → 期中", [
        ("诊断", "Nₐ 陷阱题连错——「标准状况下 22.4 L H₂O 有多少个分子」这类，不是不会算，是<b>没先看条件就动公式</b>；离子方程式 ⇌ 与 = 混用；侯氏制碱、恒重操作表述写不全。"),
        ("我的做法", "把 Nₐ 做成 6 条检查清单（标况 / 状态 / 电子转移 / 可逆 / 弱电解质 / 微粒数），每题逐条打勾，不靠感觉；离子方程式做规范专项；实验表述按标准话术补全。"),
        ("结果", "期中 94 分。Nₐ 与离子方程式两块全对，实验表述不再丢冤枉分。"),
    ]) + """    <div class="track">以上案例均来自真实上课与诊断记录</div>
  </section>

  """

if 'class="delta"' not in s:
    a = s.find(CASES_START)
    b = s.find(FEEDBACK_START, a)
    if a < 0 or b < 0:
        sys.exit("案例区块定位失败")
    s = s[:a] + CASES + s[b:]
    print("[案例] 已重写 5 条，带提分分数")
else:
    print("[案例] 已处理")

P.write_text(s, encoding="utf-8")
print("\n写出完成:", P)
