# -*- coding: utf-8 -*-
"""案例题渲染数据修复:
1) 从原版HTML补回缺失的图表格(C-2022-2-3/C-2023-2-4)
2) 原版<pre>代码/日志块恢复为<pre>(内容转义)
3) 清除 [图]/（修复：…）等编辑标记
4) 去掉问题文本开头的(N分)
5) 转义非标签裸 <
6) 换行规范化
"""
import json, io, os, re, shutil, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARDS_F = os.path.join(ROOT, "data", "cards.js")
QJS_F = os.path.join(ROOT, "data", "questions.js")
HTMLS = [
    os.path.join(ROOT, "资料", "信息安全工程师2016-2022下午案例真题整理版-内嵌图片版-修复版-内嵌图片版.html"),
    os.path.join(ROOT, "资料", "2023-2025年信息安全工程师下午案例真题整理版-2016-2022样式-内嵌图片版-修复版-内嵌图片版.html"),
]
HALF = {2016: 2, 2017: 1, 2018: 1, 2019: 1, 2020: 2, 2021: 2, 2022: 2, 2023: 2, 2024: 2, 2025: 2}
KNOWN_TAG = r'img|table|tr|td|th|pre|p|br|b|i|ul|li|div|span|figure|figcaption|details|summary|a'


def load_var(path, var):
    raw = io.open(path, encoding="utf-8").read()
    return json.loads(raw[raw.index(var + "=") + len(var) + 1: raw.rindex(";")])


def dump_var(path, var, obj):
    with io.open(path, "w", encoding="utf-8") as f:
        f.write("/*自动生成*/\n" + var + "=")
        f.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":")))
        f.write(";\n")


def read_html_cases():
    out = {}
    for fp in HTMLS:
        if not os.path.exists(fp):
            continue
        raw = io.open(fp, encoding="utf-8").read()
        parts = re.split(r'<h2 class="exam" id="y(\d+)s(\d+)"', raw)
        for i in range(1, len(parts), 3):
            cid = f"C-{int(parts[i])}-{HALF[int(parts[i])]}-{int(parts[i+1])}"
            out[cid] = parts[i + 2]
    return out


def clean_caption(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    t = t.replace('🖼️', '').replace('原卷图表', '').replace('🟢', '').replace('原卷题干', '')
    t = re.sub(r'（修复：[^）]*）', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def clean_markers(t):
    t = t.replace('[图]', '')
    t = t.replace('🖼️', '').replace('原卷图表', '')
    t = t.replace('🔵', '').replace('🔴', '').replace('📝', '')
    t = re.sub(r'（修复：[^）]*）', '', t)
    t = re.sub(r'（[^）]{0,20}(?:原卷|原图|核对稿)[^）]{0,20}）', '', t)
    return t


def escape_bare_lt(t):
    return re.sub(r'<(?!\/?(?:' + KNOWN_TAG + r')\b)(?=[A-Za-z?/])', '&lt;', t)


def esc_pre(text):
    return html.escape(text, quote=False)


def wrap_pre_in_field(field_text, pre_text):
    """在字段文本中按行定位 pre 文本并包裹为<pre>"""
    src_lines = [ln.rstrip() for ln in pre_text.split('\n')]
    if not any(src_lines):
        return None
    first = src_lines[0].strip()
    last = [ln for ln in src_lines if ln.strip()][-1].strip()
    lines = field_text.split('\n')
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == first:
            start = i
            break
    if start is None:
        return None
    end = None
    for j in range(start, len(lines)):
        if lines[j].strip() == last:
            end = j
    if end is None:
        return None
    block = '\n'.join(lines[start:end + 1])
    wrapped = '<pre>' + esc_pre(block) + '</pre>'
    return '\n'.join(lines[:start]) + ('\n' if start > 0 else '') + wrapped + '\n' + '\n'.join(lines[end + 1:])


def main():
    cases_html = read_html_cases()
    db = load_var(QJS_F, "window.DB")

    stats = {"tables_added": 0, "pre_wrapped": 0, "pre_missed": [], "markers": 0, "score_stripped": 0}

    # ---------- 1) 补缺失表格 ----------
    for cid in ["C-2022-2-3", "C-2023-2-4"]:
        body = cases_html.get(cid, "")
        c = db["cases"].get(cid)
        if not body or not c:
            continue
        if "<table" in (c.get("scenario") or ""):
            continue
        tabs = re.findall(r'(?s)<div class="figure-title">(.*?)</div>\s*(<table.*?</table>)', body)
        if not tabs:
            tabs = [(m.group(1), m.group(2)) for m in re.finditer(r'(?s)图\s*3-[12][^<]*</p>\s*(<table.*?</table>)', body)]
        add = []
        for cap, tab in tabs[:2]:
            cap_txt = clean_caption(cap)
            tab = tab.strip()
            add.append(cap_txt + '\n' + tab)
        if add:
            c["scenario"] = (c.get("scenario") or "").rstrip() + "\n\n" + "\n\n".join(add)
            stats["tables_added"] += len(add)

    # ---------- 2) 恢复 pre ----------
    for cid, body in cases_html.items():
        c = db["cases"].get(cid)
        if not c:
            continue
        pres = re.findall(r'(?s)<pre[^>]*>(.*?)</pre>', body)
        for raw_pre in pres:
            pre_text = html.unescape(re.sub(r'<[^>]+>', '', raw_pre)).strip('\n')
            if len(pre_text.strip()) < 10:
                continue
            targets = [("scenario", c)] + [("q%d" % q["no"], q) for q in c["qs"]]
            done = False
            for fname, obj in targets:
                fld = "scenario" if fname == "scenario" else "text"
                t = obj.get(fld) or ""
                if "<pre>" in t:
                    continue
                wrapped = wrap_pre_in_field(t, pre_text)
                if wrapped:
                    obj[fld] = wrapped
                    stats["pre_wrapped"] += 1
                    done = True
                    break
            if not done:
                stats["pre_missed"].append((cid, pre_text[:40].replace('\n', ' ')))

    # ---------- 3) 清标记 + 4) 去分数 + 5) 转义 + 6) 换行 ----------
    def fix_text(t, is_question):
        nonlocal_stats = 0
        before = t
        t = clean_markers(t)
        if t != before:
            stats["markers"] += 1
        if is_question:
            t2 = re.sub(r'^[（(]\s*\d+\s*分[）)]\s*\n?', '', t)
            if t2 != t:
                stats["score_stripped"] += 1
                t = t2
        t = escape_bare_lt(t)
        t = re.sub(r'[ \t]+\n', '\n', t)
        t = re.sub(r'\n{3,}', '\n\n', t)
        return t.strip('\n')

    for cid, c in db["cases"].items():
        c["scenario"] = fix_text(c.get("scenario") or "", False)
        for q in c["qs"]:
            q["text"] = fix_text(q.get("text") or "", True)
            q["answer"] = fix_text(q.get("answer") or "", False)
            q["analysis"] = fix_text(q.get("analysis") or "", False)

    if not os.path.exists(QJS_F + ".bak2"):
        shutil.copy2(QJS_F, QJS_F + ".bak2")
        print("备份:", QJS_F + ".bak2")
    dump_var(QJS_F, "window.DB", db)

    # 复检
    total_pre = sum(json.dumps(c, ensure_ascii=False).count("<pre>") for c in db["cases"].values())
    total_tab = sum(json.dumps(c, ensure_ascii=False).count("<table") for c in db["cases"].values())
    marks = sum((json.dumps(c, ensure_ascii=False).count("[图]") + json.dumps(c, ensure_ascii=False).count("（修复：")) for c in db["cases"].values())
    print(f"补表: {stats['tables_added']} | 包裹pre: {stats['pre_wrapped']} | 漏配pre: {stats['pre_missed']}")
    print(f"清标记字段: {stats['markers']} | 去分数: {stats['score_stripped']}")
    print(f"复检: <pre>={total_pre} <table>={total_tab} 残留标记={marks}")


if __name__ == "__main__":
    main()
