# -*- coding: utf-8 -*-
"""合并 原handbook + 生成staging -> data/handbook.js v2, 并重生成打印版HTML"""
import json, io, os, re, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HB_F = os.path.join(ROOT, "data", "handbook.js")
STATE = os.path.join(ROOT, "scripts", "handbook_gen.json")
CARDS_F = os.path.join(ROOT, "data", "cards.js")
HTML_F = os.path.join(ROOT, "案例冲刺手册.html")


def load_var(path, var):
    raw = io.open(path, encoding="utf-8").read()
    return json.loads(raw[raw.index(var + "=") + len(var) + 1: raw.rindex(";")])


def esc(s):
    return html.escape(str(s or ""), quote=False)


hb = load_var(HB_F, "window.HANDBOOK")
st = json.load(open(STATE, encoding="utf-8"))
cards = load_var(CARDS_F, "window.CARDS")

MOD = {'A': [7], 'B': [3, 6], 'C': [19, 20, 21],
       'D': [8, 9, 10, 11, 12, 14, 16, 17, 18],
       'E': [2, 13, 22], 'F': [1, 4, 5, 15, 23, 24, 25, 26]}
MOD_TITLE = {
    'A': 'A. 访问控制（十年考 8 次，最高频）',
    'B': 'B. 密码学与计算（考 7 次）',
    'C': 'C. 操作系统安全（Linux / Windows，考 6 次）',
    'D': 'D. 网络防御与防火墙（考 8 次）',
    'E': 'E. 代码漏洞与 Web 安全（考 7 次）',
    'F': 'F. 协议、数据安全与法规（近年新增热点）',
}
UNIT_FREQ = {u["id"]: (u.get("freq") or 0) for u in cards["units"]}


def module_of(ch, s2ch):
    try:
        if ch and int(ch) in sum(MOD.values(), []):
            for L, chs in MOD.items():
                if int(ch) in chs:
                    return L
        if s2ch:
            if int(s2ch) in (1, 2, 3):
                return 'D'
            if int(s2ch) == 4:
                return 'C'
    except Exception:
        pass
    return 'F'


def norm(s):
    return re.sub(r'[\s，。、；：,.;:()（）"\'？！]', '', str(s or ''))


# ---------- 1) 默写清单: 保留原105 + 考频优先新增到300 ----------
existing_by_mod = {m["id"].split("-")[-1]: m for m in hb["checklists"]}
seen = set()
for m in hb["checklists"]:
    for it in m["items"]:
        seen.add(norm(it["q"])[:24])

new_pool = []
for uid, rec in (st.get("checklist_gen") or {}).items():
    L = module_of(rec.get("ch"), rec.get("s2ch"))
    fr = UNIT_FREQ.get(uid, 0)
    for it in rec.get("items", []):
        q, a = str(it.get("q", "")).strip(), str(it.get("a", "")).strip()
        if not q or not a:
            continue
        k = norm(q)[:24]
        if k in seen:
            continue
        seen.add(k)
        new_pool.append({"mod": L, "q": q, "a": a, "freq": fr, "uid": uid})
new_pool.sort(key=lambda x: -x["freq"])

cur_total = sum(len(m["items"]) for m in hb["checklists"])
TARGET = 300
add_n = max(0, TARGET - cur_total)
added = 0
for it in new_pool:
    if added >= add_n:
        break
    m = existing_by_mod[it["mod"]]
    m["items"].append({"id": "HB-%s-%d" % (it["mod"], len(m["items"]) + 1), "q": it["q"], "a": it["a"]})
    added += 1

# 模块标题统一
for m in hb["checklists"]:
    L = m["id"].split("-")[-1]
    if L in MOD_TITLE:
        m["title"] = MOD_TITLE[L]

# ---------- 2) 计算卡: 原5 + 新增 ----------
CALC_UNITS = {
    "HC-6": ["U3.3.1"], "HC-7": ["U3.3"], "HC-8": ["G2-4.3", "U22.1"], "HC-9": ["U22.1"],
    "HC-10": ["U3.3"], "HC-11": ["U2.3.3"], "HC-12": ["U3.4"], "HC-13": ["U3.3"],
    "HC-14": ["U3.3"], "HC-15": ["G2-4.1", "U12.1"], "HC-16": ["U3.4"],
}
have_calcs = {c["id"] for c in hb["calcs"]}
for cid, rec in sorted((st.get("calcs_gen") or {}).items()):
    if cid in have_calcs:
        continue
    body = ""
    if rec.get("steps"):
        body += "<pre>" + esc(rec["steps"]) + "</pre>"
    if rec.get("example"):
        body += "<p><b>例题：</b>" + esc(rec["example"]) + "</p>"
    if rec.get("pitfalls"):
        body += '<p class="muted">易错点：' + esc(rec["pitfalls"]) + "</p>"
    hb["calcs"].append({"id": cid, "title": rec.get("title", cid), "html": body, "units": CALC_UNITS.get(cid, [])})

# ---------- 3) 话术: 原6(补cat) + 新增 ----------
OLD_CAT = {"HS-1": "通用", "HS-2": "题型", "HS-3": "题型", "HS-4": "技术域", "HS-5": "题型", "HS-6": "通用"}
for s in hb["scripts"]:
    if not s.get("cat"):
        s["cat"] = OLD_CAT.get(s["id"], "其他")
have_scripts = {s["id"] for s in hb["scripts"]}
SCRIPT_UNITS2 = {
    "密码学概念": ["U3.1"], "密码学计算": ["U3.3"], "认证协议": ["U6.1"], "访问控制/BLP": ["U7.1"],
    "Linux 系统": ["U19.3"], "Windows 系统": ["U19.2"], "防火墙/iptables": ["G2-3.1"], "IDS/IPS/Snort": ["U10.1"],
    "VPN/IPSec": ["U9.1"], "漏洞扫描": ["U13.3"], "恶意代码": ["U14.1"], "应急响应": ["U17.1"],
    "安全审计": ["U12.1"], "风险评估": ["U16.1"], "等级保护": ["U18.1"], "网站安全/SQL注入": ["U22.1"],
    "数据库安全": ["U20.1"], "网络设备安全": ["U21.1"], "物理与环境安全": ["U5.1"], "数据安全": ["U26.1"],
    "隐私保护": ["U15.8"], "法律法规": ["U1.7"], "Android/移动应用": ["U25.1"], "云计算安全": ["U23.1"],
    "工控安全": ["U24.1"], "大数据安全": ["U26.1"], "AI 安全": [],
}
for sid, rec in sorted((st.get("scripts_gen") or {}).items()):
    if sid in have_scripts:
        continue
    parts = []
    if rec.get("signal"):
        parts.append("<p><b>信号：</b>" + esc(rec["signal"]) + "</p>")
    if rec.get("write"):
        parts.append("<p><b>写：</b>" + esc(rec["write"]) + "</p>")
    if rec.get("example"):
        parts.append("<p><b>示例：</b>" + esc(rec["example"]) + "</p>")
    if rec.get("memo"):
        parts.append('<p class="muted">口诀：' + esc(rec["memo"]) + "</p>")
    hb["scripts"].append({"id": sid, "title": rec.get("title", sid), "html": "".join(parts),
                          "units": SCRIPT_UNITS2.get(rec.get("title", ""), []), "cat": rec.get("cat", "其他")})

# ---------- 4) 速查: 原5 + 新增 ----------
have_cheats = {c["id"] for c in hb["cheats"]}
for hid, rec in sorted((st.get("cheats_gen") or {}).items()):
    if hid in have_cheats:
        continue
    hb["cheats"].append({"id": hid, "title": rec.get("title", hid), "html": rec.get("html", "")})

hb["version"] = 2
hb["generated"] = datetime.date.today().isoformat()

with io.open(HB_F, "w", encoding="utf-8") as f:
    f.write("/*自动生成 请勿手改*/\n")
    f.write("window.HANDBOOK=" + json.dumps(hb, ensure_ascii=False, separators=(",", ":")) + ";\n")

n_items = sum(len(m["items"]) for m in hb["checklists"])
print(f"handbook v2: 清单{n_items} 计算卡{len(hb['calcs'])} 话术{len(hb['scripts'])} 速查{len(hb['cheats'])}")

# ---------- 5) 重生成打印版 HTML ----------
old = io.open(HTML_F, encoding="utf-8").read() if os.path.exists(HTML_F) else ""
head = old[:old.index("<body>") + len("<body>")] if "<body>" in old else "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>案例冲刺手册</title></head><body>"

body = ['<div class="wrap">']
body.append('<h1>信息安全工程师（中级）· 案例冲刺手册</h1>')
body.append('<p class="muted">2026年10月考试用 · 勾选框可直接在复习系统"冲刺页"勾选记录</p>')
body.append('<h2 class="first">第一部分 · 默写清单（遮右列自测）</h2>')
for m in hb["checklists"]:
    body.append('<h3>%s</h3><table><tr><th style="width:26px">✓</th><th>问题</th><th>答案</th></tr>' % esc(m["title"]))
    for it in m["items"]:
        body.append('<tr><td class="ck">☐</td><td class="q">%s</td><td>%s</td></tr>' % (esc(it["q"]), esc(it["a"])))
    body.append('</table>')
body.append('<h2>第二部分 · 计算卡</h2>')
for c in hb["calcs"]:
    body.append('<div class="card"><h3>%s</h3>%s</div>' % (esc(c["title"]), c.get("html", "")))
body.append('<h2>第三部分 · 考场万能话术</h2>')
for s in hb["scripts"]:
    body.append('<div class="card"><h3>%s <span class="muted">[%s]</span></h3>%s</div>' % (esc(s["title"]), esc(s.get("cat", "")), s.get("html", "")))
body.append('<h2>第四部分 · 考前速查表</h2>')
for c in hb["cheats"]:
    body.append('<h3>%s</h3><div class="qtext">%s</div>' % (esc(c["title"]), c.get("html", "")))
body.append('<p class="muted" style="margin-top:30px;border-top:1px solid #ccc;padding-top:10px">数据源：data/handbook.js（由脚本生成）。勾选进度请在复习系统"冲刺"页操作。</p>')
body.append('</div><div class="noprint"><button onclick="window.print()">打印 / 导出 PDF</button></div></body></html>')

with io.open(HTML_F, "w", encoding="utf-8") as f:
    f.write(head + "\n".join(body))
print("打印版HTML已重新生成")
