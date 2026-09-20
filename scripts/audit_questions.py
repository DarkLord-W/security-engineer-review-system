# -*- coding: utf-8 -*-
"""全量题目数据审计：题干/选项/答案/组题材料/单元与计划链接。
用法: python scripts/audit_questions.py
报告输出: 资料/questions_audit_report.md
"""
import io, json, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_js(p, var):
    raw = io.open(p, encoding="utf-8").read()
    return json.loads(raw[raw.index(var + "=") + len(var) + 1: raw.rindex(";")])


def load_plan_refs(p):
    raw = io.open(p, encoding="utf-8").read()
    i = raw.index("window.PLAN")
    return sorted(set(re.findall(r"C-\d{4}-\d-\d+", raw[i:])))


def main():
    db = load_js(os.path.join(ROOT, "data", "questions.js"), "window.DB")
    cards = load_js(os.path.join(ROOT, "data", "cards.js"), "window.CARDS")
    plan_refs = load_plan_refs(os.path.join(ROOT, "data", "plan.js"))
    groups = db.get("groups", {})
    issues, warns = [], []

    nq = ncase = nsub = 0
    grouped = 0
    for qid, q in db["questions"].items():
        nq += 1
        if len(q.get("options") or []) != 4:
            issues.append("[选择] %s 选项数≠4" % qid)
        if not (q.get("answer") or "").strip():
            issues.append("[选择] %s 缺答案" % qid)
        if not (q.get("stem") or "").strip():
            g = groups.get(q.get("group") or "")
            if g and (g.get("stem") or "").strip():
                grouped += 1
            else:
                issues.append("[选择] %s 题干为空且无组题材料" % qid)
        if q.get("group") and q["group"] not in groups:
            issues.append("[选择] %s 组题引用不存在: %s" % (qid, q["group"]))

    for cid, c in db["cases"].items():
        ncase += 1
        if not (c.get("scenario") or "").strip():
            warns.append("[案例] %s 无案例背景" % cid)
        for s in c["qs"]:
            nsub += 1
            tag = "%s#%s" % (cid, s.get("no"))
            t = s.get("text") or ""
            if not t.strip():
                issues.append("[案例] %s 缺题干" % tag)
            if not (s.get("answer") or "").strip():
                issues.append("[案例] %s 缺答案" % tag)
            if "【答案】" in t:
                warns.append("[案例] %s 题干内含【答案】(疑似合并块)" % tag)
            if re.search(r"【问题\s*\d+\s*至问题", t) or len(re.findall(r"问题\s*\d+\s*[.．、）)]", t)) >= 2:
                issues.append("[案例] %s 疑似合并题块（应拆分为独立小题）" % tag)

    meta = cards.get("meta", {})
    for k in list(meta.get("cunit", {})) + list(meta.get("cunitX", {})):
        cid, _, no = k.partition("#")
        c = db["cases"].get(cid)
        if not c or not any(str(s.get("no")) == no for s in c["qs"]):
            issues.append("[链接] 案例单元映射失效: %s" % k)
    for qid in list(meta.get("qunit", {})) + list(meta.get("qunitX", {})):
        if qid not in db["questions"]:
            issues.append("[链接] 选择单元映射失效: %s" % qid)

    for cid in plan_refs:
        if cid not in db["cases"]:
            issues.append("[计划] 引用不存在: %s" % cid)

    lines = []
    lines.append("# 题库数据审计报告")
    lines.append("")
    lines.append("- 生成时间: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    lines.append("- 选择题: %d 道（其中组题 %d 道，题干在共享材料中）" % (nq, grouped))
    lines.append("- 案例: %d 道 / 小题 %d 问" % (ncase, nsub))
    lines.append("- 单元: %d 个" % len(cards.get("units", [])))
    lines.append("- 严重问题: %d | 提示: %d" % (len(issues), len(warns)))
    lines.append("")
    if issues:
        lines.append("## 严重问题")
        lines += ["- " + x for x in issues]
        lines.append("")
    if warns:
        lines.append("## 提示")
        lines += ["- " + x for x in warns]
        lines.append("")
    if not issues and not warns:
        lines.append("## 全部通过 ✅")
        lines.append("")
    out = os.path.join(ROOT, "资料", "questions_audit_report.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    io.open(out, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print("选择题 %d（组题 %d）| 案例 %d/%d 问 | 单元 %d" % (nq, grouped, ncase, nsub, len(cards.get("units", []))))
    print("严重问题 %d | 提示 %d" % (len(issues), len(warns)))
    for x in issues[:20]:
        print("  ✗", x)
    for x in warns[:10]:
        print("  !", x)
    print("报告 -> 资料/questions_audit_report.md")
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
