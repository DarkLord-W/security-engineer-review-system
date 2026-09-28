# -*- coding: utf-8 -*-
"""v1.6: 补 C-2019-1-4#1 表注；清理 C-2022-2-4#5 末尾的"文档结束"残留。
自动备份 questions.js -> questions.js.bak7；可重复执行（幂等）。
用法: python scripts/fix_notes_v16.py
"""
import io, json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QJS = os.path.join(ROOT, "data", "questions.js")
BAK = os.path.join(ROOT, "data", "questions.js.bak7")
PREFIX = "/*自动生成 请勿手改*/\nwindow.DB="

NOTE = "\n\n注：表中“*”表示通配符，任意服务端口都有两条规则。"


def load(p, var="window.DB"):
    raw = io.open(p, encoding="utf-8").read()
    return json.loads(raw[raw.index(var + "=") + len(var) + 1: raw.rindex(";")])


def sub(cid, no):
    return None


def main():
    db = load(QJS)
    changed = 0

    def get(cid, no):
        for s in db["cases"][cid]["qs"]:
            if s.get("no") == no:
                return s
        return None

    # 1) C-2019-1-4#1 补表注
    s = get("C-2019-1-4", 1)
    if s is not None:
        t = s.get("text") or ""
        if "任意服务端口都有两条规则" not in t:
            s["text"] = t.rstrip() + NOTE
            changed += 1
            print("补表注: C-2019-1-4#1")
        else:
            print("表注已存在: C-2019-1-4#1")

    # 2) 清理"文档结束"残留
    for cid, c in db["cases"].items():
        for s in c["qs"]:
            t = s.get("text") or ""
            nt = t
            for pat in ("\n— 文档结束 —", "— 文档结束 —", "\n—文档结束—", "—文档结束—"):
                nt = nt.replace(pat, "")
            nt = nt.rstrip()
            if nt != t:
                s["text"] = nt
                changed += 1
                print("清理残留: %s#%s" % (cid, s["no"]))

    if not changed:
        print("无改动")
        return
    if not os.path.exists(BAK):
        shutil.copy2(QJS, BAK)
        print("已备份 -> data/questions.js.bak7")
    body = json.dumps(db, ensure_ascii=False, separators=(",", ":"))
    io.open(QJS, "w", encoding="utf-8", newline="\n").write(PREFIX + body + ";\n")
    print("已写入 data/questions.js | 改动", changed, "项")


if __name__ == "__main__":
    main()
