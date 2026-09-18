# -*- coding: utf-8 -*-
"""冲刺手册全面扩充内容生成 (断点续传)
产出 staging: scripts/handbook_gen.json
  scripts_gen: 新增话术 (补齐到45条, 保留原HS-1..6)
  cheats_gen:  新增速查表 (补齐到24张, 保留原HT-1..5)
  calcs_gen:   新增计算卡 (补齐到16张, 保留原HC-1..5)
  checklist_gen: 按考频>0单元生成的问答条目
"""
import json, re, os, time, io, urllib.request, urllib.error, threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYF = os.path.join(ROOT, "scripts", ".llmkey")
QJS = os.path.join(ROOT, "data", "questions.js")
CARDS_F = os.path.join(ROOT, "data", "cards.js")
AI_F = os.path.join(ROOT, "data", "ai_content.js")
STATE = os.path.join(ROOT, "scripts", "handbook_gen.json")
LOG = os.path.join(ROOT, "scripts", "handbook_gen.log")


def log(m):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(m + "\n")
    print(m, flush=True)


def load_var(path, var):
    raw = io.open(path, encoding="utf-8").read()
    return json.loads(raw[raw.index(var + "=") + len(var) + 1: raw.rindex(";")])


cfg = {}
for ln in open(KEYF, encoding="utf-8-sig"):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1); cfg[k.strip()] = v.strip()
PROVIDER, KEY = cfg.get("provider", "deepseek"), cfg.get("key", "")
PRIMARY = cfg.get("model", "deepseek-flash")
URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions" if PROVIDER == "glm" else "https://api.deepseek.com/chat/completions"
CHAIN = [PRIMARY, "deepseek-v4-pro"] if PROVIDER != "glm" else [PRIMARY, "glm-4.7-flash"]
CHAIN = list(dict.fromkeys(m for m in CHAIN if m))

cards = load_var(CARDS_F, "window.CARDS")
ai = load_var(AI_F, "window.AI_CONTENT")
state = {"scripts_gen": {}, "cheats_gen": {}, "calcs_gen": {}, "checklist_gen": {}}
if os.path.exists(STATE):
    try:
        state = json.load(open(STATE, encoding="utf-8"))
        log(f"续传: scripts={len(state.get('scripts_gen',{}))} cheats={len(state.get('cheats_gen',{}))} calcs={len(state.get('calcs_gen',{}))} checklist={len(state.get('checklist_gen',{}))}")
    except Exception as e:
        log(f"读取staging失败: {e}")

# ---------------- 任务清单 ----------------
# 新增话术 39 条 (原 HS-1..6 保留: 安全目标判定/协议缺陷/代码漏洞/防火墙/计算步骤分/陌生题兜底)
SCRIPT_TOPICS = [
    ("通用", "安全事件类型判定"), ("通用", "不会写时的保底话术"), ("通用", "踩分点与时间分配"), ("通用", "交卷前检查清单"),
    ("题型", "概念解释题"), ("题型", "列举题"), ("题型", "对比题"), ("题型", "流程/步骤题"),
    ("题型", "原因分析题"), ("题型", "改进/加固措施题"), ("题型", "方案设计题"), ("题型", "配置命令题"),
    ("题型", "日志分析题"), ("题型", "流量分析题"), ("题型", "代码审计题"), ("题型", "协议安全性分析题"),
    ("技术域", "密码学概念"), ("技术域", "密码学计算"), ("技术域", "认证协议"), ("技术域", "访问控制/BLP"),
    ("技术域", "Linux 系统"), ("技术域", "Windows 系统"), ("技术域", "防火墙/iptables"), ("技术域", "IDS/IPS/Snort"),
    ("技术域", "VPN/IPSec"), ("技术域", "漏洞扫描"), ("技术域", "恶意代码"), ("技术域", "应急响应"),
    ("技术域", "安全审计"), ("技术域", "风险评估"), ("技术域", "等级保护"), ("技术域", "网站安全/SQL注入"),
    ("技术域", "数据库安全"), ("技术域", "网络设备安全"), ("技术域", "物理与环境安全"), ("技术域", "数据安全"),
    ("技术域", "隐私保护"), ("技术域", "法律法规"), ("技术域", "Android/移动应用"), ("技术域", "云计算安全"),
    ("技术域", "工控安全"), ("技术域", "大数据安全"), ("技术域", "AI 安全"),
]
# 新增速查 19 张 (原 HT-1..5: 端口/事件ID/命令/模型服务/真题复刻)
CHEAT_TOPICS = [
    "密码学公式速查", "密钥与算法参数速查", "Linux 权限与文件速查", "编码速查（ASCII/Hex/Base64/URL）",
    "攻击特征速查", "Wireshark 过滤与 TLS 速查", "防火墙与 iptables 速查", "IDS/Snort 速查",
    "等保 2.0 速查", "法律法规速查", "数据分级与脱敏速查", "恶意代码与应急速查",
    "风险评估与管理模型速查", "网站安全速查", "数据库安全速查", "网络设备安全速查",
    "Android 安全速查", "云计算/工控/大数据安全速查", "物理与环境安全速查",
]
# 新增计算卡 11 张 (原 HC-1..5: RSA/仿射/DES/权限/子网)
CALC_TOPICS = [
    "DES 初始置换 IP", "十六进制与 ASCII 转换", "URL 编码", "Base64 编码", "分组密码工作模式",
    "心跳包与长度字段", "哈希长度与性质", "密钥长度对比", "模运算与逆运算", "时间线/日志时间计算", "CRC 与校验和",
]

SYS = "你是全国软考中级·信息安全工程师的资深辅导讲师，熟悉历年真题与考纲重点。严格只输出JSON，不要输出任何其他文字。"


def chat(usr, maxtok=2000):
    last = None
    for model in CHAIN:
        for attempt in range(2):
            body = {"model": model, "messages": [{"role": "system", "content": SYS}, {"role": "user", "content": usr}],
                    "temperature": 0.3, "max_tokens": maxtok, "stream": False}
            if PROVIDER == "deepseek":
                body["response_format"] = {"type": "json_object"}
            try:
                req = urllib.request.Request(URL, data=json.dumps(body).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": "Bearer " + KEY})
                with urllib.request.urlopen(req, timeout=120) as r:
                    j = json.loads(r.read().decode("utf-8"))
                msg = j["choices"][0]["message"]
                txt = msg.get("content") or msg.get("reasoning_content") or ""
                m = re.search(r'\{[\s\S]*\}', txt)
                if not m:
                    raise ValueError("no json: " + txt[:60])
                return json.loads(m.group(0))
            except urllib.error.HTTPError as e:
                last = f"{model} HTTP{e.code}"; time.sleep(2); break
            except Exception as e:
                last = f"{model} {str(e)[:70]}"; time.sleep(2)
    raise RuntimeError(last or "fail")


# ---------------- 单元清单(考频优先) ----------------
units = [u for u in cards["units"] if (u.get("freq") or 0) > 0]
units.sort(key=lambda u: -(u.get("freq") or 0))
log(f"考频>0单元: {len(units)}")

# ---------------- 生成任务 ----------------
lock = threading.Lock()
fail = 0


def save_state():
    with lock:
        with io.open(STATE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False)


def task_scripts():
    global fail
    for i, (cat, title) in enumerate(SCRIPT_TOPICS):
        sid = "HS-%d" % (7 + i)
        if sid in state["scripts_gen"]:
            continue
        usr = f"""请为软考中级信息安全工程师"下午案例题"写一条考场答题模板。
【分类】{cat}｜【场景】{title}
输出JSON格式：
{{"signal":"看到什么题干信号就用它（50字内）",
"write":"直接写什么关键词/句子，分号分隔（150字内）",
"example":"一个满分示例（180字内）",
"memo":"记忆口诀（30字内）"}}"""
        try:
            d = chat(usr)
            with lock:
                state["scripts_gen"][sid] = {"id": sid, "cat": cat, "title": title,
                    "signal": str(d.get("signal", ""))[:200], "write": str(d.get("write", ""))[:400],
                    "example": str(d.get("example", ""))[:400], "memo": str(d.get("memo", ""))[:80]}
        except Exception as e:
            with lock:
                fail += 1
            log(f"[失败] 话术 {title}: {str(e)[:80]}")


def task_cheats():
    global fail
    for i, title in enumerate(CHEAT_TOPICS):
        hid = "HT-%d" % (6 + i)
        if hid in state["cheats_gen"]:
            continue
        usr = f"""请生成一张"【{title}】"速查表，用于软考信息安全工程师下午案例考试。
输出JSON格式：{{"html":"<table>...</table>","note":"一句话说明(40字内)"}}
要求：3-12行；2-3列；内容必须准确（端口、命令、公式、日期不得编造）；HTML 只用 <table><tr><th><td>，th 用于表头。"""
        try:
            d = chat(usr, 2200)
            html = str(d.get("html", ""))
            if "<table" not in html:
                raise ValueError("no table")
            with lock:
                state["cheats_gen"][hid] = {"id": hid, "title": title, "html": html[:6000],
                                            "note": str(d.get("note", ""))[:80]}
        except Exception as e:
            with lock:
                fail += 1
            log(f"[失败] 速查 {title}: {str(e)[:80]}")


def task_calcs():
    global fail
    for i, title in enumerate(CALC_TOPICS):
        cid = "HC-%d" % (6 + i)
        if cid in state["calcs_gen"]:
            continue
        usr = f"""请写一张"【{title}】"计算步骤卡，用于软考信息安全工程师下午案例考试。
输出JSON格式：
{{"steps":"步骤说明：公式与操作要点，可分步换行（250字内）",
"example":"真题级例题：必须包含完整演算过程与结果（300字内）",
"pitfalls":"易错点（100字内）"}}
计算与公式必须准确，不确定的宁可少写。"""
        try:
            d = chat(usr, 2200)
            with lock:
                state["calcs_gen"][cid] = {"id": cid, "title": title,
                    "steps": str(d.get("steps", ""))[:700], "example": str(d.get("example", ""))[:700],
                    "pitfalls": str(d.get("pitfalls", ""))[:300]}
        except Exception as e:
            with lock:
                fail += 1
            log(f"[失败] 计算卡 {title}: {str(e)[:80]}")


def task_checklist():
    global fail
    for u in units:
        uid = u["id"]
        if uid in state["checklist_gen"]:
            continue
        keys = [k for k in (ai.get(uid, {}).get("keys") or []) if len(k) <= 18]
        if not keys:
            keys = [k for k in (ai.get(uid, {}).get("keys") or []) if len(k) <= 30]
        pts = [p.get("t", "") for p in (u.get("points") or [])][:6]
        if not keys and not pts:
            continue
        usr = f"""把下面知识点整理成"问答式默写条目"，用于软考信息安全工程师备考默写。
【知识点】{u.get('no','')} {u.get('title','')}
【要点】{'；'.join(keys[:8])}
【相关小标题】{'；'.join(pts)}
输出JSON格式：{{"items":[{{"q":"问题(≤15字)","a":"答案(≤60字)"}}, ...]}}
要求：2-3条；答案准确、可直接背诵；不要包含"如图"等指代。"""
        try:
            d = chat(usr, 1500)
            items = d.get("items") or d.get("list") or (d if isinstance(d, list) else [])
            clean = []
            for it in items[:3]:
                q = str(it.get("q", "")).strip()[:40]
                a = str(it.get("a", "")).strip()[:120]
                if q and a:
                    clean.append({"q": q, "a": a})
            if clean:
                with lock:
                    state["checklist_gen"][uid] = {"ch": u.get("ch"), "s2ch": u.get("s2ch"),
                                                   "no": u.get("no"), "title": u.get("title"), "items": clean}
        except Exception as e:
            with lock:
                fail += 1
            log(f"[失败] 清单 {uid}: {str(e)[:80]}")


log("== 冲刺手册内容生成启动 ==")
todo_n = len(SCRIPT_TOPICS) + len(CHEAT_TOPICS) + len(CALC_TOPICS) + len(units)
log(f"任务: 话术{len(SCRIPT_TOPICS)} + 速查{len(CHEAT_TOPICS)} + 计算卡{len(CALC_TOPICS)} + 清单{len(units)}单元")

threads = [threading.Thread(target=f, daemon=True) for f in (task_scripts, task_cheats, task_calcs, task_checklist)]
for t in threads:
    t.start()
last_n = -1
while any(t.is_alive() for t in threads):
    time.sleep(15)
    n = len(state["scripts_gen"]) + len(state["cheats_gen"]) + len(state["calcs_gen"]) + len(state["checklist_gen"])
    if n != last_n:
        last_n = n
        save_state()
        log(f"[进度] 话术{len(state['scripts_gen'])}/{len(SCRIPT_TOPICS)} 速查{len(state['cheats_gen'])}/{len(CHEAT_TOPICS)} 计算{len(state['calcs_gen'])}/{len(CALC_TOPICS)} 清单{len(state['checklist_gen'])}/{len(units)} 失败{fail}")
for t in threads:
    t.join()
save_state()
log(f"== 完成: 失败 {fail} ==")
