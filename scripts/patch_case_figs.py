# -*- coding: utf-8 -*-
"""从两份案例HTML中提取缺失原图, 保存到 assets/img/, 并补进 data/questions.js。
用法: python scripts/patch_case_figs.py   (自动备份为 data/questions.js.bak)"""
import re, io, os, json, base64, hashlib, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QJS = os.path.join(ROOT, "data", "questions.js")
IMGDIR = os.path.join(ROOT, "assets", "img")
HTMLS = [
    os.path.join(ROOT, "资料", "信息安全工程师2016-2022下午案例真题整理版-内嵌图片版-修复版-内嵌图片版.html"),
    os.path.join(ROOT, "资料", "2023-2025年信息安全工程师下午案例真题整理版-2016-2022样式-内嵌图片版-修复版-内嵌图片版.html"),
]
HALF = {2016: 2, 2017: 1, 2018: 1, 2019: 1, 2020: 2, 2021: 2, 2022: 2, 2023: 2, 2024: 2, 2025: 2}

def read_html_cases():
    out = {}
    for fp in HTMLS:
        if not os.path.exists(fp):
            continue
        raw = io.open(fp, encoding="utf-8").read()
        parts = re.split(r'<h2 class="exam" id="y(\d+)s(\d+)"', raw)
        for i in range(1, len(parts), 3):
            year, idx, body = int(parts[i]), int(parts[i + 1]), parts[i + 2]
            out[f"C-{year}-{HALF[year]}-{idx}"] = body
    return out

IMG_RE = re.compile(r'<img[^>]*src="(data:image/([^;]+);base64,([^"]+))"[^>]*>')

def html_imgs(body):
    res = []
    for m in IMG_RE.finditer(body):
        tag = body[m.start():m.end()]
        alt_m = re.search(r'alt="([^"]*)"', tag)
        res.append({
            "uri": m.group(1), "ext": m.group(2), "b64": m.group(3),
            "alt": alt_m.group(1) if alt_m else "",
            "md5": hashlib.md5(m.group(3).encode()).hexdigest(),
        })
    return res

def ref_of(alt):
    m = re.search(r'图\s*(\d+)\s*[-–—]\s*(\d+)', alt or "")
    return f"图{m.group(1)}-{m.group(2)}" if m else ""

def insert_img(case, ref, alt, tag):
    anchor_patterns = []
    if ref:
        anchor_patterns = [
            (ref + "（修复", None), (ref + "（原图", None),
            (ref, "[图]"), ("[图] " + ref, None),
            (ref, "@start"),
        ]
    fields = [("scenario", case.get("scenario") or "")]
    for q in case.get("qs", []):
        fields.append(("q" + str(q.get("no")), q.get("text") or ""))
    for pat, must in anchor_patterns:
        for fname, txt in fields:
            for i, ln in enumerate(txt.split("\n")):
                if must == "@start":
                    ok = ln.strip().startswith(pat)
                elif must is None:
                    ok = pat in ln
                else:
                    ok = (pat in ln and must in ln)
                if ok:
                    lines = txt.split("\n")
                    lines.insert(i + 1, tag)
                    newtxt = "\n".join(lines)
                    if fname == "scenario":
                        case["scenario"] = newtxt
                    else:
                        for q in case.get("qs", []):
                            if "q" + str(q.get("no")) == fname:
                                q["text"] = newtxt
                    return fname + " 行:" + ln.strip()[:40]
    # 场景末尾兜底
    cap = ("\n" + alt + "\n") if alt else "\n"
    case["scenario"] = (case.get("scenario") or "") + cap + tag
    return "scenario 末尾兜底"

def main():
    cases_html = read_html_cases()
    raw = io.open(QJS, encoding="utf-8").read()
    pre = raw[:raw.index("window.DB=") + len("window.DB=")]
    post = raw[raw.rindex("}") + 1:]
    db = json.loads(raw[raw.index("window.DB=") + len("window.DB="): raw.rindex("}") + 1])

    if not os.path.exists(QJS + ".bak"):
        shutil.copy2(QJS, QJS + ".bak")
        print("备份:", QJS + ".bak")

    added = []
    for cid, c in db["cases"].items():
        body = cases_html.get(cid)
        if not body:
            continue
        himgs = html_imgs(body)
        db_blob = json.dumps(c, ensure_ascii=False)
        db_hashes = set(hashlib.md5(x.encode()).hexdigest()
                        for x in re.findall(r'base64,([A-Za-z0-9+/=]+)', db_blob))
        for k, im in enumerate(himgs, 1):
            if im["md5"] in db_hashes:
                continue
            ext = "jpg" if "jpeg" in im["ext"] or "jpg" in im["ext"] else im["ext"].split("/")[-1]
            fname = f"case_{cid}_{k}.{ext}"
            fpath = os.path.join(IMGDIR, fname)
            with open(fpath, "wb") as f:
                f.write(base64.b64decode(im["b64"]))
            tag = '<img src="assets/img/%s" alt="%s">' % (fname, im["alt"])
            where = insert_img(c, ref_of(im["alt"]), im["alt"], tag)
            added.append((cid, fname, im["alt"], where))
            db_hashes.add(im["md5"])

    if added:
        out = pre + json.dumps(db, ensure_ascii=False, separators=(",", ":")) + post
        io.open(QJS, "w", encoding="utf-8").write(out)
    print("补充图片:", len(added))
    for cid, fname, alt, where in added:
        print(f"  {cid} <- {fname} | {alt[:26]} | {where}")

if __name__ == "__main__":
    main()
