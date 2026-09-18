# -*- coding: utf-8 -*-
"""知识点单元质量增强:
1) 薄父单元聚合子单元内容
2) 16个科目二实践单元生成考试导向内容(理论+案例)
3) 专业英语术语表
4) 真题映射增强(qunitX/cunitX) 与考频重算
5) 输出 cards.js(备份) + units_for_llm.json + regen_ids.json
"""
import json, io, os, re, shutil, datetime
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARDS_F = os.path.join(ROOT, "data", "cards.js")
QJS_F = os.path.join(ROOT, "data", "questions.js")
LLM_F = os.path.join(ROOT, "scripts", "units_for_llm.json")
REGEN_F = os.path.join(ROOT, "scripts", "regen_ids.json")


def load_var(path, var):
    raw = io.open(path, encoding="utf-8").read()
    i = raw.index(var + "=")
    j = raw.rindex(";")
    return json.loads(raw[i + len(var) + 1:j])


def dump_var(path, var, obj, header="/*自动生成*/\n"):
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(header + var + "=")
        f.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":")))
        f.write(";\n")


cards = load_var(CARDS_F, "window.CARDS")
db = load_var(QJS_F, "window.DB")
units = cards["units"]
meta = cards["meta"]
by_id = {u["id"]: u for u in units}
changed = set()

# ============ 1) 薄父单元聚合子单元 ============
kids_of = defaultdict(list)
for u in units:
    if not u["id"].startswith("U"):
        continue
    no = u["no"]
    if "." in no:
        kids_of[no.rsplit(".", 1)[0]].append(u)

agg_n = 0
for u in sorted(units, key=lambda x: -x["no"].count(".")):
    if not u["id"].startswith("U"):
        continue
    kids = [k for k in kids_of.get(u["no"], []) if k["no"].count(".") == u["no"].count(".") + 1]
    if not kids:
        continue
    if u.get("points") and len(u.get("content") or "") >= 200:
        continue
    if len(u.get("define") or "") < 60:
        fd = next((k.get("define") for k in kids if k.get("define")), "")
        if fd:
            u["define"] = (u["define"] or "") + ("　" if u.get("define") else "") + fd
            u["define"] = u["define"][:300]
    pts = list(u.get("points") or [])
    have = set(p.get("t") for p in pts)
    for k in kids:
        t = f"{k['no']} {k['title']}"
        if t in have:
            continue
        d = (k.get("define") or k.get("content") or "").strip()
        if d:
            pts.append({"t": t, "d": d[:240]})
    u["points"] = pts
    parts = [(u.get("content") or "").strip()]
    for k in kids:
        c = (k.get("content") or "").strip()
        if c:
            parts.append(f"【{k['no']} {k['title']}】{c[:520]}")
    content = "\n".join(p for p in parts if p)
    u["content"] = content[:2800]
    u["chars"] = len(u["content"])
    changed.add(u["id"])
    agg_n += 1
print("父单元聚合:", agg_n)

# ============ 2) G2 实践单元 ============
def case_summary(cid, maxlen=320):
    c = db["cases"].get(cid)
    if not c:
        return None
    parts = []
    for q in c.get("qs", [])[:3]:
        a = re.sub(r"\s+", " ", q.get("answer") or "").strip()
        if a:
            parts.append(f"问{q['no']}:{a[:110]}")
    d = "；".join(parts)[:maxlen]
    half = "下" if c.get("half") == 2 else "上"
    return f"{c.get('year')}年{half}试题{c.get('cn')}《{c.get('title','')}》：{d}"


def match_prefix(no, p):
    p = p.rstrip(".")
    return no == p or no.startswith(p + ".")


def theory_units(prefixes, limit=5):
    out = []
    for u in units:
        if not u["id"].startswith("U"):
            continue
        if any(match_prefix(u["no"], p) for p in prefixes):
            out.append(u)
    out.sort(key=lambda x: (-(x.get("freq") or 0), x["no"]))
    lv1 = [u for u in out if u["no"].count(".") == 1]
    pick = (lv1 or out)[:limit]
    return pick


G2 = {
    "G2-1.1": dict(goal="掌握网络安全风险评估与等保测评的实践流程",
        tips=["风险评估四要素：资产、威胁、脆弱性、安全措施", "风险值 = 资产价值 × 威胁程度 × 脆弱性严重程度",
              "等保2.0：政府网站不低于二级、每两年测评一次", "测评方式：安全功能检测、安全管理检测、代码安全审查、安全渗透、攻击测试",
              "风险处置：接受、规避、降低、转移"],
        cmds=["netstat 查看端口开放情况", "漏洞扫描：Nmap / Nessus / OpenVAS"],
        theory=["16", "18"], cases=["C-2021-2-1"]),
    "G2-1.2": dict(goal="掌握安全数据收集与分析方法",
        tips=["数据来源：系统日志、网络流量、配置基线、漏洞扫描、威胁情报", "分析方法：关联分析、基线比对、异常检测",
              "日志三要素：时间、来源、事件", "工具：Wireshark 流量分析、IDS 告警、日志审计"],
        cmds=[], theory=["16.2", "16.3", "12"], cases=[]),
    "G2-2.1": dict(goal="掌握操作系统安全方案设计要点",
        tips=["账号口令：/etc/passwd、/etc/shadow，口令哈希加盐存储", "最小权限原则，控制 SUID 程序",
              "补丁与安全基线加固，关闭无用服务与端口", "日志审计：/var/log/auth.log、Windows 事件日志",
              "远程运维使用 SSH 密钥登录，禁用弱口令与 root 直登"],
        cmds=[], theory=["19"], cases=["C-2018-1-3", "C-2020-2-1", "C-2024-2-1", "C-2022-2-2", "C-2021-2-2"]),
    "G2-2.2": dict(goal="掌握网络设备与通信安全方案设计",
        tips=["防火墙：屏蔽子网(DMZ)体系结构，内外包过滤器构成双重屏障", "IDS/IPS：异常+误用检测，部署在 DMZ 交换机镜像口",
              "VPN：IPSec(AH/ESP、传输/隧道模式)与 SSL VPN", "网闸：接近物理隔离的信息摆渡",
              "访问控制策略：最小放行、默认拒绝"],
        cmds=[], theory=["8", "9", "10", "11", "21"], cases=["C-2022-2-1", "C-2017-1-3"]),
    "G2-2.3": dict(goal="掌握计算环境安全方案设计",
        tips=["操作系统加固 + 数据库安全 + 应用安全三层防护", "恶意代码防护：防病毒、白名单、及时打补丁",
              "主机审计与文件完整性校验", "数据备份与恢复演练"],
        cmds=[], theory=["19", "20", "14"], cases=[]),
    "G2-2.4": dict(goal="掌握应用与数据安全方案设计",
        tips=["网站安全：SQL 注入/XSS 防护，预编译参数化查询", "口令哈希加盐存储，防彩虹表撞库",
              "数据分级：一级公开、二级内部、三级秘密、四级机密", "隐私脱敏：抑制、泛化、置换、扰动、裁剪",
              "三大法：网络安全法、数据安全法、个人信息保护法"],
        cmds=[], theory=["22", "26", "15"], cases=["C-2022-2-4"]),
    "G2-2.5": dict(goal="掌握网络安全管理方案设计",
        tips=["P2DR 模型：策略(Policy)、保护(Protection)、检测(Detection)、响应(Response)",
              "管理制度：人员管理、资产管理、运维管理、应急管理", "等保合规：定级、备案、建设整改、测评",
              "安全意识培训与考核"],
        cmds=[], theory=["1.6", "4", "17"], cases=[]),
    "G2-3.1": dict(goal="掌握防火墙部署与规则配置（iptables/规则表）",
        tips=["三种体系结构：双重宿主主机、屏蔽主机、屏蔽子网(DMZ)", "外部包过滤器=第一道屏障，内部=第二道屏障",
              "规则表五列定位法：源地址、目的地址、源端口、目的端口、协议", "动作：Accept/Reject/Drop；默认拒绝(白名单)",
              "必背端口：Web 80/443、DNS 53、SMTP 25、SSH 22、RDP 3389、SMB 445"],
        cmds=["iptables -L 查看规则", "iptables -P INPUT DROP 默认拒绝", "iptables -A INPUT -p tcp --dport 80 -j ACCEPT",
              "iptables -I INPUT -s 192.168.229.1 -j DROP", "Windows：控制面板→系统和安全→Windows Defender 防火墙→高级设置"],
        theory=["8"], cases=["C-2019-1-4", "C-2022-2-1", "C-2020-2-3", "C-2017-1-3", "C-2018-1-1"]),
    "G2-3.2": dict(goal="掌握 IDS/IPS 部署与使用（含 Snort）",
        tips=["IDS 被动防护(监管)，IPS 主动防护(阻断)", "异常检测可查未知但误报高；误用检测基于特征、准确",
              "Snort：基于误用的网络型 IDS，三种模式(嗅探/包记录/NIDS)", "部署位置：DMZ 交换机镜像口",
              "Snort 规则首项动作：alert"],
        cmds=["华为交换机镜像：observe-port 1 interface GE1/0/1；port-mirroring to observe-port 1 inbound/outbound/both"],
        theory=["10"], cases=["C-2018-1-5", "C-2021-2-1"]),
    "G2-3.3": dict(goal="掌握网闸部署与使用",
        tips=["网闸实现接近物理隔离的网间安全隔离与信息交换（信息摆渡）", "适用场景：生产网与办公网/互联网之间",
              "与防火墙区别：隔离强度接近物理隔离"],
        cmds=[], theory=["11"], cases=["C-2022-2-1"]),
    "G2-3.4": dict(goal="掌握 VPN 部署与使用",
        tips=["IPSec：AH 只认证、ESP 加密+认证；传输模式/隧道模式", "IKE 协商安全联盟 SA",
              "SSL VPN 基于 TLS，适合移动办公接入", "远程安全运维通道：VPN 或 SSH"],
        cmds=[], theory=["9"], cases=[]),
    "G2-3.5": dict(goal="掌握漏洞扫描部署与使用",
        tips=["扫描器组成：用户界面、扫描引擎、结果分析、漏洞库", "类型：主机/网络/Web/数据库漏洞扫描",
              "常用工具：Nmap、Nessus、OpenVAS、X-Scan、AppScan、SQLMap", "流程：资产发现→端口扫描→漏洞探测→报告整改",
              "扫描有风险：需授权、限速，避免影响业务"],
        cmds=[], theory=["13", "18.4"], cases=["C-2021-2-1"]),
    "G2-4.1": dict(goal="掌握操作系统安全配置与管理（Linux/Windows）",
        tips=["账号口令：/etc/passwd(744)、/etc/shadow(400/600)", "UID：0=root、1-99系统账号、500+普通；/sbin/nologin 禁止登录",
              "权限换算：r=4/w=2/x=1；SUID=4000；目录 x 权限=能否进入", "SSH 免密：/etc/ssh/sshd_config、authorized_keys 权限 600",
              "清除历史：rm ~/.bash_history；Windows：eventvwr、4624成功/4625失败"],
        cmds=["chmod 700 file；chmod a-x dir", "ln -s 目标 链接名；find /home -xtype l -delete",
              "systemctl restart sshd", "netstat 查看端口"],
        theory=["19"], cases=["C-2018-1-3", "C-2020-2-1", "C-2024-2-1", "C-2022-2-2", "C-2021-2-2"]),
    "G2-4.2": dict(goal="掌握数据库系统安全配置与管理",
        tips=["最小权限：账号按需授权，禁止 root/管理员远程直连", "口令哈希加盐存储，防撞库",
              "SQL 注入防护：预编译/参数化查询、输入校验", "开启审计日志、定期备份与恢复演练"],
        cmds=[], theory=["20"], cases=["C-2021-2-1"]),
    "G2-4.3": dict(goal="掌握网站系统安全配置与管理",
        tips=["等保2.0：政府网站不低于二级、两年一测", "SQL 注入测试语句：1' or 1=1 #",
              "URL 编码解码（%20/%2C 等）", "服务器加固：关闭目录浏览、最小化服务、部署 WAF",
              "口令存储：哈希加盐"],
        cmds=[], theory=["22"], cases=["C-2021-2-1"]),
    "G2-4.4": dict(goal="掌握网络设备安全配置与管理",
        tips=["关闭无用端口与服务，最小化开放", "管理面：SSH 替代 Telnet，ACL 限制管理源",
              "交换机镜像口用于 IDS 流量采集", "配置备份与变更审计"],
        cmds=[], theory=["21"], cases=["C-2022-2-1", "C-2017-1-3"]),
}

g2_n = 0
for u in units:
    gid = u["id"]
    if gid not in G2:
        continue
    cfg = G2[gid]
    old_no = u["no"]
    u["no"] = "科二" + old_no[2:] if old_no.startswith("2.") else old_no
    u["title"] = u["title"]
    pts = []
    cs = [s for s in (case_summary(c) for c in cfg["cases"]) if s]
    if cs:
        pts.append({"t": "考试怎么考（历年案例）", "d": "\n".join(cs)[:1200]})
    if cfg["tips"]:
        pts.append({"t": "核心要点", "d": "\n".join("· " + t for t in cfg["tips"])})
    if cfg["cmds"]:
        pts.append({"t": "常用命令 / 配置", "d": "\n".join("· " + c for c in cfg["cmds"])})
    rel = theory_units(cfg["theory"], 5)
    for t in rel:
        d = (t.get("define") or t.get("content") or "").strip()
        if d:
            pts.append({"t": "相关理论 " + t["no"] + " " + t["title"], "d": d[:240]})
    u["points"] = pts
    u["related"] = [t["id"] for t in rel]
    u["define"] = f"学习目标：{cfg['goal']}。本科目侧重实践应用，重点掌握部署/配置步骤、常考命令与案例答题要点。"
    parts = [f"大纲要求：{u['bullets'][0] if u.get('bullets') else u['title']}", "核心要点："] + ["· " + t for t in cfg["tips"]]
    if cfg["cmds"]:
        parts += ["常用命令/配置："] + ["· " + c for c in cfg["cmds"]]
    if cs:
        parts += ["相关案例："] + cs
    for t in rel:
        d = (t.get("define") or "").strip()
        if d:
            parts.append(f"相关理论 {t['no']} {t['title']}：{d[:200]}")
    u["content"] = "\n".join(parts)[:2800]
    u["chars"] = len(u["content"])
    changed.add(gid)
    g2_n += 1
print("G2实践单元:", g2_n)

# ============ 3) 专业英语 ============
TERMS = [
    ("attack", "攻击"), ("vulnerability", "脆弱性/漏洞"), ("exploit", "漏洞利用"), ("malware", "恶意软件"),
    ("virus", "病毒"), ("worm", "蠕虫"), ("trojan horse", "特洛伊木马"), ("ransomware", "勒索软件"),
    ("phishing", "网络钓鱼"), ("spoofing", "欺骗"), ("sniffing", "嗅探"), ("eavesdropping", "窃听"),
    ("encryption", "加密"), ("decryption", "解密"), ("cipher", "密码/密文"), ("plaintext", "明文"),
    ("ciphertext", "密文"), ("symmetric", "对称的"), ("asymmetric", "非对称的"), ("public key", "公钥"),
    ("private key", "私钥"), ("digital signature", "数字签名"), ("hash", "哈希/散列"), ("certificate", "证书"),
    ("authentication", "认证"), ("authorization", "授权"), ("access control", "访问控制"), ("firewall", "防火墙"),
    ("intrusion detection", "入侵检测"), ("intrusion prevention", "入侵防御"), ("packet filtering", "包过滤"),
    ("proxy", "代理"), ("gateway", "网关"), ("isolation", "隔离"), ("backup", "备份"), ("recovery", "恢复"),
    ("availability", "可用性"), ("confidentiality", "保密性"), ("integrity", "完整性"), ("non-repudiation", "不可否认性"),
    ("audit", "审计"), ("risk assessment", "风险评估"), ("penetration testing", "渗透测试"), ("patch", "补丁"),
]
eng = by_id.get("G1-22")
if eng:
    pts = list(eng.get("points") or [])
    pts.append({"t": "高频安全术语表（中英对照）", "d": "；".join(f"{en} {cn}" for en, cn in TERMS)})
    eng["points"] = pts
    eng["content"] = ("上午卷第71-75题为英语阅读，考查安全领域英文术语与短文理解。\n"
                      "应试策略：先读题干空格前后句，再回原文定位；积累下列高频术语。\n"
                      + "；".join(f"{en} {cn}" for en, cn in TERMS))[:2800]
    eng["chars"] = len(eng["content"])
    eng["define"] = "考查安全领域英文术语与短文理解；掌握下列高频术语即可覆盖大部分阅读障碍。"
    changed.add("G1-22")
    print("专业英语: ok")

# ============ 4) 真题映射增强 ============
CASE_RULES = [
    (r"防火墙|iptables|规则表|包过滤|ACL", ["G2-3.1"]),
    (r"Snort|IDS|IPS|入侵检测|镜像|observe-port", ["G2-3.2"]),
    (r"网闸|隔离装置|物理隔离", ["G2-3.3"]),
    (r"VPN|IPSec|隧道|SSL VPN", ["G2-3.4"]),
    (r"SSH|免密|sshd|authorized_keys|bash_history", ["G2-4.1"]),
    (r"漏洞扫描|漏扫|扫描器|Nmap|Nessus|OpenVAS", ["G2-3.5"]),
    (r"passwd|shadow|chmod|SUID|符号链接|用户账号|口令文件|Linux权限|ls -l", ["G2-4.1"]),
    (r"数据库|MySQL|SQL", ["G2-4.2"]),
    (r"等保|测评|网站|Apache|SQL注入|URL编码", ["G2-4.3", "G2-1.1"]),
    (r"交换机|路由器|网络设备", ["G2-4.4"]),
    (r"风险评估|风险分析", ["G2-1.1"]),
    (r"数据安全|隐私|脱敏|数据分级", ["G2-2.4"]),
    (r"操作系统|Windows|Linux", ["G2-2.1", "G2-4.1"]),
    (r"认证|口令|身份", ["G2-2.1"]),
]
cunitX = defaultdict(list)
for cid, c in db["cases"].items():
    for q in c.get("qs", []):
        key = f"{cid}#{q['no']}"
        blob = " ".join([c.get("title") or "", c.get("scenario") or "", q.get("text") or "",
                         q.get("answer") or "", q.get("analysis") or ""])
        for pat, targets in CASE_RULES:
            if re.search(pat, blob):
                for t in targets:
                    if t not in cunitX[key]:
                        cunitX[key].append(t)

Q_RULES = [
    (r"防火墙|包过滤|规则表|DMZ|屏蔽子网", "8"),
    (r"入侵检测|Snort|IDS|IPS", "10"),
    (r"网闸|物理隔离", "11"),
    (r"VPN|IPSec|隧道", "9"),
    (r"访问控制|BLP|BiBa|ACL|能力表", "7"),
    (r"RSA|公钥|非对称", "3.3"),
    (r"DES|分组密码|S盒", "3.3"),
    (r"Hash|摘要|碰撞", "3.4"),
    (r"数字签名|数字证书|PKI|CA", "6.3"),
    (r"身份认证|Kerberos|口令", "6"),
    (r"漏洞|扫描|Nmap|Nessus", "13"),
    (r"恶意代码|病毒|蠕虫|木马", "14"),
    (r"应急响应", "17"),
    (r"风险评估|风险", "16"),
    (r"等保|测评", "18"),
    (r"网络安全法|数据安全法|个人信息保护法|法律|法规", "1.7"),
    (r"云计算|云安全", "23"),
    (r"工控|工业控制", "24"),
    (r"大数据|数据安全", "26"),
    (r"移动|Android|iOS", "25"),
    (r"网站|Web|SQL注入|XSS", "22"),
    (r"数据库|SQL|Oracle|MySQL", "20"),
    (r"操作系统|Linux|Windows", "19"),
    (r"审计", "12"),
    (r"物理|环境安全", "5"),
    (r"DDoS|拒绝服务|攻击", "2"),
    (r"密码学|加密|保密", "3"),
]
unit_by_prefix = {}
for u in units:
    if not u["id"].startswith("U"):
        continue
    top = u["no"].split(".")[0]
    unit_by_prefix.setdefault(top, []).append(u)
for k in unit_by_prefix:
    unit_by_prefix[k].sort(key=lambda x: (x["no"].count("."), x["no"]))


def resolve_unit(prefix):
    top = prefix.split(".")[0]
    cands = unit_by_prefix.get(top, [])
    exact = [u for u in cands if u["no"] == prefix or u["no"].startswith(prefix + ".")]
    pick = exact[0] if exact else (cands[0] if cands else None)
    return pick["id"] if pick else None


qunitX = defaultdict(list)
for qid, q in db["questions"].items():
    blob = " ".join([q.get("stem") or "", q.get("analysis") or "", meta.get("qpoint", {}).get(qid, "")])
    for pat, prefix in Q_RULES:
        if re.search(pat, blob):
            uid = resolve_unit(prefix)
            if uid and uid not in qunitX[qid]:
                qunitX[qid].append(uid)

meta["qunitX"] = {k: v for k, v in qunitX.items()}
meta["cunitX"] = {k: v for k, v in cunitX.items()}
print("qunitX:", len(qunitX), "| cunitX:", len(cunitX))

# 重算考频
freq = defaultdict(int)
for qid, uid in meta.get("qunit", {}).items():
    freq[uid] += 1
for qid, uids in meta["qunitX"].items():
    for uid in uids:
        freq[uid] += 1
for key, uid in meta.get("cunit", {}).items():
    freq[uid] += 1
for key, uids in meta["cunitX"].items():
    for uid in uids:
        freq[uid] += 1
for u in units:
    u["freq"] = freq.get(u["id"], 0)
meta["generated"] = datetime.date.today().isoformat()

# ============ 5) 写出 ============
if not os.path.exists(CARDS_F + ".bak"):
    shutil.copy2(CARDS_F, CARDS_F + ".bak")
    print("备份:", CARDS_F + ".bak")
dump_var(CARDS_F, "window.CARDS", cards)

slim = [{"id": u["id"], "no": u["no"], "title": u["title"], "ch": u.get("ch"), "content": u["content"][:1800]}
        for u in units if len(u.get("content") or "") >= 30]
with io.open(LLM_F, "w", encoding="utf-8") as f:
    json.dump(slim, f, ensure_ascii=False, indent=1)
print("LLM清单:", len(slim))

regen = sorted(changed)
with io.open(REGEN_F, "w", encoding="utf-8") as f:
    json.dump(regen, f, ensure_ascii=False)
print("需重生成:", len(regen))

# 统计
bad = [u for u in units if not u.get("points") and len(u.get("content") or "") < 80]
print("增强后 无要点且<80字:", len(bad))
print("完成")
