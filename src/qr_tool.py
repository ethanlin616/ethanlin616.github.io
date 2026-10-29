#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二维码素材工具（纯标准库，不依赖 PIL）。

背景：主页把整张微信名片截图（200x295 竖图）内联进 HTML，并用 70x70 的
正方形容器显示，二维码因此被纵向压扁；同时整图重复内联 3 次，占 92KB。
本脚本从高清原图 workbench/assets/wechat-qr.png 里按模块网格重建二维码，
输出正方形、纯黑白的小图，既不变形又小一个数量级。

用法：
    python3 src/qr_tool.py            # 生成 src/assets/qr-square.png
    python3 src/qr_tool.py --probe    # 校验网格对齐（定位图案 + 时序图案）
    python3 src/qr_tool.py --ascii    # 打印整图字符预览，排查用
"""
import os
import re
import sys
import zlib
import struct
import base64

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_HD = os.path.join(ROOT, "workbench", "assets", "wechat-qr.png")
OUT = os.path.join(ROOT, "src", "assets", "qr-square.png")


# ---------- PNG 读写 ----------

def read_png(path):
    """返回 (宽, 高, 每像素字节数, RGB(A) 像素字节)。仅支持 8bit RGB/RGBA 非隔行。"""
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "不是 PNG"
    pos, idat, ihdr = 8, [], None
    while pos < len(data):
        ln, typ = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", body)
        elif typ == b"IDAT":
            idat.append(body)
        elif typ == b"IEND":
            break
        pos += 12 + ln
    w, h, depth, ctype, comp, filt, inter = ihdr
    assert depth == 8 and inter == 0 and ctype in (2, 6), \
        f"仅支持 8bit RGB/RGBA 非隔行 PNG，实际 depth={depth} ctype={ctype} inter={inter}"
    bpp = 3 if ctype == 2 else 4
    raw = zlib.decompress(b"".join(idat))
    stride = w * bpp
    out = bytearray(h * stride)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        f = raw[p]
        p += 1
        line = bytearray(raw[p:p + stride])
        p += stride
        if f == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return w, h, bpp, bytes(out)


def write_png(path, w, h, rgb):
    """rgb 为 3 字节/像素、无滤波。返回文件字节数。"""
    stride = w * 3
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]

    def chunk(typ, body):
        return (struct.pack(">I", len(body)) + typ + body
                + struct.pack(">I", zlib.crc32(typ + body) & 0xFFFFFFFF))

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "wb").write(png)
    return len(png)


def to_gray(w, h, bpp, px):
    g = [0] * (w * h)
    for y in range(h):
        row = y * w * bpp
        base = y * w
        for x in range(w):
            i = row + x * bpp
            g[base + x] = (px[i] * 299 + px[i + 1] * 587 + px[i + 2] * 114) // 1000
    return g


# ---------- 几何 ----------

def bbox_dark(g, w, h, thr=110, y0=0.22, y1=0.86):
    """在指定纵向区间里找暗像素包围盒，避开顶部头像和底部说明文字。"""
    ay0, ay1 = int(h * y0), int(h * y1)
    minx, miny, maxx, maxy = w, h, -1, -1
    for y in range(ay0, ay1):
        base = y * w
        for x in range(w):
            if g[base + x] < thr:
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
    return minx, miny, maxx, maxy


def cell_dark(g, w, h, x0, x1, y0, y1, thr=128):
    """一格内多数投票，返回 0/1。"""
    dark = tot = 0
    for y in range(max(0, y0), min(y1, h)):
        base = y * w
        for x in range(max(0, x0), min(x1, w)):
            tot += 1
            if g[base + x] < thr:
                dark += 1
    return (1 if dark * 2 > tot else 0) if tot else 0


def grid_error(g, w, h, x0, y0, side, N, thr=128):
    """只比对固定图案（三个定位 + 两条时序）的错误格数，用于搜索最佳网格。"""
    cell = side / N

    def at(cy, cx):
        return cell_dark(g, w, h,
                         int(x0 + cx * cell), int(x0 + (cx + 1) * cell),
                         int(y0 + cy * cell), int(y0 + (cy + 1) * cell), thr)

    err = 0
    for oy, ox in ((0, 0), (0, N - 7), (N - 7, 0)):
        for dy in range(7):
            for dx in range(7):
                want = 1 if (dy in (0, 6) or dx in (0, 6)
                             or (2 <= dy <= 4 and 2 <= dx <= 4)) else 0
                if at(oy + dy, ox + dx) != want:
                    err += 1
    for i in range(8, N - 8):
        want = 1 if i % 2 == 0 else 0
        if at(6, i) != want:
            err += 1
        if at(i, 6) != want:
            err += 1
    return err


def align_grid(g, w, h, box, only_N=None):
    """穷举模块数与 1~3 像素的网格偏移，找出固定图案完全对得上的那组。
    返回 (错误数, 模块数, 横向偏移, 纵向偏移, 边长)。"""
    minx, miny, maxx, maxy = box
    span = min(maxx - minx + 1, maxy - miny + 1)
    cands = [only_N] if only_N else list(range(21, 98, 4))
    best = (10 ** 9, None, None, None, span)
    for Nc in cands:
        for oy in range(-3, 4):
            for ox in range(-3, 4):
                x0, y0 = minx + ox, miny + oy
                if x0 < 0 or y0 < 0 or x0 + span > w or y0 + span > h:
                    continue
                e = grid_error(g, w, h, x0, y0, span, Nc)
                if e < best[0]:
                    best = (e, Nc, ox, oy, span)
    return best


def module_matrix(g, w, h, x0, y0, side, N, thr=128):
    cell = side / N
    mat = []
    for cy in range(N):
        row = []
        for cx in range(N):
            row.append(cell_dark(g, w, h,
                                 int(x0 + cx * cell), int(x0 + (cx + 1) * cell),
                                 int(y0 + cy * cell), int(y0 + (cy + 1) * cell), thr))
        mat.append(row)
    return mat


def validate_qr(mat):
    """结构校验：三个定位图案 + 两条时序图案。网格对齐正确时必然全部成立。"""
    N = len(mat)
    msgs = []
    ok = True

    def finder(oy, ox, name):
        nonlocal ok
        for dy in range(7):
            for dx in range(7):
                want = 1 if (dy in (0, 6) or dx in (0, 6)
                             or (2 <= dy <= 4 and 2 <= dx <= 4)) else 0
                if mat[oy + dy][ox + dx] != want:
                    ok = False
                    msgs.append(f"{name}定位图案第 ({dy},{dx}) 格不符")
                    return

    finder(0, 0, "左上")
    finder(0, N - 7, "右上")
    finder(N - 7, 0, "左下")

    bad_h = [i for i in range(8, N - 8) if mat[6][i] != (1 if i % 2 == 0 else 0)]
    bad_v = [i for i in range(8, N - 8) if mat[i][6] != (1 if i % 2 == 0 else 0)]
    if bad_h:
        ok = False
        msgs.append(f"横向时序图案 {len(bad_h)} 格不符（首个第 {bad_h[0]} 格）")
    if bad_v:
        ok = False
        msgs.append(f"纵向时序图案 {len(bad_v)} 格不符（首个第 {bad_v[0]} 格）")
    if ok:
        msgs.append("三个定位图案 + 两条时序图案全部正确，网格对齐无误")
    return ok, msgs


def build_crisp(mat, target=360, quiet=4):
    """按模块矩阵重建：每模块画成 scale×scale 的实心块，外加静区。"""
    N = len(mat)
    total = N + quiet * 2
    scale = max(2, round(target / total))
    size = total * scale
    out = [255] * (size * size)
    for cy in range(N):
        for cx in range(N):
            if not mat[cy][cx]:
                continue
            py0 = (cy + quiet) * scale
            px0 = (cx + quiet) * scale
            for y in range(py0, py0 + scale):
                base = y * size
                for x in range(px0, px0 + scale):
                    out[base + x] = 0
    return size, out


def ascii_preview(g, w, h, cols=48, rows=70):
    for ry in range(rows):
        line = []
        for rx in range(cols):
            x0, x1 = rx * w // cols, (rx + 1) * w // cols
            y0, y1 = ry * h // rows, (ry + 1) * h // rows
            dark = tot = 0
            for y in range(y0, y1, 3):
                for x in range(x0, x1, 3):
                    tot += 1
                    if g[y * w + x] < 128:
                        dark += 1
            line.append("#" if tot and dark / tot > 0.35 else
                        ("+" if tot and dark / tot > 0.12 else "."))
        print(f"{ry * h // rows:5d} " + "".join(line))


def main():
    w, h, bpp, px = read_png(SRC_HD)
    g = to_gray(w, h, bpp, px)
    print(f"高清原图 {w}x{h}")

    if "--ascii" in sys.argv:
        ascii_preview(g, w, h)
        return

    box = bbox_dark(g, w, h)
    print(f"二维码包围盒 {box}  边长 {min(box[2]-box[0], box[3]-box[1])+1}px")

    err, N, ox, oy, span = align_grid(g, w, h, box)
    if N is None:
        sys.exit("未找到可用的模块网格，请人工确认素材")
    x0, y0 = box[0] + ox, box[1] + oy
    mat = module_matrix(g, w, h, x0, y0, span, N)
    ok, msgs = validate_qr(mat)
    print(f"网格：模块数 {N}，偏移 ({ox},{oy})，固定图案误差 {err}")
    for m in msgs:
        print("   ", m)
    if not ok:
        sys.exit("结构校验未通过，拒绝生成（宁可不换图，也不能换出一张扫不出来的码）")

    if "--probe" in sys.argv:
        html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
        m = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]{20000,})', html)
        if m:
            tmp = "/tmp/_inline_qr.png"
            open(tmp, "wb").write(base64.b64decode(m.group(1)))
            w2, h2, b2, p2 = read_png(tmp)
            box2 = bbox_dark(to_gray(w2, h2, b2, p2), w2, h2)
            side2 = min(box2[2] - box2[0], box2[3] - box2[1]) + 1
            print(f"页面现用图 {w2}x{h2}，二维码边长 {side2}px，"
                  f"每模块仅 {side2/N:.2f}px（重建后 {span/N:.2f}px）")
        return

    size, out = build_crisp(mat, target=360)
    rgb = bytearray()
    for v in out:
        rgb += bytes((v, v, v))
    sz = write_png(OUT, size, size, bytes(rgb))
    print(f"已生成 {os.path.relpath(OUT, ROOT)}  {size}x{size}  "
          f"{sz/1024:.1f}KB（base64 约 {sz*4/3/1024:.1f}KB）")


if __name__ == "__main__":
    main()
