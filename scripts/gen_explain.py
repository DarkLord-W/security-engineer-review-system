# -*- coding: utf-8 -*-
"""为46道案例题生成详细讲解 -> data/explain.js (断点续传)"""
import json, re, os, time, io, html, urllib.request, urllib.error, threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYF = os.path.join(ROOT, "scripts", ".llmkey")
QJS = os.path.join(ROOT, "data", "questions.js")
OUT = os.path.join(ROOT, "data", "explain.js")
LOG = os.path.join(ROOT, "scripts", "explain.log")


def log(m):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(m + "\n")
    print(m, flush=True)


cfg = {}
for ln in open(KEYF, encoding="utf-8-sig"):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1); cfg[k.strip()] = v.strip()
PROVIDER, KEY = cfg.get("provider", "deepseek"), cfg.get("key", "")
PRIMARY = cfg.get("model", "deepseek-flash")
URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions" if PROVIDER == "glm" else "https://api.deepseek.com/chat/completions"
CHAIN = [PRIMARY, "glm-5.3-flash", "glm-4.7"] if PROVIDER == "glm" else [PRIMARY, "deepseek-v4-pro"]
CHAIN = list(dict.fromkeys(m for m in CHAIN if m))
MAXTOK = int(cfg.get("explain_maxtokens", "6000"))
log(f"== 案例详细讲解生成 provider={PROVIDER} 链={' -> '.join(CHAIN)} ==")

raw = io.open(QJS, encoding="utf-8").read()
db = json.loads(raw[raw.index("window.DB=") + len("window.DB="): raw.rindex("}") + 1])

explain = {}
if os.path.exists(OUT):
    try:
        t = io.open(OUT, encoding="utf-8").read()
        explain = json.loads(t[t.index("window.EXPLAIN=") + len("window.EXPLAIN="): t.rindex(";")])
        log(f"续传: 已有 {len(explain)} 条")
    except Exception as e:
        log(f"读取已有失败: {e}")


def to_text(s):
    s = re.sub(r'(?s)<table.*?</table>', lambda m: re.sub(r'</t[dh]>', ' | ', re.sub(r'<[^>]+>', ' ', m.group(0))) + '\n', s or '')
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n\s*\n+', '\n', s)
    return s.strip()


def case_prompt(c):
    parts = [f"【题目】{c.get('year')}年{'下' if c.get('half') == 2 else '上'}试题{c.get('cn')}《{c.get('title','')}》",
             "【案例背景】", to_text(c.get("scenario"))[:900]]
    for q in c.get("qs", []):
        parts.append(f"【问题{q['no']}】" + to_text(q.get("text"))[:350])
        if q.get("answer"):
            parts.append("参考答案：" + to_text(q.get("answer"))[:280])
        if q.get("analysis"):
            parts.append("官方解析：" + to_text(q.get("analysis"))[:200])
    return "\n".join(parts)


SYS = "你是全国软考中级·信息安全工程师的资深辅导讲师，熟悉历年真题与考纲重点。严格只输出JSON，不要输出任何其他文字。"
TPL = """请为下面这道历年案例真题生成"详细讲解"，帮助考生理解并记忆。
{case}
输出JSON格式：
{{"kaodian":"考点地图：本题涉及哪些知识点、对应教材位置、命题意图，120字内",
"jieti":"逐步解题：按小问逐步讲清怎么想、怎么答；计算题必须写公式、代入过程、计算步骤与验算方法；可分步换行",
"yicuodian":"易错点：考生常见错误与避坑提示，120字内",
"koujue":"记忆口诀：一句话口诀或对比记忆法，40字内"}}"""


def extract_json(txt):
    if not txt:
        raise ValueError("empty")
    m = re.search(r'\{[\s\S]*\}', txt)
    if not m:
        raise ValueError("no json: " + txt[:80])
    return json.loads(m.group(0))


def chat(c):
    usr = TPL.format(case=case_prompt(c))
    last = None
    for model in CHAIN:
        for attempt in range(2):
            body = {"model": model, "messages": [{"role": "system", "content": SYS}, {"role": "user", "content": usr}],
                    "temperature": 0.3, "max_tokens": MAXTOK, "stream": False}
            if PROVIDER == "deepseek":
                body["response_format"] = {"type": "json_object"}
            try:
                req = urllib.request.Request(URL, data=json.dumps(body).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": "Bearer " + KEY})
                with urllib.request.urlopen(req, timeout=120) as r:
                    j = json.loads(r.read().decode("utf-8"))
                msg = j["choices"][0]["message"]
                txt = msg.get("content") or ""
                if not txt.strip():
                    txt = msg.get("reasoning_content") or ""
                d = extract_json(txt)
                return {"kaodian": str(d.get("kaodian", ""))[:400], "jieti": str(d.get("jieti", ""))[:2200],
                        "yicuodian": str(d.get("yicuodian", ""))[:400], "koujue": str(d.get("koujue", ""))[:120],
                        "model": model}
            except urllib.error.HTTPError as e:
                last = f"{model} HTTP{e.code}"
                if e.code == 429:
                    time.sleep(2); break
                time.sleep(2); break
            except Exception as e:
                last = f"{model} {str(e)[:80]}"
                time.sleep(3)
    raise RuntimeError("全链失败: " + str(last))


lock = threading.Lock()
fail = 0


def worker(chunk):
    global fail
    for cid, c in chunk:
        if cid in explain:
            continue
        try:
            r = chat(c)
            with lock:
                explain[cid] = r
        except Exception as e:
            with lock:
                fail += 1
            log(f"[失败] {cid}: {str(e)[:100]}")


def save_all():
    with lock:
        with io.open(OUT, "w", encoding="utf-8") as f:
            f.write("/*AI生成 自动生成*/\nwindow.EXPLAIN=")
            f.write(json.dumps(explain, ensure_ascii=False, separators=(",", ":"))); f.write(";\n")


todo = [(cid, c) for cid, c in db["cases"].items() if cid not in explain]
log(f"待生成 {len(todo)} / {len(db['cases'])}")
chunks = [todo[i::3] for i in range(3)]
threads = [threading.Thread(target=worker, args=(ch,), daemon=True) for ch in chunks]
for t in threads:
    t.start()
last_n = 0
while any(t.is_alive() for t in threads):
    time.sleep(15)
    if len(explain) != last_n:
        last_n = len(explain)
        save_all()
        log(f"[进度] 已存 {len(explain)}/{len(db['cases'])} 失败 {fail}")
for t in threads:
    t.join()
save_all()
log(f"== 完成: 成功 {len(explain)} 失败 {fail} ==")
