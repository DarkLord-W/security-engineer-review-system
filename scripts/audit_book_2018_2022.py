# -*- coding: utf-8 -*-
"""用 PDF 全书 OCR 文本核对 2018-2022 案例题目是否有缺漏。
用法: set OCRTXT=<ocr文件> && python scripts/audit_book_2018_2022.py
报告: 资料/questions_audit_report_2018-2022.md
"""
import io, json, os, re, sys, difflib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QJS = os.path.join(ROOT, "data", "questions.js")
OCRTXT = os.environ.get("OCRTXT") or os.path.join(ROOT, "资料", "ocr_full.txt")
REPORT = os.path.join(ROOT, "资料", "questions_audit_report_2018-2022.md")


def load(p, var="window.DB"):
    raw = io.open(p, encoding="utf-8").read()
    return json.loads(raw[raw.index(var + "=") + len(var) + 1: raw.rindex(";")])


def norm(s):
    s = re.sub(r"\$[^$]*\$", "", s or "")
    s = re.sub(r"<[^>]*>", "", s)
    s = re.sub(r"\[[^\]]*\]\([^)]*\)", "", s)
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "", s)
    return s


def grams(s, n=6, step=2):
    if len(s) <= n:
        return [s] if s else []
    return [s[i:i + n] for i in range(0, len(s) - n + 1, step)]


def main():
    db = load(QJS)
    pages = []
    cur, buf = None, []
    for line in io.open(OCRTXT, encoding="utf-8"):
        m = re.match(r"=== PAGE (\d+) ===", line.strip())
        if m:
            if cur is not None:
                pages.append((cur, "".join(buf)))
            cur, buf = int(m.group(1)), []
        else:
            buf.append(line)
    if cur is not None:
        pages.append((cur, "".join(buf)))
    full_raw = "\n".join(t for _, t in pages)
    nf = norm(full_raw)
    print("OCR 页数:", len(pages), "| 文本长度:", len(full_raw))

    lows, total = [], 0
    for cid, c in sorted(db["cases"].items()):
        if not (2018 <= c["year"] <= 2022):
            continue
        for s in c["qs"]:
            total += 1
            a = norm(s.get("text"))
            if len(a) < 8:
                continue
            g = grams(a)
            hit = sum(1 for x in g if x in nf)
            ratio = hit / len(g) if g else 1.0
            if ratio < 0.6:
                lows.append((cid, s["no"], round(ratio, 2), (s.get("text") or "")[:80]))

    # 扫描 OCR 中的"填空/规则"行，看我们是否缺失
    rule_lines = []
    for ln in full_raw.split("\n"):
        t = ln.strip()
        if not t:
            continue
        if re.search(r"sid:\s*\d+", t) or re.search(r"[（(][abAB][）)]", t) and "____" in t:
            rule_lines.append(t)
    miss_rule = []
    for t in set(rule_lines):
        nt = norm(t)
        if nt and nt[:12] not in nf:
            pass
        if nt and nt not in nf:
            miss_rule.append(t)

    lines = ["# 2018-2022 案例题目 与 PDF书 OCR 核对报告", "",
             "- OCR 页数: %d" % len(pages),
             "- 核对案例小题: %d" % total,
             "- 命中率低（<0.6，疑似缺漏或OCR差异）: %d" % len(lows),
             "- OCR中疑似规则/填空行且我方未见: %d" % len(miss_rule), ""]
    if lows:
        lines.append("## 命中率低的小题（需人工/原页复核）")
        for cid, no, r, t in lows:
            lines.append("- %s#%s 命中率%.2f | %s" % (cid, no, r, t))
        lines.append("")
    if miss_rule:
        lines.append("## OCR 中的规则/填空行（我方可能缺失）")
        for t in miss_rule:
            lines.append("- " + t)
        lines.append("")
    if not lows and not miss_rule:
        lines.append("## 全部通过 ✅")
        lines.append("")
    io.open(REPORT, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print("命中率低:", len(lows), "| 疑似缺规则行:", len(miss_rule))
    for x in lows[:20]:
        print("  LOW", x)
    for x in miss_rule[:10]:
        print("  RULE", x)
    print("报告 -> 资料/questions_audit_report_2018-2022.md")


if __name__ == "__main__":
    main()
