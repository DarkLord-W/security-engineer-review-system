# -*- coding: utf-8 -*-
"""补齐案例小题->知识点映射(cunitX), 重算考频。不重跑AI。"""
import json, io, os, re, shutil
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARDS_F = os.path.join(ROOT, "data", "cards.js")
QJS_F = os.path.join(ROOT, "data", "questions.js")


def load_var(path, var):
    raw = io.open(path, encoding="utf-8").read()
    return json.loads(raw[raw.index(var + "=") + len(var) + 1: raw.rindex(";")])


def dump_var(path, var, obj):
    with io.open(path, "w", encoding="utf-8") as f:
        f.write("/*自动生成*/\n" + var + "=")
        f.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":")))
        f.write(";\n")


cards = load_var(CARDS_F, "window.CARDS")
db = load_var(QJS_F, "window.DB")
meta = cards["meta"]
units = cards["units"]
by_id = {u["id"]: u for u in units}
cunit = meta.get("cunit", {})
cunitX = {k: list(v) for k, v in meta.get("cunitX", {}).items()}

RULES = [
    (r"影响等级|不适用|安全分类|机密性|完整性|可用性|CIA", ["U1.3", "U1.4"]),
    (r"DES|S盒|初始置换|分组密码|弱密钥|加密|解密|密钥", ["U3.3"]),
    (r"仿射|乘法逆元|明文|密文", ["U3.3"]),
    (r"RSA|公钥|私钥|数字签名|签名", ["U3.4", "U3.3"]),
    (r"心跳包|模糊测试|缓冲区|溢出|栈|内存布局|编译选项|GS|代码", ["U2.3.3"]),
    (r"DNS|域名|TXT", ["U2.5"]),
    (r"SQL|数据库|MySQL|Oracle", ["U20.1"]),
    (r"网站|Web|HTTP|URL", ["U22.1"]),
    (r"等保|测评|等级保护", ["U18.1"]),
    (r"口令|密码|认证|身份", ["U6.1"]),
    (r"数据|隐私|脱敏", ["U26.1", "U15.8"]),
    (r"日志|事件|审计", ["U12.1"]),
    (r"权限|访问控制|主体|客体", ["U7.1"]),
]

uncovered_before = []
for cid, c in db["cases"].items():
    for q in c.get("qs", []):
        key = f"{cid}#{q['no']}"
        if key in cunit or key in cunitX:
            continue
        blob = " ".join([c.get("title") or "", c.get("scenario") or "", q.get("text") or "",
                         q.get("answer") or "", q.get("analysis") or ""])
        add = []
        for pat, targets in RULES:
            if re.search(pat, blob):
                for t in targets:
                    if t in by_id and t not in add:
                        add.append(t)
                if add:
                    break
        if add:
            cunitX[key] = add
        else:
            uncovered_before.append((key, (q.get("text") or "")[:50]))

meta["cunitX"] = cunitX

# 重算考频
freq = defaultdict(int)
for qid, uid in meta.get("qunit", {}).items():
    freq[uid] += 1
for qid, uids in meta.get("qunitX", {}).items():
    for uid in uids:
        freq[uid] += 1
for key, uid in cunit.items():
    freq[uid] += 1
for key, uids in cunitX.items():
    for uid in uids:
        freq[uid] += 1
for u in units:
    u["freq"] = freq.get(u["id"], 0)

total = sum(len(c["qs"]) for c in db["cases"].values())
covered = len(set(cunit) | set(cunitX))
print(f"案例小题映射: {covered}/{total}")
if uncovered_before:
    print("仍未覆盖:", uncovered_before)

if not os.path.exists(CARDS_F + ".bak2"):
    shutil.copy2(CARDS_F, CARDS_F + ".bak2")
    print("备份:", CARDS_F + ".bak2")
dump_var(CARDS_F, "window.CARDS", cards)
print("完成")
