# -*- coding: utf-8 -*-
"""修复上午场选择题: 补选项(从官方解析书MD) + 补答案(提取/AI推断+引文校验)
用法: python scripts/fix_quiz_missing.py
"""
import json, io, os, re, shutil, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QJS = os.path.join(ROOT, "data", "questions.js")
MD = os.path.join(ROOT, "资料", "MinerU_markdown_信息安全工程师2018至2022试题分析与解答_(清华大学出版社)_(z-library.sk,_1lib.sk,_z-lib.sk)_2093262293397954560.md")
KEYF = os.path.join(ROOT, "scripts", ".llmkey")


def load_var(path, var):
    raw = io.open(path, encoding="utf-8").read()
    return json.loads(raw[raw.index(var + "=") + len(var) + 1: raw.rindex(";")])


def dump_var(path, var, obj):
    with io.open(path, "w", encoding="utf-8") as f:
        f.write("/*自动生成 请勿手改*/\n" + var + "=")
        f.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":")))
        f.write(";\n")


# ---------- 解析 MD 上午卷 ----------
txt = io.open(MD, encoding="utf-8").read()
am_sections = {}
for m in re.finditer(r'#+ 第\s*\d+\s*章\s*(\d{4})\s*([上下])半年信息安全工程师(.*?)(?=#+ 第\s*\d+\s*章|$)', txt, re.S):
    year = int(m.group(1)); half = 1 if m.group(2) == '上' else 2
    body = m.group(3)
    if '上午试题分析与解答' in body:
        am_sections[(year, half)] = body.split('下午试题分析与解答')[0]


def find_options(am, num):
    m = re.search(r'[（(]\s*' + str(num) + r'\s*[）)]\s*A[.、．]\s*', am)
    if not m:
        return None
    seg = am[m.end(): m.end() + 400]
    parts = re.split(r'\s*([B-D])[.、．]\s*', seg, maxsplit=3)
    if len(parts) >= 7:
        def clean(s):
            return re.sub(r'\s+', ' ', s.split('\n')[0]).strip()[:80]
        return {'A': clean(parts[0]), 'B': clean(parts[2]), 'C': clean(parts[4]), 'D': clean(parts[6])}
    return None


def find_answer(am, num):
    pats = [
        r'参考答案\s*[（(]\s*' + str(num) + r'\s*[）)]\s*([A-D])',
        r'[（(]\s*' + str(num) + r'\s*[）)]\s*([A-D])(?=\s*(?:\n|$))',
        r'参考答案\s*([A-D])\b',
    ]
    for p in pats:
        ms = list(re.finditer(p, am))
        if ms:
            return ms[-1].group(1)
    return None


def strip_inline_options(stem, num):
    pat = r'[（(]\s*' + str(num) + r'\s*[）)]\s*A[.、．][\s\S]*$'
    m = re.search(pat, stem)
    if m and ('B.' in m.group(0) or 'B、' in m.group(0)):
        return stem[:m.start()].rstrip()
    return stem


db = load_var(QJS, "window.DB")
fixed_opt = 0; fixed_ans = 0
need_ai = []
for qid, q in db["questions"].items():
    if q.get("subject") != 1:
        continue
    am = am_sections.get((q["year"], q["half"]), "")
    if not am:
        continue
    if len(q.get("options") or []) != 4:
        o = find_options(am, q["num"])
        if o:
            q["options"] = [{"key": k, "text": o[k]} for k in "ABCD"]
            q["stem"] = strip_inline_options(q.get("stem") or "", q["num"])
            fixed_opt += 1
    if not q.get("answer"):
        a = find_answer(am, q["num"])
        if a:
            q["answer"] = a
            fixed_ans += 1
        else:
            need_ai.append(qid)
print(f"MD提取修复: 选项 {fixed_opt} 题, 答案 {fixed_ans} 题")
print(f"需AI推断答案: {len(need_ai)} 题: {need_ai}")

# ---------- AI 推断缺失答案(引文校验) ----------
cfg = {}
if os.path.exists(KEYF):
    for ln in open(KEYF, encoding="utf-8-sig"):
        ln = ln.strip()
        if "=" in ln and not ln.startswith("#"):
            k, v = ln.split("=", 1); cfg[k.strip()] = v.strip()
PROVIDER, KEY = cfg.get("provider", "deepseek"), cfg.get("key", "")
PRIMARY = cfg.get("model", "deepseek-flash")
URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions" if PROVIDER == "glm" else "https://api.deepseek.com/chat/completions"
CHAIN = [PRIMARY, "deepseek-v4-pro"]
SYS = "你是软考中级信息安全工程师的资深辅导讲师。严格只输出JSON，不要输出任何其他文字。"


def norm(s):
    return re.sub(r'\s+', '', str(s or ''))


def ai_answer(q):
    opts = " ".join("%s. %s" % (o["key"], o["text"]) for o in (q.get("options") or []))
    usr = ("下面是软考信息安全工程师上午选择题。请根据官方解析推断正确答案。\n"
           "【题干】%s\n【选项】%s\n【官方解析】%s\n"
           '输出JSON：{"answer":"A/B/C/D","quote":"解析中能支持该答案的原文片段(必须逐字摘自解析)","reason":"20字内"}'
           "\n若解析不足以判断，answer 填空字符串。") % (q.get("stem") or "", opts, (q.get("analysis") or "")[:900])
    last = None
    for model in CHAIN:
        for attempt in range(2):
            body = {"model": model, "messages": [{"role": "system", "content": SYS}, {"role": "user", "content": usr}],
                    "temperature": 0.2, "max_tokens": 1200, "stream": False}
            if PROVIDER == "deepseek":
                body["response_format"] = {"type": "json_object"}
            try:
                req = urllib.request.Request(URL, data=json.dumps(body).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": "Bearer " + KEY})
                with urllib.request.urlopen(req, timeout=120) as r:
                    j = json.loads(r.read().decode("utf-8"))
                msg = j["choices"][0]["message"]
                t = msg.get("content") or msg.get("reasoning_content") or ""
                m = re.search(r'\{[\s\S]*\}', t)
                if not m:
                    raise ValueError("no json")
                return json.loads(m.group(0))
            except urllib.error.HTTPError as e:
                last = "HTTP%d" % e.code; time.sleep(2); break
            except Exception as e:
                last = str(e)[:60]; time.sleep(2)
    raise RuntimeError(last)


ai_ok = 0; ai_fail = []
if need_ai and KEY:
    for qid in need_ai:
        q = db["questions"][qid]
        try:
            d = ai_answer(q)
            ans = str(d.get("answer", "")).strip().upper()
            quote = str(d.get("quote", "")).strip()
            if ans in "ABCD" and quote and norm(quote) in norm(q.get("analysis") or ""):
                q["answer"] = ans
                q["answer_src"] = "ai"
                q["answer_quote"] = quote[:120]
                ai_ok += 1
                print(f"  [AI] {qid} -> {ans} | 依据: {quote[:40]}")
            else:
                ai_fail.append((qid, ans, "引文校验失败" if ans in "ABCD" else "无法判断"))
        except Exception as e:
            ai_fail.append((qid, "", str(e)[:60]))
print(f"AI推断成功: {ai_ok} | 失败: {len(ai_fail)} {ai_fail}")

# ---------- 写回 ----------
if not os.path.exists(QJS + ".bak3"):
    shutil.copy2(QJS, QJS + ".bak3")
    print("备份:", QJS + ".bak3")
dump_var(QJS, "window.DB", db)

bad_opt = sum(1 for q in db["questions"].values() if q.get("subject") == 1 and len(q.get("options") or []) != 4)
bad_ans = sum(1 for q in db["questions"].values() if q.get("subject") == 1 and not q.get("answer"))
print(f"复检: 选项≠4 = {bad_opt} | 缺答案 = {bad_ans}")
