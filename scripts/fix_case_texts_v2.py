# -*- coding: utf-8 -*-
"""v1.4 案例文本修复：
1) 补全 2023-2025 整理版被删的前置句/条件（14 处，用往年重复真题完整原文）
2) 拆分 2 个 2025 合并题块（C-2025-2-3 -> 6 问；C-2025-2-4 -> 3 问）
自动备份 questions.js -> questions.js.bak5；可重复执行（幂等）。
用法: python scripts/fix_case_texts_v2.py
"""
import io, json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QJS = os.path.join(ROOT, "data", "questions.js")
BAK = os.path.join(ROOT, "data", "questions.js.bak5")
PREFIX = "/*自动生成 请勿手改*/\nwindow.DB="

# (cid, no) -> 补全规则
PATCHES = [
    # C-2023-2-3#1 插入缺失条件句（在问句之后、图之前）
    ("C-2023-2-3", 1, {"insert_after": "能否互换计算顺序？",
                       "insert": "如果不能互换请说明原因，如果能互换请说明对安全目标的影响。"}),
    ("C-2023-2-4", 1, {"prepend": "访问 Windows 系统中的日志记录有多种方法，请问"}),
    ("C-2023-2-4", 2, {"prepend": "Windows 系统通过事件 ID 来记录不同的系统行为，"}),
    ("C-2023-2-4", 3, {"prepend": "王工通过对攻击流量的关联分析定位到了图 3-2 所示的网络分组，"}),
    ("C-2023-2-4", 5, {"prepend": "Windows 系统提供的日志有三种类型，分别是系统日志、应用程序日志和安全日志，请问"}),
    ("C-2023-2-4", 7, {"prepend": "Windows 系统为了实现安全的远程登录使用了 tls 协议，请问图 3-2 中，",
                       "append": "请给出对应数据包的序号。"}),
    ("C-2023-2-4", 8, {"prepend": "网络安全事件可分为有害程序事件、网络攻击事件、信息破坏事件、信息内容安全事件、设备设施故障、灾害性事件和其他事件。请问"}),
    ("C-2023-2-4", 9, {"replace": ["三大安全目标中的", "三大安全目标（保密性、完整性、可用性）中的"]}),
    ("C-2024-2-3", 1, {"prepend": "身份认证可以通过用户知道什么、用户拥有什么和用户的生理特征等方法来验证。请问"}),
    ("C-2024-2-4", 1, {"prepend": "信息安全的基本目标包括：真实性、保密性、完整性、不可否认性、可控性、可用性、可审查性等。"}),
    ("C-2024-2-4", 2, {"prepend": "RSA公钥密码是一种基于大整数因子分解难题的公开密钥密码。"}),
    ("C-2024-2-4", 5, {"prepend": "在 RSA 公钥算法中，"}),
    ("C-2024-2-4", 6, {"prepend": "在 RSA 密码中，"}),
    ("C-2024-2-4", 7, {"set": "是否可以直接使用RSA密码进行数字签名？如果可以，请给出消息m的数字签名计算公式。如果不可以，请给出原因。"}),
]

# 2025 合并块拆分
SPLITS = {
    "C-2025-2-3": [
        ("针对跨站伪造请求攻击可以采用哪些安全服务来解决或者缓解？", "①（认证服务）"),
        ("针对口令明文传输漏洞攻击可以采用哪些安全服务来解决或者缓解？", "③（数据保密性服务）"),
        ("针对 Smurf 攻击可以采用哪些安全服务来解决或者缓解？", "⑦（可用性服务）"),
        ("针对签名伪造攻击可以采用哪些安全服务来解决或者缓解？", "⑤（抗否认性服务）"),
        ("针对攻击进行追踪溯源时，可以采用哪些安全服务？", "⑥（审计服务）"),
        ("如果下载的软件被植入木马，可以采用哪些安全服务来进行解决或者缓解？", "④（数据完整性服务）"),
    ],
    "C-2025-2-4": [
        ("针对信息系统的访问控制包含哪三个基本要素？", "主体、客体、授权访问。"),
        ("BLP模型是一种强制访问控制模型，请问：(1) BLP模型保证了信息的机密性还是完整性？(2) BLP模型采用的访问控制策略是上读下写还是下读上写？",
         "(1) 机密性；(2) 下读上写。"),
        ("Linux系统中可以通过ls命令查看文件的权限，例如：文件net.txt的权限属性如下所示：-rwx---- 1 root root 5025 May 25 2019 /home/abc/net.txt　请问：(1)文件net.txt属于系统的哪个用户？(2)文件net.txt权限的数字表示是什么？",
         "(1) root用户；(2) 700。"),
    ],
}


def load(p, var="window.DB"):
    raw = io.open(p, encoding="utf-8").read()
    return json.loads(raw[raw.index(var + "=") + len(var) + 1: raw.rindex(";")])


def find_sub(case, no):
    for s in case["qs"]:
        if s.get("no") == no:
            return s
    return None


def main():
    db = load(QJS)
    changed = 0

    for cid, no, rule in PATCHES:
        c = db["cases"].get(cid)
        if not c:
            print("跳过（案例不存在）:", cid)
            continue
        s = find_sub(c, no)
        if not s:
            print("跳过（小题不存在）:", cid, no)
            continue
        t = s.get("text") or ""
        if "set" in rule:
            if t == rule["set"]:
                continue
            s["text"] = rule["set"]
        else:
            if "prepend" in rule and not t.startswith(rule["prepend"]):
                t = rule["prepend"] + t
            if "append" in rule and not t.endswith(rule["append"]):
                t = t + rule["append"]
            if "insert_after" in rule:
                anchor = rule["insert_after"]
                if rule["insert"] not in t and anchor in t:
                    t = t.replace(anchor, anchor + rule["insert"], 1)
            if "replace" in rule:
                old, new = rule["replace"]
                if old in t:
                    t = t.replace(old, new)
            if t != (s.get("text") or ""):
                s["text"] = t
            else:
                continue
        changed += 1
        print("补全:", cid + "#" + str(no))

    for cid, items in SPLITS.items():
        c = db["cases"].get(cid)
        if not c:
            print("跳过（案例不存在）:", cid)
            continue
        merged = c["qs"][0] if len(c["qs"]) == 1 and "【问题" in (c["qs"][0].get("text") or "") else None
        if merged is None:
            if len(c["qs"]) == len(items):
                continue
            print("跳过（非合并块状态）:", cid)
            continue
        new_subs = []
        for i, (text, ans) in enumerate(items, 1):
            new_subs.append({"no": i, "text": text, "score": None,
                             "answer": ans, "analysis": None, "reconstructed": False})
        c["qs"] = new_subs
        changed += 1
        print("拆分:", cid, "->", len(new_subs), "问")

    if not changed:
        print("无改动（已是目标状态）")
        return
    if not os.path.exists(BAK):
        shutil.copy2(QJS, BAK)
        print("已备份 -> data/questions.js.bak5")
    body = json.dumps(db, ensure_ascii=False, separators=(",", ":"))
    io.open(QJS, "w", encoding="utf-8", newline="\n").write(PREFIX + body + ";\n")
    print("已写入 data/questions.js | 改动", changed, "项")


if __name__ == "__main__":
    main()
