# -*- coding: utf-8 -*-
"""主域 index.html 内容优化 v2 —— 从「描述教学」到「展示教学」

幂等：所有插入块带 <!-- v2:xxx --> 标记，重复执行不会重复插入。
用法：python3 src/optimize_v2.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "index.html"
s = P.read_text(encoding="utf-8")
orig_len = len(s)

# ============================================================
# 1. CSS
# ============================================================
CSS = """
  /* ===== v2：现场感组件（2026-10-29） ===== */
  .thesis{margin:22px 22px 0;background:linear-gradient(150deg,#0E2C57,#0B4E9E);color:#fff;border-radius:20px;padding:24px 22px;box-shadow:0 14px 34px rgba(11,78,158,.26);}
  .thesis b{display:block;font-size:19px;font-weight:800;letter-spacing:-.3px;margin-bottom:9px;line-height:1.45;}
  .thesis p{font-size:13.5px;line-height:1.85;opacity:.93;}
  .thesis em{font-style:normal;color:#FFD08A;font-weight:800;}

  .lead{font-size:13px;color:var(--muted);margin:-6px 0 18px;line-height:1.8;}

  .demo{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:20px;margin-bottom:14px;box-shadow:0 2px 14px rgba(0,0,0,.04);}
  .demo .dtag{display:inline-block;font-size:11.5px;font-weight:800;color:#fff;background:linear-gradient(135deg,var(--c1),var(--c2));padding:3px 11px;border-radius:999px;margin-bottom:12px;letter-spacing:.2px;}
  .demo .q{font-size:14.5px;font-weight:700;line-height:1.7;color:var(--ink);padding:12px 14px;background:#F5F7FA;border-radius:12px;border-left:3px solid var(--c1);}
  .demo .wrong{margin-top:11px;font-size:13px;line-height:1.75;color:#B42318;background:#FEF3F2;border:1px solid #FECDCA;border-radius:12px;padding:12px 14px;}
  .demo .wrong b{color:#912018;}
  .demo ol{margin-top:12px;}
  .demo ol li{list-style:none;position:relative;padding-left:26px;font-size:13px;line-height:1.75;color:var(--ink);margin-bottom:8px;}
  .demo ol li:last-child{margin-bottom:0;}
  .demo ol li::before{counter-increment:d;content:counter(d);position:absolute;left:0;top:3px;width:18px;height:18px;border-radius:50%;background:rgba(0,113,227,.12);color:var(--c1);font-size:11px;font-weight:800;text-align:center;line-height:18px;}
  .demo ol{counter-reset:d;}
  .demo ol li b{color:var(--c1);}
  .demo .key{margin-top:13px;font-size:13.5px;font-weight:800;color:#7C2D12;background:linear-gradient(135deg,#FFF7ED,#FFEDD5);border:1px solid #FED7AA;border-radius:12px;padding:11px 14px;line-height:1.6;}
  .demo .key::before{content:"口诀 · ";font-size:11px;color:#B45309;letter-spacing:1px;}
  .demo .src{margin-top:9px;font-size:11.5px;color:#A1A1AA;line-height:1.6;}

  .tablebox{overflow-x:auto;border:1px solid var(--line);border-radius:16px;background:var(--card);}
  .dtable{width:100%;border-collapse:collapse;font-size:12.5px;min-width:340px;}
  .dtable th{background:#EFF6FF;color:#0B4E9E;font-weight:800;text-align:left;padding:10px 9px;font-size:11.5px;letter-spacing:.3px;white-space:nowrap;}
  .dtable td{padding:10px 9px;border-top:1px solid var(--line);color:var(--ink);line-height:1.55;vertical-align:top;}
  .dtable td.no{font-weight:800;color:var(--c1);white-space:nowrap;}
  .dtable td.lo{font-weight:800;color:#B42318;text-align:right;white-space:nowrap;}
  .concl{margin-top:14px;background:#F0FDF4;border:1px solid #BBF7D0;border-radius:14px;padding:14px 16px;font-size:13px;line-height:1.8;color:#14532D;}
  .concl b{color:#166534;}

  .deliver{display:grid;grid-template-columns:1fr 1fr;gap:10px;}
  .dv{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:15px 14px;}
  .dv .n{font-size:11px;font-weight:800;color:var(--c1);opacity:.55;letter-spacing:1.2px;}
  .dv h4{font-size:14px;font-weight:800;margin:3px 0 5px;letter-spacing:-.2px;}
  .dv p{font-size:12px;color:var(--muted);line-height:1.62;}

  .pf{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px;margin-bottom:12px;box-shadow:0 2px 14px rgba(0,0,0,.04);}
  .pf .ph{display:flex;align-items:center;gap:9px;margin-bottom:10px;}
  .pf .pt{font-size:11.5px;font-weight:800;color:#fff;background:#1D1D1F;padding:3px 10px;border-radius:999px;letter-spacing:.5px;}
  .pf .pn{font-size:15.5px;font-weight:800;letter-spacing:-.2px;}
  .pf .pd{font-size:13px;line-height:1.75;color:var(--ink);}
  .pf .pd .lb{display:inline-block;font-size:11px;font-weight:800;color:var(--c1);background:rgba(0,113,227,.08);padding:1px 7px;border-radius:6px;margin-right:6px;}
  .pf .act{margin-top:10px;padding-top:10px;border-top:1px dashed var(--line);font-size:12.5px;color:var(--muted);line-height:1.75;}
  .pf .act b{color:var(--ink);}
  .pf .act .hi{color:var(--accent);font-weight:800;}

  .notdo{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:6px 20px;box-shadow:0 2px 14px rgba(0,0,0,.04);}
  .notdo .ni{padding:16px 0;border-bottom:1px solid var(--line);}
  .notdo .ni:last-child{border-bottom:none;}
  .notdo .ni h4{font-size:14.5px;font-weight:800;margin-bottom:5px;color:var(--ink);}
  .notdo .ni h4::before{content:"\\00D7";color:#B42318;font-weight:800;margin-right:8px;}
  .notdo .ni p{font-size:12.5px;color:var(--muted);line-height:1.75;}
  .notdo .ni p b{color:var(--ink);}

  @media (max-width:420px){
    .thesis{margin:18px 18px 0;padding:20px 18px;}
    .thesis b{font-size:17px;}
    .deliver{grid-template-columns:1fr;}
    .demo{padding:17px;}
  }
"""
if "/* ===== v2：现场感组件" not in s:
    s = s.replace("</style>", CSS + "\n</style>", 1)

# ============================================================
# 2. Hero 副标题 + 数据条
# ============================================================
s = re.sub(r'(<div class="sub"[^>]*>).*?(</div>)',
           r'\g<1>「听懂」到「会做」，差的是练法\g<2>', s, count=1)

for old, new in [
    ('<b[^>]*>3 年</b><span[^>]*>清华联合培养</span>', '<b>65 张</b><span>自绘讲义图</span>'),
    ('<b[^>]*>4 年</b><span[^>]*>一线提分经验</span>', '<b>6 份</b><span>每课材料</span>'),
    ('<b[^>]*>数学·理化</b><span[^>]*>三科精讲</span>', '<b>74 张</b><span>知识图谱</span>'),
]:
    s = re.sub(old, new, s, count=1)

# 图谱数量口径同步
s = s.replace("共 40+ 张知识图谱", "共 74 张知识图谱")

# ============================================================
# 3. 论点条（hero 之后）
# ============================================================
THESIS = """  <!-- v2:thesis -->
  <div class="thesis">
    <b>90% 的补课，停在「听懂」这一步。</b>
    <p>孩子点头、家长放心、考试照错。我做的事很窄：把<em>已经听懂的东西</em>，练到考场上能自己拿出来。</p>
  </div>

"""
if "<!-- v2:thesis -->" not in s:
    anchor = '  <section data-page-node-id="9e2RbJLEXMHpiO2qgtylNg">'
    if anchor not in s:
        sys.exit("找不到痛点区块锚点")
    s = s.replace(anchor, THESIS + anchor, 1)

# ============================================================
# 4. 一道题，看我怎么教
# ============================================================
DEMO = """  <!-- v2:demo -->
  <section id="demo">
    <div class="sec-title"><span class="dot"></span>一道题，看我怎么教<small>真题 · 真错法 · 真口诀</small></div>
    <p class="lead">不用听我讲方法多好。下面三道题，你先看学生怎么错，再看我怎么判——看完你就知道差别在哪。</p>

    <div class="demo">
      <span class="dtag">物理 · 高一 · 刹车陷阱</span>
      <div class="q">汽车以 20 m/s 行驶，刹车加速度大小 5 m/s²，求 10 s 内的位移。</div>
      <div class="wrong"><b>多数学生会这样错：</b>直接代 x = v₀t + ½at² = 20×10 − 2.5×100 = <b>−50 m</b>。算出个负数，也不知道错在哪。</div>
      <ol>
        <li>先算它什么时候停：t<sub>停</sub> = v₀/|a| = 20/5 = <b>4 s</b></li>
        <li>4 s &lt; 10 s → 车 4 秒就停了，后 6 秒位移是 0，不能按 10 秒算</li>
        <li>用 x = v₀²/(2|a|) = 400/10 = <b>40 m</b></li>
      </ol>
      <div class="key">先问「它停了吗」，再问「走了多远」</div>
      <div class="src">出处：月考查漏补缺讲义 第 8 题（sympy 复核 400/10 = 40 ✓）</div>
    </div>

    <div class="demo">
      <span class="dtag">物理 · 高一 · 摩擦力</span>
      <div class="q">重 100 N 的箱子放在水平桌面，动摩擦因数 μ = 0.2，用 10 N 的水平力拉它，摩擦力多大？</div>
      <div class="wrong"><b>多数学生会这样错：</b>f = μF<sub>N</sub> = 0.2 × 100 = <b>20 N</b>。公式没错，但用错了地方——箱子根本没动。</div>
      <ol>
        <li>先算最大静摩擦：f<sub>max</sub> ≈ μF<sub>N</sub> = 20 N</li>
        <li>10 N &lt; 20 N → 拉不动，箱子静止，这是静摩擦，不是滑动摩擦</li>
        <li>静摩擦「要多少给多少」→ f = <b>10 N</b></li>
      </ol>
      <div class="key">先判状态，再定方向，最后算大小</div>
      <div class="src">出处：第 04–06 讲 能力进阶 · 方法思路笔记 第二章</div>
    </div>

    <div class="demo">
      <span class="dtag">数学 · 六年级 · 单位「1」</span>
      <div class="q">一本书 120 页，读了 1/4，还剩多少页？</div>
      <div class="wrong"><b>多数学生会这样错：</b>120 × 1/4 = 30，答「还剩 30 页」。算得没错，但答的是「读了多少」。</div>
      <ol>
        <li>圈出分率句：1/4</li>
        <li>「的」字前面是单位「1」→ 全书 120 页</li>
        <li>写关系式：剩下 = 120 × (1 − 1/4) = <b>90 页</b></li>
        <li>回代检验：读的 30 + 剩的 90 = 120 ✓</li>
      </ol>
      <div class="key">「的」前「比」后找标准；先写关系式，再算不迷糊</div>
      <div class="src">出处：六年级第 1 课《单位 1 与应用题拆解》四步卡</div>
    </div>

    <div class="track">三道题均出自真实讲义 · 学生姓名与学校已脱敏</div>
  </section>

"""
if "<!-- v2:demo -->" not in s:
    anchor = '  <div class="hook-card" data-page-node-id="AmeXv3Rnsy8li3DFV6ZHmX">'
    if anchor not in s:
        sys.exit("找不到免费资料 hook-card 锚点")
    s = s.replace(anchor, DEMO + anchor, 1)

# ============================================================
# 5. 一节课带走 6 样东西
# ============================================================
DELIVER = """  <!-- v2:deliver -->
  <section id="deliver">
    <div class="sec-title"><span class="dot"></span>一节课，带走 6 样东西<small>不是一张卷子</small></div>
    <p class="lead">上面那条闭环不是口号，它落成纸面就是下面这 6 份材料。每节课都有，全部留档。</p>
    <div class="deliver">
      <div class="dv"><div class="n">01</div><h4>备课计划</h4><p>这节课讲什么、讲到哪、留多少练习，开课前就定好。</p></div>
      <div class="dv"><div class="n">02</div><h4>上课讲义</h4><p>彩色图文，每个易错点配示意图——全站 65 张图都是自己画的。</p></div>
      <div class="dv"><div class="n">03</div><h4>学生练习</h4><p>分层设计：课上练一遍，课后带回去再做一遍。</p></div>
      <div class="dv"><div class="n">04</div><h4>答案与解析</h4><p>每题给思路和易错提醒，不只给一个答案。</p></div>
      <div class="dv"><div class="n">05</div><h4>速查卡 / 四步卡</h4><p>一页纸装下一个专题的口诀和流程，考前能翻。</p></div>
      <div class="dv"><div class="n">06</div><h4>课后反馈</h4><p>当天微信发家长：讲了什么、掌握到哪、下次做什么。</p></div>
    </div>
    <div class="track">机构大班一节课给你一张卷子 · 这里一节课 6 份，全部留档</div>
  </section>

"""
if "<!-- v2:deliver -->" not in s:
    anchor = '      <section data-page-node-id="fb-sample-sec">'
    if anchor not in s:
        sys.exit("找不到课后反馈示例锚点")
    s = s.replace(anchor, DELIVER + anchor, 1)

# ============================================================
# 6. 诊断报告长什么样
# ============================================================
ROWS = [
    ("单选 4", "概念", "加速度方向与速度方向的关系判断错", "4"),
    ("实验 12", "实验", "纸带逐差法公式书写不规范", "8"),
    ("13", "解答", "追及相遇 / 多阶段运动，过程列式丢分", "4"),
    ("14", "解答", "多阶段运动，分段处理不严谨", "4"),
    ("15", "解答", "v-t 图像分段，斜率 / 面积应用不熟", "8"),
    ("16", "解答", "多过程综合压轴（滑块 + 斜面），思路混乱", "13"),
]
tr = "\n".join(
    f'        <tr><td class="no">{a}</td><td>{b}</td><td>{c}</td><td class="lo">−{d}</td></tr>'
    for a, b, c, d in ROWS)

DIAG = f"""  <!-- v2:diagnose -->
  <section id="diagnose">
    <div class="sec-title"><span class="dot"></span>诊断报告长什么样<small>真实节选 · 已脱敏</small></div>
    <p class="lead">别的诊断写「基础薄弱、需加强训练」。这份写的是——每一分丢在哪道题、为什么丢。</p>
    <div class="tablebox">
      <table class="dtable">
        <tr><th>题号</th><th>类型</th><th>可见问题</th><th style="text-align:right">失分</th></tr>
{tr}
      </table>
    </div>
    <div class="concl"><b>可见失分合计 41 分，实际得分 50。</b>六处失分指向同一个根因：运动学综合 + 实验。不是知识盲区，是「学过，考场上拿不出来」。</div>
    <div class="track">同一份诊断里三科一起拆：物理 50 / 化学 79 / 数学 121 · 先打头号短板</div>
  </section>

"""
if "<!-- v2:diagnose -->" not in s:
    # 紧跟「6 件套」之后：材料清单 → 诊断表实物 → 反馈原文，三块连成「交付物样例」
    anchor = '      <section data-page-node-id="fb-sample-sec">'
    if anchor not in s:
        sys.exit("找不到课后反馈示例锚点（诊断）")
    s = s.replace(anchor, DIAG + anchor, 1)

# ============================================================
# 7. 你家孩子是哪种
# ============================================================
PORTRAIT = """  <!-- v2:portrait -->
  <section id="portrait">
    <div class="sec-title"><span class="dot"></span>你家孩子是哪种<small>先对号，再看案例</small></div>
    <p class="lead">补课前我最想确认的不是分数，是类型。类型不同，补法完全相反。</p>

    <div class="pf">
      <div class="ph"><span class="pt">A 型</span><span class="pn">单科塌方</span></div>
      <div class="pd"><span class="lb">你会看到</span>某一科突然掉下去，其他科还行，孩子自己也说「不知道为什么会错」。</div>
      <div class="act"><b>真实案例：</b>杨同学 · 物理 50 / 化学 79 / 数学 121。<br><b>我的动作：</b><span class="hi">补考场提取，不补新课</span>——重做错题 + 同类题闭环，而不是把课本再讲一遍。</div>
    </div>

    <div class="pf">
      <div class="ph"><span class="pt">B 型</span><span class="pn">听懂就过</span></div>
      <div class="pd"><span class="lb">你会看到</span>上课点头、作业会写，一考就掉分；一问都说会，一看卷子全是「不该错的」。</div>
      <div class="act"><b>真实案例：</b>琪琪 · 初三物理，练过套路的题全对，概念辨析题连丢 4 道。<br><b>我的动作：</b><span class="hi">建练习闭环 + 话术清单</span>——把「听懂」按天拆成可检验的小动作。</div>
    </div>

    <div class="pf">
      <div class="ph"><span class="pt">C 型</span><span class="pn">算得快，读不懂</span></div>
      <div class="pd"><span class="lb">你会看到</span>计算又准又快，一碰应用题就卡；不是不会算，是不知道题目在问什么。</div>
      <div class="act"><b>真实案例：</b>小宇 · 六年级数学，卡在「单位 1」和数量关系式。<br><b>我的动作：</b><span class="hi">补「文字→关系式」的翻译</span>——四步卡固定流程，8 课搭成体系。</div>
    </div>

    <div class="track">三种类型教学动作完全不同：A 补提取、B 补闭环、C 补翻译 · 这也是我不接「统一进度班」的原因</div>
  </section>

"""
if "<!-- v2:portrait -->" not in s:
    anchor = '  <section data-page-node-id="ut8zskzISvKBcFq209J8vJ">'
    if anchor not in s:
        sys.exit("找不到真实案例锚点（画像）")
    s = s.replace(anchor, PORTRAIT + anchor, 1)

# ============================================================
# 8. 我不做的四件事
# ============================================================
NOTDO = """  <!-- v2:notdo -->
  <section id="notdo">
    <div class="sec-title"><span class="dot"></span>我不做的四件事<small>比承诺更可信</small></div>
    <div class="notdo">
      <div class="ni">
        <h4>不重讲一遍</h4>
        <p>杨同学国庆刚补过「逐差法」，月考照样错。<b>再讲一遍不会让他会，重做 + 同类闭环才会。</b>所以我从不靠「多上几节」解决问题。</p>
      </div>
      <div class="ni">
        <h4>不刷题海</h4>
        <p>一份卷子做三遍，比三份卷子各做一遍有用。<b>我给的是变式，不是题量。</b>练完能讲出「这题在考哪个动作」，才算过。</p>
      </div>
      <div class="ni">
        <h4>不承诺分数</h4>
        <p>谁都能说「包提 30 分」。<b>我只承诺三件可查的事：</b>每节课有材料、每次课后有反馈、每道错题有归档。</p>
      </div>
      <div class="ni">
        <h4>不用通用讲义</h4>
        <p>北京版 / 北师大版 / 人教 A / 苏教版 / 人教版——<b>你孩子用哪版，我按哪版备课。</b>教材版本对不上，讲得再好也白讲。</p>
      </div>
    </div>
    <div class="track">这些话不好听，但能省掉你两次试错的学费</div>
  </section>

"""
if "<!-- v2:notdo -->" not in s:
    anchor = '  <div class="hook-card scarcity" data-page-node-id="Q2Z8ctKbTBiwAMoEnDkkWj">'
    if anchor not in s:
        sys.exit("找不到稀缺性 hook-card 锚点")
    s = s.replace(anchor, NOTDO + anchor, 1)

# ============================================================
# 9. 落盘
# ============================================================
P.write_text(s, encoding="utf-8")
print(f"done. {orig_len} -> {len(s)} chars (+{len(s)-orig_len})")
