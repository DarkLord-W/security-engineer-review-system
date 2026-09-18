# -*- coding: utf-8 -*-
"""第二轮: 处理已转义字段中的pre、同一字段多个pre、以及缺失的代码块"""
import json, io, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QJS_F = os.path.join(ROOT, "data", "questions.js")
HTMLS = [
    os.path.join(ROOT, "资料", "信息安全工程师2016-2022下午案例真题整理版-内嵌图片版-修复版-内嵌图片版.html"),
    os.path.join(ROOT, "资料", "2023-2025年信息安全工程师下午案例真题整理版-2016-2022样式-内嵌图片版-修复版-内嵌图片版.html"),
]
HALF = {2016: 2, 2017: 1, 2018: 1, 2019: 1, 2020: 2, 2021: 2, 2022: 2, 2023: 2, 2024: 2, 2025: 2}


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
            out[f"C-{int(parts[i])}-{HALF[int(parts[i])]}-{int(parts[i+1])}"] = parts[i + 2]
    return out


def find_range(plain_lines, pre_text):
    pre_lines = [l.strip() for l in pre_text.split('\n') if l.strip()]
    if not pre_lines:
        return None
    first, last = pre_lines[0], pre_lines[-1]
    start = None
    for i, ln in enumerate(plain_lines):
        if ln.strip() == first:
            start = i
            break
    if start is None:
        return None
    end = None
    for j in range(start, len(plain_lines)):
        if plain_lines[j].strip() == last:
            end = j
    return (start, end) if end is not None else None


def wrap_field(field, pre_text):
    plain = html.unescape(field)
    rng = find_range(plain.split('\n'), pre_text)
    if not rng:
        return None
    start, end = rng
    orig_lines = field.split('\n')
    plain_lines = plain.split('\n')
    block = '\n'.join(plain_lines[start:end + 1])
    wrapped = '<pre>' + html.escape(block, quote=False) + '</pre>'
    return '\n'.join(orig_lines[:start] + [wrapped] + orig_lines[end + 1:])


def main():
    cases_html = read_html_cases()
    db = load_var(QJS_F, "window.DB")
    wrapped = 0
    missed = []

    for cid, body in cases_html.items():
        c = db["cases"].get(cid)
        if not c:
            continue
        pres = re.findall(r'(?s)<pre[^>]*>(.*?)</pre>', body)
        for raw_pre in pres:
            pre_text = html.unescape(re.sub(r'<[^>]+>', '', raw_pre)).strip('\n')
            if len(pre_text.strip()) < 10:
                continue
            first_esc = html.escape([l for l in pre_text.split('\n') if l.strip()][0], quote=False)
            targets = [("scenario", c)] + [("q%d" % q["no"], q) for q in c["qs"]]
            done = False
            for fname, obj in targets:
                for fld in (["scenario"] if fname == "scenario" else ["text", "answer", "analysis"]):
                    t = obj.get(fld) or ""
                    if not t:
                        continue
                    if '<pre>' + first_esc in t:
                        done = True
                        break
                    nt = wrap_field(t, pre_text)
                    if nt is not None:
                        obj[fld] = nt
                        wrapped += 1
                        done = True
                        break
                if done:
                    break
            if not done:
                missed.append((cid, pre_text[:50].replace('\n', ' ')))

    # 缺失代码块补插(C-2018-1-4 心跳包代码)
    c = db["cases"].get("C-2018-1-4")
    if c and "process_heartbeat" not in json.dumps(c, ensure_ascii=False):
        body = cases_html.get("C-2018-1-4", "")
        pres = re.findall(r'(?s)<pre[^>]*>(.*?)</pre>', body)
        if pres:
            code = html.unescape(re.sub(r'<[^>]+>', '', pres[0])).strip('\n')
            c["scenario"] = c["scenario"].rstrip() + \
                "\n\n接收端收到该心跳包后的处理函数是process_heartbeat()：\n<pre>" + html.escape(code, quote=False) + "</pre>"
            print("补插 C-2018-1-4 心跳包代码")

    dump_var(QJS_F, "window.DB", db)
    total_pre = sum(json.dumps(c, ensure_ascii=False).count("<pre>") for c in db["cases"].values())
    print(f"本轮包裹pre: {wrapped} | 仍漏配: {missed}")
    print(f"复检: <pre>={total_pre}")


if __name__ == "__main__":
    main()
