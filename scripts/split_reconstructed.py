# -*- coding: utf-8 -*-
"""拆分"逆推"合并题块为独立小题（题干/答案/解析分离），并自动备份 questions.js。
用法: python scripts/split_reconstructed.py
"""
import io, json, os, re, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QJS = os.path.join(ROOT, "data", "questions.js")
BAK = os.path.join(ROOT, "data", "questions.js.bak4")
PREFIX = "/*自动生成 请勿手改*/\nwindow.DB="


def load(p, var="window.DB"):
    raw = io.open(p, encoding="utf-8").read()
    return json.loads(raw[raw.index(var + "=") + len(var) + 1: raw.rindex(";")])


def parse_block(text):
    """把合并块解析为 [(no, question, answer, analysis), ...]"""
    out = []
    parts = re.split(r"\n\s*问题(\d+)（逆推）：", text)
    for i in range(1, len(parts), 2):
        no = int(parts[i])
        body = parts[i + 1] if i + 1 < len(parts) else ""
        m = re.search(r"【答案】([\s\S]*?)(?=\n\s*解析：|$)", body)
        if m:
            qtext = body[:m.start()]
            ans = m.group(1).strip()
        else:
            qtext = body
            ans = ""
        qtext = re.sub(r"\s+", " ", qtext).strip()
        m2 = re.search(r"解析：([\s\S]*)$", body)
        ana = re.sub(r"\s+", " ", m2.group(1)).strip() if m2 else None
        out.append((no, qtext, ans, ana))
    return out


def main():
    db = load(QJS)
    changed = 0
    for cid in ["C-2023-2-4", "C-2024-2-4"]:
        c = db["cases"][cid]
        qs = c["qs"]
        idx = None
        for i, s in enumerate(qs):
            if s.get("reconstructed") and "【问题" in (s.get("text") or ""):
                idx = i
                break
        if idx is None:
            print("跳过（未找到合并块）:", cid)
            continue
        items = parse_block(qs[idx]["text"])
        print(cid, "拆分", len(items), "题:", [x[0] for x in items])
        new_subs = []
        for no, qtext, ans, ana in items:
            new_subs.append({"no": no, "text": qtext, "score": None,
                             "answer": ans or None, "analysis": ana,
                             "reconstructed": True})
        c["qs"] = qs[:idx] + new_subs
        changed += 1
    if not changed:
        print("无改动")
        return
    if not os.path.exists(BAK):
        shutil.copy2(QJS, BAK)
        print("已备份 -> data/questions.js.bak4")
    body = json.dumps(db, ensure_ascii=False, separators=(",", ":"))
    io.open(QJS, "w", encoding="utf-8", newline="\n").write(PREFIX + body + ";\n")
    print("已写入 data/questions.js")


if __name__ == "__main__":
    main()
