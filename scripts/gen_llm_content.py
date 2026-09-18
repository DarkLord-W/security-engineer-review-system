# -*- coding: utf-8 -*-
"""AI预生成知识点讲解/记忆提示/敲记句 (断点续传, 限速)"""
import json, re, os, time, sys, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYF = os.path.join(ROOT, "scripts", ".llmkey")
UNITS = os.path.join(ROOT, "scripts", "units_for_llm.json")
OUTJS = os.path.join(ROOT, "data", "ai_content.js")
LOG = os.path.join(ROOT, "scripts", "pregen.log")

def log(m):
    with open(LOG, "a", encoding="utf-8") as f: f.write(m + "\n")
    print(m, flush=True)

cfg = {}
for ln in open(KEYF, encoding="utf-8-sig"):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1); cfg[k.strip()] = v.strip()
PROVIDER, KEY = cfg.get("provider", "deepseek"), cfg.get("key", "")
PRIMARY = cfg.get("model", "glm-4.7-flash")
URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions" if PROVIDER == "glm" else "https://api.deepseek.com/chat/completions"
# 模型降级链: flash优先, 限流/失败自动切换
CHAIN = [PRIMARY, "glm-5.3-flash", "glm-4.7"] if PROVIDER == "glm" else [PRIMARY, "deepseek-v4-pro"]
CHAIN = list(dict.fromkeys(m for m in CHAIN if m))
MAXTOK = int(cfg.get("maxtokens", "2200"))
log(f"== AI预生成启动 provider={PROVIDER} 模型链={' -> '.join(CHAIN)} max_tokens={MAXTOK} ==")

units = json.load(open(UNITS, encoding="utf-8"))
ai = {}
if os.path.exists(OUTJS):
    try:
        raw = open(OUTJS, encoding="utf-8").read()
        ai = json.loads(raw[raw.index("window.AI_CONTENT=")+len("window.AI_CONTENT="):].rstrip().rstrip(";"))
        log(f"续传: 已有 {len(ai)} 条")
    except Exception as e:
        log(f"读取已有内容失败: {e}")

REGEN = os.path.join(ROOT, "scripts", "regen_ids.json")
if os.path.exists(REGEN):
    try:
        ids = json.load(open(REGEN, encoding="utf-8"))
        drop = [i for i in ids if i in ai]
        for i in drop: del ai[i]
        log(f"重生成清单: {len(ids)} 条, 已移除旧内容 {len(drop)} 条")
    except Exception as e:
        log(f"读取重生成清单失败: {e}")

SYS = "你是全国软考中级·信息安全工程师的资深辅导讲师，熟悉历年真题与考纲重点。严格只输出JSON，不要输出任何其他文字。"
TPL = """请为下面的教材知识点生成备考复习内容。
【知识点】{no} {title}（教程第{ch}章）
【教材内容】
{content}
输出JSON格式：
{{"explain":"通俗讲解：备考视角讲清这是什么、为什么重要、考试怎么考、易错点在哪，150-250字",
"memo":"记忆提示：口诀/联想/对比，30字内",
"keys":["需能默写的关键术语或短句1","关键2","关键3"]}}"""

def extract_json(txt):
    if not txt: raise ValueError("empty content")
    m = re.search(r'\{[\s\S]*\}', txt)
    if not m: raise ValueError("no json: " + txt[:80])
    return json.loads(m.group(0))

def chat(unit):
    usr = TPL.format(no=unit["no"], title=unit["title"], ch=unit["ch"], content=unit["content"][:1700])
    last_err = None
    for model in CHAIN:
        for attempt in range(2):
            body = {"model": model, "messages": [{"role":"system","content":SYS},{"role":"user","content":usr}],
                    "temperature": 0.4, "max_tokens": MAXTOK, "stream": False}
            try:
                req = urllib.request.Request(URL, data=json.dumps(body).encode("utf-8"),
                    headers={"Content-Type":"application/json","Authorization":"Bearer "+KEY})
                with urllib.request.urlopen(req, timeout=180) as r:
                    j = json.loads(r.read().decode("utf-8"))
                msg = j["choices"][0]["message"]
                txt = msg.get("content") or ""
                d = extract_json(txt)
                return {"explain": str(d.get("explain",""))[:600], "memo": str(d.get("memo",""))[:120],
                        "keys": [str(k)[:60] for k in (d.get("keys") or [])[:4] if str(k).strip()],
                        "model": model}
            except urllib.error.HTTPError as e:
                last_err = f"{model} HTTP{e.code}"
                if e.code == 429:      # 限流: 短暂等待后快速切下一模型
                    time.sleep(1.5); break
                elif e.code in (401, 403):
                    break
                else:
                    time.sleep(2); break
            except Exception as e:
                last_err = f"{model} {str(e)[:80]}"
                time.sleep(3)
    raise RuntimeError("全链失败: " + str(last_err))

import threading
SAVE_LOCK = threading.Lock()
def worker(chunk):
    global fail
    for u in chunk:
        if u["id"] in ai: continue
        try:
            r = chat(u)
            with SAVE_LOCK:
                ai[u["id"]] = r
        except Exception as e:
            with SAVE_LOCK:
                fail += 1
            log(f"[失败] {u['id']} {u['title'][:16]}: {str(e)[:100]}")

def save_all():
    with SAVE_LOCK:
        with open(OUTJS, "w", encoding="utf-8") as f:
            f.write("/*AI预生成 自动生成*/\nwindow.AI_CONTENT=")
            f.write(json.dumps(ai, ensure_ascii=False, separators=(',',':'))); f.write(";\n")

todo = [u for u in units if u["id"] not in ai]
log(f"待生成 {len(todo)} / {len(units)}, 3线程并发")
fail = 0
t0 = time.time()
NW = 3
chunks = [todo[i::NW] for i in range(NW)]
threads = [threading.Thread(target=worker, args=(c,), daemon=True) for c in chunks]
for t in threads: t.start()
done_last = 0
while any(t.is_alive() for t in threads):
    time.sleep(20)
    if len(ai) != done_last:
        done_last = len(ai)
        save_all()
        rate = done_last/max(0.5,(time.time()-t0)/60)
        log(f"[进度] 已存 {len(ai)}/{len(units)} 失败 {fail} 速率 {rate:.1f}题/分")
for t in threads: t.join()
save_all()
log(f"== 完成: 成功 {len(ai)} 失败 {fail} ==")
