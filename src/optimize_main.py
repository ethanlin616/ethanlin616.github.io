# -*- coding: utf-8 -*-
"""主域 index.html 内容优化：真实案例 + 四步闭环增强 + 图谱画廊 + 错题管家 + 反馈示例"""
import re, io

P = "/Users/geo/Documents/00_data/04_教学/部署-teacher-lin/index.html"
s = open(P, encoding="utf-8").read()

# ---------- 1. CSS 追加 ----------
CSS = """
  /* ===== 内容优化新增样式（2026-10-29） ===== */
  .case-real .cmeta{font-size:13px;color:var(--muted);margin:2px 0 12px;line-height:1.6;}
  .case-real .cmeta b.lo{color:#E04646;font-size:16px;}
  .case-real .cmeta b.up{color:var(--accent);font-size:16px;}
  .cblock{font-size:13px;line-height:1.7;margin-bottom:11px;color:var(--ink);}
  .cblock .ct{display:inline-block;font-weight:800;color:#fff;background:linear-gradient(135deg,var(--c1),var(--c2));font-size:11.5px;padding:2px 9px;border-radius:999px;margin-right:8px;vertical-align:1px;}
  .cblock b{color:var(--accent);}
  .fb-sample{background:#F7F9FC;border:1px solid var(--line);border-radius:16px;padding:18px;font-size:13.5px;line-height:1.85;color:var(--ink);}
  .fb-sample .fb-h{font-size:12px;color:var(--muted);margin-bottom:10px;text-align:center;}
  .gallery{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;}
  .gallery .gimg{border-radius:14px;overflow:hidden;border:1px solid var(--line);background:#fff;box-shadow:0 2px 12px rgba(0,0,0,.05);}
  .gallery .gimg img{width:100%;display:block;aspect-ratio:3/4;object-fit:cover;}
  .gallery .gimg span{display:block;font-size:11.5px;color:var(--muted);padding:7px 6px;text-align:center;}
  .toolflow{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0 4px;align-items:stretch;}
  .toolflow .tf{flex:1;min-width:110px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 10px;text-align:center;}
  .toolflow .tf b{display:block;font-size:14px;margin-bottom:5px;color:var(--ink);}
  .toolflow .tf span{font-size:12px;color:var(--muted);}
  .toolflow .arr{align-self:center;color:var(--accent);font-weight:800;font-size:18px;}
  @media (max-width:560px){ .gallery{grid-template-columns:repeat(2,1fr);} .toolflow .arr{display:none;} }
"""
s = s.replace("</style>", CSS + "\n</style>", 1)

# ---------- 2. 替换 真实提分案例 区块 ----------
new_cases = '''  <section data-page-node-id="ut8zskzISvKBcFq209J8vJ">
    <div class="sec-title"><span class="dot"></span>真实提分案例<small>诊断式教学，效果看得见</small></div>

    <div class="case case-real">
      <div class="head"><span class="tag-pill">案例 · 高一</span><span class="title">杨同学 · 江苏某重点高中</span></div>
      <div class="cmeta">高一阶段性测试：物理 <b class="lo">50</b> / 化学 79 / 数学 121（物理为三科头号短板，但多数失分是"学过没用出来"）</div>
      <div class="cblock"><span class="ct">诊断</span>把 50 分的物理卷逐题拆到题号：单选 4（加速度方向）、实验 12（纸带逐差法）、15/16（多过程综合）…… 失分集中在运动学综合 + 实验；国庆补过的"逐差法""Nₐ 陷阱"考场上仍错——属于"听懂没练熟"，不是知识盲区。</div>
      <div class="cblock"><span class="ct">我的动作</span>不重讲新课，按"错题重做 → 同类题闭环"推进；多过程题强制先画过程图再列式；Nₐ 陷阱做成 6 条检查清单逐题打勾。</div>
      <div class="cblock"><span class="ct">配套产物</span>期中"逐题详解 + 方法思路笔记"双件套、9 张彩色 SVG 讲义、Nₐ 六陷阱清单。</div>
    </div>

    <div class="case case-real">
      <div class="head"><span class="tag-pill">案例 · 初三</span><span class="title">琪琪 · 北京通州（初三物理）</span></div>
      <div class="cmeta">9 月月考：电流方向 / 串联"送分题"丢分，比热容实验单题 −5</div>
      <div class="cblock"><span class="ct">诊断</span>逐题定位失分：第 8/9 题（电流方向规定、串联电流相等）这类概念题丢分最冤；第 25 题比热容实验 −5 是全卷单题最大失分；实验题标准表述（验电器原理）写不准。</div>
      <div class="cblock"><span class="ct">关键发现</span>凡课上练过套路的都拿了分（比热容计算、电表读数、图像题全对）——印证"听懂了没练熟"。物理学习热情明显高于数学。</div>
      <div class="cblock"><span class="ct">配套</span>每课微信课后反馈（讲了什么 / 掌握到哪 / 下次做什么）+ 概念对比卡 + 实验话术清单。</div>
    </div>

    <div class="case case-real">
      <div class="head"><span class="tag-pill">案例 · 六年级</span><span class="title">小宇（化名）· 六年级数学</span></div>
      <div class="cmeta">应用题"单位 1"理解不到位，拆题写关系式习惯没形成</div>
      <div class="cblock"><span class="ct">诊断</span>计算能力强、基础扎实，短板是应用题——单位"1"抽象、不会把文字转成数量关系式。</div>
      <div class="cblock"><span class="ct">我的动作</span>8 课搭建"单位 1 拆解"体系（差量对应、比的应用、分数乘除、圆与组合图形……），每课配备课计划 + 学生练习 + 四步卡 + 答案解析 + 动画。</div>
      <div class="cblock"><span class="ct">配套</span>五件套闭环材料，应用题从"抽象不会"到"会拆关系式"。</div>
    </div>

    <div class="track">以上案例均来自真实上课与诊断记录，姓名与地区已脱敏展示</div>
  </section>'''

m = re.search(r'<section data-page-node-id="ut8zskzISvKBcFq209J8vJ">.*?</section>', s, re.S)
if not m:
    raise SystemExit("找不到 真实提分案例 区块")
s = s[:m.start()] + new_cases + s[m.end():]

# ---------- 3. 四步闭环 每步加真实例句 ----------
repl = [
  ('先找出知识漏洞、思维卡点、失分题型，不盲目开课。',
   '先找出知识漏洞、思维卡点、失分题型，不盲目开课。例：把一份 50 分试卷逐题拆到题号，定位 6 处失分。'),
  ('针对薄弱环节讲透原理，建立解题模型和答题规范。',
   '针对薄弱环节讲透原理，建立解题模型和答题规范。例：受力题按"摩擦三步 / 叠加体 / 合成分解 / 平衡求力"四类动作拆解。'),
  ('精选北京真题/模拟题，限时训练，把方法练成条件反射。',
   '精选北京真题 / 模拟题，限时训练，把方法练成条件反射。例：同类变式卷 + 各区真题限时练。'),
  ('错题归档、阶段测评、及时向家长反馈进度，形成正循环。',
   '错题归档、阶段测评、及时向家长反馈进度，形成正循环。例：每课微信反馈 + 错题进档案定期回炉。'),
]
for a, b in repl:
    if a not in s:
        print("WARN 未命中:", a[:20])
    s = s.replace(a, b, 1)

# ---------- 4. 反馈示例 区块（插在 真实提分案例 之前） ----------
fb = '''  <section data-page-node-id="fb-sample-sec">
    <div class="sec-title"><span class="dot"></span>课后反馈示例<small>每课向家长同步，脱敏展示</small></div>
    <div class="fb-sample">
      <div class="fb-h">— 林老师发给琪琪家长的课后反馈（节选）—</div>
      琪琪家长，第六次课（方差）上完了，跟您反馈一下今天课上暴露的问题。其实还是那几个老问题，重点说两点：<br><br>
      1. <b>熟练度还是欠火候，复习得跟上。</b>课堂这两小时效果是不错的，她一听就懂；但光靠上课、课后不复习，到下周就容易回生。<br>
      2. <b>计算这块还得盯。</b>方差这一章数据量大，特别容易算错。后面我会继续关注她的计算习惯、书写规范，还有读题的仔细程度。<br><br>
      她底子不差，就是"练得不够、课后没收住"。复习抓起来、计算习惯养好，能稳上来，咱们一起盯，继续加油。
    </div>
  </section>
'''
s = s.replace('<section data-page-node-id="ut8zskzISvKBcFq209J8vJ">', fb + '  <section data-page-node-id="ut8zskzISvKBcFq209J8vJ">', 1)

# ---------- 5. 图谱画廊 + 错题管家（插在 学习工作台 之前） ----------
gallery = '''  <section data-page-node-id="gallery-sec">
    <div class="sec-title"><span class="dot"></span>讲义与知识图谱<small>按你孩子的教材版本备课</small></div>
    <div class="gallery">
      <div class="gimg"><img src="gallery/junior-ohm-1.jpg" alt="欧姆定律知识图谱"><span>欧姆定律 · 初中</span></div>
      <div class="gimg"><img src="gallery/junior-ohm-3.jpg" alt="欧姆定律知识图谱"><span>欧姆定律 · 初中</span></div>
      <div class="gimg"><img src="gallery/junior-pow-2.jpg" alt="电功率知识图谱"><span>电流做功 · 初中</span></div>
      <div class="gimg"><img src="gallery/junior-house-1.jpg" alt="生活用电知识图谱"><span>生活用电 · 初中</span></div>
      <div class="gimg"><img src="gallery/junior-cap.jpg" alt="比热容知识图谱"><span>比热容 · 初中</span></div>
      <div class="gimg"><img src="gallery/junior-elec-2.png" alt="电学专题"><span>电学专题 · 初中</span></div>
      <div class="gimg"><img src="gallery/junior-elec-5.png" alt="电学专题"><span>电学专题 · 初中</span></div>
      <div class="gimg"><img src="gallery/senior-balance-1.jpg" alt="共点力平衡"><span>共点力平衡 · 高一</span></div>
      <div class="gimg"><img src="gallery/senior-kinetic-1.png" alt="匀变速直线运动"><span>匀变速 · 高一</span></div>
      <div class="gimg"><img src="gallery/senior-2-1.png" alt="必修二知识图谱"><span>曲线运动 · 高二</span></div>
      <div class="gimg"><img src="gallery/senior-2-3.png" alt="必修二知识图谱"><span>必修二 · 高中</span></div>
    </div>
    <div class="track">共 40+ 张知识图谱覆盖初中电学 / 内能 / 高中必修一·二 · 讲义均彩色图文并茂</div>
  </section>

  <section data-page-node-id="cuotigj-sec">
    <div class="sec-title"><span class="dot"></span>自研 · 错题管家<small>一对一之外的个性化服务</small></div>
    <p style="font-size:13px;color:var(--muted);margin-bottom:6px;line-height:1.7;">孩子错题拍照提交，系统自动标知识点 / 错因，一键生成 AI 解析，并可勾选自动出"变式练习卷"打印重练——机构大班给不了的个性化闭环。</p>
    <div class="toolflow">
      <div class="tf"><b>① 拍照提交</b><span>家长 / 孩子拍下错题</span></div>
      <div class="arr">→</div>
      <div class="tf"><b>② AI 解析</b><span>标知识点 · 错因 · 解法</span></div>
      <div class="arr">→</div>
      <div class="tf"><b>③ 变式卷</b><span>勾选自动出同类题</span></div>
    </div>
    <div class="track">错题管家为学员专享工具，随课程赠送 · 详情加微信了解</div>
  </section>
'''
s = s.replace('<section class="wb-intro" data-page-node-id="M8Hy2KOjlDX9krqZH4JrOw">', gallery + '  <section class="wb-intro" data-page-node-id="M8Hy2KOjlDX9krqZH4JrOw">', 1)

open(P, "w", encoding="utf-8").write(s)
print("主域优化写入完成，文件大小", len(s), "字符")
