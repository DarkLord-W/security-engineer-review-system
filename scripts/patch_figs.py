# -*- coding: utf-8 -*-
"""从教程章节数据提取图号->原图索引, 生成 data/figs.js (复习系统知识卡插图用)"""
import re, io, os, glob, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "figs.js")
PAT = re.compile(
    r'<img[^>]*src=\\?"(assets/textbook/tb\d+_\d+\.jpg)\\?"[^>]*>.{0,500}?'
    r'<p>\s*图\s*(\d+)\s*[-–—]\s*(\d+)([^<]{0,80})</p>', re.S)

figs = {}
dup = []
for fp in sorted(glob.glob(os.path.join(ROOT, "data", "textbook", "ch*.js"))):
    raw = io.open(fp, encoding="utf-8").read()
    for m in PAT.finditer(raw):
        src, a, b, cap = m.group(1), m.group(2), m.group(3), m.group(4)
        key = a + "-" + b
        if key in figs:
            dup.append(key)
            continue
        figs[key] = {"src": src, "cap": ("图 " + a + "-" + b + cap).strip()}

missing_files = [v["src"] for v in figs.values()
                 if not os.path.exists(os.path.join(ROOT, v["src"].replace("/", os.sep)))]

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("/*自动生成 请勿手改*/\n")
    f.write("window.FIGS=" + json.dumps(figs, ensure_ascii=False, separators=(",", ":")) + ";\n")

print("figs:", len(figs), "dup:", len(dup), "missing files:", len(missing_files))
print("out:", OUT, os.path.getsize(OUT), "bytes")
if missing_files:
    print("MISSING:", missing_files[:5])
