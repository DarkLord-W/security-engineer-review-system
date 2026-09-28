# -*- coding: utf-8 -*-
"""句子级核对：把 PDF书 OCR 中 2018-2022 案例各题的句子逐句与题库比对，
输出"书中存在、题库缺失"的句子清单。
报告: 资料/questions_audit_report_2018-2022.md  （追加/覆盖句子级部分）
用法: set OCRTXT=... && python scripts/audit_book_sentences.py
"""
import io, json, os, re, sys, difflib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QJS = os.path.join(ROOT, "data", "questions.js")
OCRTXT = os.environ.get("OCRTXT") or os.path.join(ROOT, "资料", "ocr_full.txt")
REPORT = os.path.join(ROOT, "资料", "questions_audit_report_2018-2022.md")

# 章 -> (year, half)
CH = {2: (2018, 1), 4: (2019, 1), 6: (2020, 2), 8: (2021, 2), 10: (2022, 2)}
CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5}


def load(p, var="window.DB"):
    raw = io.open(p, encoding="utf-8").read()
    return json.loads(raw[raw.index(var + "=") + len(var) + 1: raw.rindex(";")])


def norm(s):
    s = re.sub(r"\$[^$]*\$", "", s or "")
    s = re.sub(r"<[^>]*>", "", s)
    s = re.sub(r"\[[^\]]*\]\([^)]*\)", "", s)
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "", s)
    return s


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

    # 按章聚合
    chaps = {}
    for pg, txt in pages:
        m = re.search(r"第\s*(\d+)\s*章", txt[:120])
        if m:
            chaps[int(m.group(1))] = chaps.get(int(m.group(1)), "") + txt

    missing = []
    checked = 0
    for ch, (year, half) in CH.items():
        seg = chaps.get(ch, "")
        if not seg:
            continue
        # 按试题切分
        exams = [(m.start(), CN.get(m.group(1), 0)) for m in re.finditer(r"试题\s*([一二三四五])", seg)]
        exams.append((len(seg), 0))
        for j in range(len(exams) - 1):
            es, cn = exams[j]
            if not cn:
                continue
            ee = exams[j + 1][0]
            part = seg[es:ee]
            # 只取"试题X分析"之前（即题目部分）
            cut = re.search(r"试题\s*[一二三四五]\s*分析", part)
            qpart = part[:cut.start()] if cut else part
            qs = [(m.start(), m.end(), int(m.group(1))) for m in re.finditer(r"【\s*问题\s*(\d+)\s*】", qpart)]
            qs.append((len(qpart), len(qpart), 0))
            for x in range(len(qs) - 1):
                s0, e0, no = qs[x]
                if not no:
                    continue
                body = qpart[e0:qs[x + 1][0]]
                # 去掉紧随其后的"分析/参考答案"
                body = re.split(r"【\s*问题\s*" + str(no) + r"\s*】\s*分析|参考答案|试题\s*[一二三四五]\s*分析", body)[0]
                body = re.sub(r"^\s*[（(]\s*[\d\.]+\s*分\s*[）)]", "", body.strip())
                cid = "C-%d-%d-%d" % (year, half, cn)
                c = db["cases"].get(cid)
                if not c:
                    continue
                sub = None
                for z in c["qs"]:
                    if z.get("no") == no:
                        sub = z
                        break
                if not sub:
                    continue
                checked += 1
                dbt = norm(sub.get("text"))
                # 把书里的题干按句切分
                body = re.sub(r"\s+", "", body)
                for sent in re.split(r"[。.？?！!；;]", body):
                    sn = norm(sent)
                    if len(sn) < 8:
                        continue
                    sm = difflib.SequenceMatcher(None, sn, dbt)
                    m = sm.find_longest_match(0, len(sn), 0, len(dbt))
                    if m.size < max(6, int(len(sn) * 0.62)):
                        missing.append((cid, no, sent.strip()[:90]))
    lines = ["# 2018-2022 案例题目 · 句子级核对（书 vs 题库）", "",
             "- 核对的小题数: %d" % checked,
             "- 书中存在、题库可能缺失的句子: %d" % len(missing), ""]
    if missing:
        lines.append("## 可能缺失的句子")
        for cid, no, t in missing:
            lines.append("- `%s#%s` %s" % (cid, no, t))
        lines.append("")
    else:
        lines.append("## 全部通过 ✅")
        lines.append("")
    io.open(REPORT, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print("核对小题:", checked, "| 可能缺失句子:", len(missing))
    for x in missing:
        print("  MISS", x)
    print("报告 ->", REPORT)


if __name__ == "__main__":
    main()
