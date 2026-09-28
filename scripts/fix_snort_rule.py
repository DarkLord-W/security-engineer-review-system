# -*- coding: utf-8 -*-
"""v1.6: 补入 2021下半年 试题一 问题5 的 Snort 规则行。
该行在"整理版HTML"与 MinerU 书摘中均缺失（只有答案 alert/union），据 PDF 原页补录。
自动备份 questions.js -> questions.js.bak6；可重复执行（幂等）。
用法: python scripts/fix_snort_rule.py
"""
import io, json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QJS = os.path.join(ROOT, "data", "questions.js")
BAK = os.path.join(ROOT, "data", "questions.js.bak6")
PREFIX = "/*自动生成 请勿手改*/\nwindow.DB="

RULE = '____（a）____tcp  any any -> any any (msg:"XXX";content:"____（b）____";nocase;sid:1106;)'
ANCHOR = "填充空（a）、（b）处的内容。（2分）"


def load(p, var="window.DB"):
    raw = io.open(p, encoding="utf-8").read()
    return json.loads(raw[raw.index(var + "=") + len(var) + 1: raw.rindex(";")])


def main():
    db = load(QJS)
    c = db["cases"]["C-2021-2-1"]
    s = None
    for x in c["qs"]:
        if x.get("no") == 5:
            s = x
            break
    if not s:
        print("未找到 C-2021-2-1#5")
        return
    t = s.get("text") or ""
    if "sid:1106" in t:
        print("规则行已存在，无需修改")
        return
    if ANCHOR not in t:
        print("未找到锚点文本，跳过")
        return
    s["text"] = t.replace(ANCHOR, ANCHOR + "\n\n" + RULE, 1)
    if not os.path.exists(BAK):
        shutil.copy2(QJS, BAK)
        print("已备份 -> data/questions.js.bak6")
    body = json.dumps(db, ensure_ascii=False, separators=(",", ":"))
    io.open(QJS, "w", encoding="utf-8", newline="\n").write(PREFIX + body + ";\n")
    print("已补入 Snort 规则行 -> data/questions.js")


if __name__ == "__main__":
    main()
