# -*- coding: utf-8 -*-
"""解析 案例冲刺手册.html -> data/handbook.js (复习系统"冲刺"页数据源)"""
import re, io, os, json, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "案例冲刺手册.html")
OUT = os.path.join(ROOT, "data", "handbook.js")

CALC_UNITS = {
    "HC-1": ["U3.3.4"],
    "HC-2": ["U3.3"],
    "HC-3": ["U3.3.1"],
    "HC-4": ["U19.3", "G2-4.1"],
    "HC-5": ["G2-3.1"],
}
SCRIPT_UNITS = {
    "HS-1": ["U1.3"],
    "HS-2": ["U3.6"],
    "HS-3": ["U2.3.3"],
    "HS-4": ["G2-3.1"],
    "HS-5": ["U3.3"],
    "HS-6": ["U1.6"],
}


def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s or '').strip()


raw = io.open(SRC, encoding="utf-8").read()
hb = {"version": 1, "generated": datetime.date.today().isoformat(),
      "checklists": [], "calcs": [], "scripts": [], "cheats": []}

# ---- 第一部分: 默写清单 ----
i1, i2 = raw.index('第一部分'), raw.index('第二部分')
part1 = raw[i1:i2]
letters = "ABCDEFGHIJ"
for mi, m in enumerate(re.finditer(r'(?s)<h3[^>]*>(.*?)</h3>(.*?)(?=<h3|$)', part1)):
    title = strip_tags(m.group(1))
    tab = re.search(r'(?s)<table>(.*?)</table>', m.group(2))
    if not tab or not title:
        continue
    items = []
    for r in re.findall(r'(?s)<tr>(.*?)</tr>', tab.group(1)):
        cells = re.findall(r'(?s)<t[hd][^>]*>(.*?)</t[hd]>', r)
        if len(cells) < 3 or not re.match(r'^\d+$', strip_tags(cells[0])):
            continue
        q = cells[1].strip()
        a = cells[2].strip()
        items.append({"id": "HB-%s-%d" % (letters[mi], len(items) + 1), "q": q, "a": a})
    hb["checklists"].append({"id": "HB-MOD-" + letters[mi], "title": title, "items": items})

# ---- 第二部分: 计算卡 ----
i2b, i3 = raw.index('第二部分'), raw.index('第三部分')
for ci, c in enumerate(re.findall(r'(?s)<div class="card">(.*?)\n</div>', raw[i2b:i3]), 1):
    tm = re.search(r'<h3[^>]*>(.*?)</h3>', c)
    if not tm:
        continue
    title = strip_tags(tm.group(1))
    html = re.sub(r'(?s)^\s*<h3[^>]*>.*?</h3>', '', c).strip()
    cid = "HC-%d" % ci
    hb["calcs"].append({"id": cid, "title": title, "html": html, "units": CALC_UNITS.get(cid, [])})

# ---- 第三部分: 话术 ----
i3b, i4 = raw.index('第三部分'), raw.index('第四部分')
for si, c in enumerate(re.findall(r'(?s)<div class="card">(.*?)\n</div>', raw[i3b:i4]), 1):
    tm = re.search(r'<h3[^>]*>(.*?)</h3>', c)
    if not tm:
        continue
    title = strip_tags(tm.group(1))
    html = re.sub(r'(?s)^\s*<h3[^>]*>.*?</h3>', '', c).strip()
    sid = "HS-%d" % si
    hb["scripts"].append({"id": sid, "title": title, "html": html, "units": SCRIPT_UNITS.get(sid, [])})

# ---- 第四部分: 速查 ----
i4b, i5 = raw.index('第四部分'), raw.index('第五部分')
for ti, m in enumerate(re.finditer(r'(?s)<h3[^>]*>(.*?)</h3>(.*?)(?=<h3|$)', raw[i4b:i5]), 1):
    title = strip_tags(m.group(1))
    body = m.group(2).strip()
    if not title or '<table' not in body:
        continue
    hb["cheats"].append({"id": "HT-%d" % ti, "title": title, "html": body})

# ---- 校验 ----
n_items = sum(len(m["items"]) for m in hb["checklists"])
print("模块:", len(hb["checklists"]), "| 清单条目:", n_items,
      "| 计算卡:", len(hb["calcs"]), "| 话术:", len(hb["scripts"]), "| 速查:", len(hb["cheats"]))
assert n_items == 105, "清单条目数不符: %d" % n_items

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("/*自动生成 请勿手改*/\n")
    f.write("window.HANDBOOK=" + json.dumps(hb, ensure_ascii=False, separators=(",", ":")) + ";\n")
print("输出:", OUT, os.path.getsize(OUT), "bytes")
