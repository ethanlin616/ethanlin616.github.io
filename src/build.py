#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""招生站构建脚本：data/*.json + templates/ -> 各学科静态页

用法：python3 build.py
输出：仓库根目录下 math/ physics/ chemistry/（主域 index.html 不由此脚本生成）
"""
import json
import shutil
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]      # 部署-teacher-lin/
SRC = ROOT / "src"
DATA = SRC / "data"
TPL = SRC / "templates"
ASSETS = SRC / "assets"

SITE = json.loads((DATA / "site.json").read_text(encoding="utf-8"))
SUBJECTS = ["math", "physics", "chemistry"]

# 各学科页突出展示的荣誉（索引对应 site.honors）
SUBJECT_HONORS = {"math": [0, 3], "physics": [2, 3], "chemistry": [1, 0]}
SUBJECT_CRED_NOTE = {
    "math": "数学既讲透原理，也讲怎么按评分标准拿分",
    "physics": "电子工程科班背景，物理是我的主攻方向",
    "chemistry": "扎实理科功底教化学，重原理推导而不是死记硬背",
}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def render_pains(pains):
    out = []
    for i, p in enumerate(pains, 1):
        out.append(f'<div class="pain"><div class="no">{i}</div><div>'
                   f'<div class="t">{esc(p["title"])}</div>'
                   f'<div class="d">{esc(p["desc"])}</div></div></div>')
    return "\n".join(out)


def render_demo(items):
    """一道题，看我怎么教：题面 → 常见错法 → 判定步骤 → 口诀 → 出处"""
    if not items:
        return ""
    out = []
    for d in items:
        steps = "".join(f"<li>{s}</li>" for s in d.get("steps", []))
        out.append(
            f'<div class="demo">'
            f'<span class="dtag">{esc(d["tag"])}</span>'
            f'<div class="q">{esc(d["q"])}</div>'
            f'<div class="wrong"><b>多数学生会这样错：</b>{esc(d["wrong"])}</div>'
            f'<ol>{steps}</ol>'
            f'<div class="key">{esc(d["key"])}</div>'
            f'<div class="src">出处：{esc(d["src"])}</div>'
            f'</div>'
        )
    return "\n".join(out)


def render_methods(methods):
    out = []
    for i, m in enumerate(methods, 1):
        out.append(f'<div class="method"><div class="t">{i}. {esc(m["title"])}</div>'
                   f'<div class="d">{esc(m["desc"])}</div></div>')
    return "\n".join(out)


def render_tabs(tabs):
    out = []
    for i, t in enumerate(tabs):
        on = " on" if i == 0 else ""
        out.append(f'<button class="tab{on}" data-tab="{t["key"]}">{esc(t["label"])}</button>')
    return '<div class="tabs">' + "\n".join(out) + "</div>"


def render_outline(outline, tabs):
    notes = {t["key"]: t.get("note", "") for t in tabs}
    out = []
    for i, o in enumerate(outline):
        on = " on" if i == 0 else ""
        tags = "".join(f"<span>{esc(x)}</span>" for x in o["topics"])
        note = notes.get(o["tab"], "")
        out.append(
            f'<div class="tabpanel{on}" id="panel-{o["tab"]}">'
            f'<div class="tabnote">{esc(note)}</div>'
            f'<div class="tags">{tags}</div></div>'
        )
    return "\n".join(out)


def render_ptable(rows):
    tr = []
    for r in rows:
        tr.append(
            f'<tr><td><div class="nm">{esc(r["name"])}</div>'
            f'<div class="ds">{esc(r["desc"])}</div></td>'
            f'<td style="color:#8A929E;font-size:12.5px">{esc(r["form"])}</td>'
            f'<td class="pr">{r["price"]} 元<small>/{esc(r["unit"].replace("元/",""))}</small></td></tr>'
        )
    return ('<table class="ptable"><tr><th style="width:52%">课程</th>'
            '<th style="width:18%">形式</th><th style="width:30%;text-align:right">价格</th></tr>'
            + "\n".join(tr) + "</table>")


def render_trialbox(rows):
    vals = "".join(f'<div class="v"><b>{r["price"]}</b><i>{esc(r["stage"])}</i></div>'
                   for r in rows)
    return ('<div class="trialbox"><div class="lb">首次试听享半价（一对一）'
            '<em>一节完整正课，满意再正式报名</em></div>'
            f'<div class="vals">{vals}</div></div>')


def render_cases(cases):
    out = []
    for c in cases:
        out.append(
            f'<div class="case"><div class="g">{esc(c["grade"])}</div>'
            f'<div class="p">{esc(c["problem"])}</div>'
            f'<div class="nums"><div><div class="k">辅导前</div><div class="v">{esc(c["before"])}</div></div>'
            f'<div><div class="k">现在</div><div class="v up">{esc(c["after"])}</div></div></div>'
            f'<div class="r">{esc(c["result"])}</div></div>'
        )
    return "\n".join(out)


def render_real_cases(cases):
    out = []
    for c in cases:
        blocks = "".join(
            f'<div class="cblock"><span class="ct">{esc(b["ct"])}</span>{esc(b["text"])}</div>'
            for b in c.get("blocks", []))
        out.append(
            f'<div class="case case-real"><div class="g">{esc(c["grade"])}</div>'
            f'<div class="cmeta">{esc(c.get("cmeta", ""))}</div>{blocks}</div>')
    return "\n".join(out)


def render_method_sample(ms):
    if not ms:
        return ""
    return "\n".join(
        f'<div class="ms-item"><div class="h">{esc(it["h"])}</div>'
        f'<div class="d">{esc(it["d"])}</div></div>'
        for it in ms.get("items", []))


def render_evidence(evi):
    if not evi:
        return ""
    parts = []
    for g in evi.get("gallery", []):
        parts.append(f'<img src="{esc(g)}" alt="讲义图谱">')
    if parts:
        parts = ['<div class="gallery-mini">'] + parts + ['</div>']
    sp = evi.get("sympy")
    if sp:
        parts.append(f'<div class="sympy-card"><span class="big">{esc(sp.get("num", ""))}</span>'
                     f'{esc(sp.get("text", ""))}</div>')
    return "\n".join(parts)


def render_creds(creds):
    return "".join(f'<div>{esc(c)}</div>' for c in creds)


def render_honors(idxs):
    out = []
    for i in idxs:
        out.append(f'<div class="honor"><span class="dot">◆</span><span>{esc(SITE["honors"][i])}</span></div>')
    return "\n".join(out)


def render_faq(faq):
    out = []
    for f in faq:
        out.append(f'<details><summary>{esc(f["q"])}</summary>'
                   f'<div class="a">{esc(f["a"])}</div></details>')
    return "\n".join(out)


def render_subjnav(cur):
    items = ['<a href="/">主页</a>']
    for s in SITE["sites"]:
        on = " on" if s["key"] == cur else ""
        items.append(f'<a class="{on.strip()}" href="{s["path"]}">{s["name"]}</a>')
    return "\n".join(items)


def render_cross(cur):
    out = []
    for s in SITE["sites"]:
        if s["key"] == cur:
            continue
        out.append(f'<a href="{s["path"]}"><b>{s["name"]}</b><i>{esc(s["desc"])}</i></a>')
    return "\n".join(out)


def build_subject(key):
    cfg = json.loads((DATA / f"{key}.json").read_text(encoding="utf-8"))
    tpl = Template((TPL / "subject.html").read_text(encoding="utf-8"))
    css = (TPL / "base.css").read_text(encoding="utf-8")

    base = SITE["base_url"]
    path = f"/{key}/"
    canonical = base + path
    cover = f"{base}{path}{cfg['cover']}"
    cases = [c for c in SITE["cases"] if c["subject"] == key]
    chips = "\n".join(f"<span>{esc(c)}</span>" for c in SITE["creds"])

    html = tpl.substitute(
        css=css,
        title=cfg["seo_title"],
        desc=cfg["seo_desc"],
        canonical=canonical,
        cover=cover,
        brand=SITE["brand"],
        brandsub="北京一对一提分",
        subjnav=render_subjnav(key),
        kicker=cfg["hero_kicker"],
        hero_title=cfg["hero_title"],
        hero_sub=cfg["hero_sub"],
        chips=chips,
        name=cfg["name"],
        pains=render_pains(cfg["pains"]),
        demo=render_demo(cfg.get("demo", [])),
        methods=render_methods(cfg["methods"]),
        tabs=render_tabs(cfg["tabs"]),
        outline=render_outline(cfg["outline"], cfg["tabs"]),
        ptable=render_ptable(cfg["pricing_rows"]),
        trialbox=render_trialbox(cfg["trial_rows"]),
        pricenote=f"{SITE['teaching']['unit_note']}；{SITE['trial']['note']}。"
                  f"上课形式：{SITE['teaching']['form']}；{SITE['teaching']['mode']}。",
        cases=render_real_cases(cfg.get("real_cases", [])),
        method_sample=render_method_sample(cfg.get("method_sample", {})),
        evi_note=cfg.get("evi_note", ""),
        evidence=render_evidence(cfg.get("evidence", {})),
        crednote=SUBJECT_CRED_NOTE[key],
        creds=render_creds(SITE["creds"]),
        honors=render_honors(SUBJECT_HONORS[key]),
        faq=render_faq(cfg["faq"]),
        trialnote=f"{cfg['name']}首次试听半价，一节完整正课，课后给学情判断和后续建议。",
        qr="qr.png",
        phone=SITE["contact"]["phone"],
        phone_display=SITE["contact"]["phone_display"],
        wechat_note=SITE["contact"]["wechat_note"],
        cross=render_cross(key),
        base_url=base,
        year="2026",
    )

    outdir = ROOT / key
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "index.html").write_text(html, encoding="utf-8")

    # 资源：二维码 + 分享封面（存在才拷）
    qr_src = ASSETS / f"qr-{key}.png"
    if qr_src.exists():
        shutil.copy2(qr_src, outdir / "qr.png")
    for fn in [cfg["cover"], "favicon.png"]:
        src = ASSETS / fn
        if src.exists():
            shutil.copy2(src, outdir / fn)
    for g in cfg.get("evidence", {}).get("gallery", []):
        src = ROOT / "gallery" / g
        if src.exists():
            shutil.copy2(src, outdir / g)
    print(f"[ok] {key}: {outdir/'index.html'} ({len(html)} bytes)")


def main():
    for k in SUBJECTS:
        build_subject(k)
    print("done.")


if __name__ == "__main__":
    main()
