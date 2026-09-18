# -*- coding: utf-8 -*-
"""重生成 handbook.js 中生成异常(占位符/空)的条目"""
import json, io, os, re, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYF = os.path.join(ROOT, "scripts", ".llmkey")
HB_F = os.path.join(ROOT, "data", "handbook.js")

cfg = {}
for ln in open(KEYF, encoding="utf-8-sig"):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1); cfg[k.strip()] = v.strip()
PROVIDER, KEY = cfg.get("provider", "deepseek"), cfg.get("key", "")
PRIMARY = cfg.get("model", "deepseek-flash")
URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions" if PROVIDER == "glm" else "https://api.deepseek.com/chat/completions"
CHAIN = [PRIMARY, "deepseek-v4-pro"]
SYS = "你是全国软考中级·信息安全工程师的资深辅导讲师。严格只输出JSON，不要输出任何其他文字。"


def chat(usr, maxtok=2500):
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
                    raise ValueError("no json")
                return json.loads(m.group(0))
            except urllib.error.HTTPError as e:
                last = f"{model} HTTP{e.code}"; time.sleep(2); break
            except Exception as e:
                last = f"{model} {str(e)[:60]}"; time.sleep(2)
    raise RuntimeError(last)


hb = json.loads(io.open(HB_F, encoding="utf-8").read().split("=", 1)[1].rstrip().rstrip(";"))

CHEATS = {
    "HT-9": ("编码速查（ASCII/Hex/Base64/URL）",
        "必须包含这些事实：ASCII：65='A'、97='a'、48='0'、32=空格；Hex：0x41='A'、0x61646d696e='admin'；Base64：3字节→4字符，'A'→'QQ=='，不足补=；URL：空格=%20、逗号=%2C、#=%23、'=' 保留、中文UTF-8占3字节。"),
    "HT-18": ("风险评估与管理模型速查",
        "必须包含：风险评估四要素(资产/威胁/脆弱性/安全措施)、风险值=资产价值×威胁程度×脆弱性严重程度、风险处置(接受/规避/降低/转移)、P2DR(策略/保护/检测/响应)、PDCA(计划/执行/检查/改进)、SDLC阶段、等保流程(定级/备案/建设整改/测评/监督检查)。"),
    "HT-22": ("Android 安全速查",
        "必须包含：四层安全措施(应用层权限声明/框架层签名机制/运行层安全沙箱/内核层ASLR)、权限声明文件AndroidManifest.xml、uses-permission、四大组件攻击(目录遍历-Content Providers、界面劫持-Activities、短信拦截-Broadcast Receiver)、5种数据存储(SharedPreferences/文件/SQLite/ContentProvider/网络)。"),
    "HT-24": ("物理与环境安全速查",
        "必须包含：门禁与区域划分、防火防水防雷、电磁屏蔽与干扰、温湿度控制、UPS与冗余供电、存储介质销毁(消磁/物理粉碎)、设备防拆与视频监控、机房选址与环境要求。"),
}
SCRIPTS = {
    "HS-27": ("技术域", "Linux 系统",
        "必须包含：账号文件/etc/passwd(744)与/etc/shadow(400/600)、UID分段(0/1-99/500+)、权限数字(r=4/w=2/x=1，SUID=4000)、命令(chmod/ln -s/find -xtype l/systemctl restart sshd/netstat/rm ~/.bash_history)、日志(/var/log/auth.log)、符号链接与失效链接。"),
}
CALCS = {
    "HC-6": ("DES 初始置换 IP",
        "步骤：DES初始置换按IP表把输入第58位放输出第1位、第50位放第2位……共64位逐一搬运。例题必须完整演算：明文M=0123456789ABCDEF，二进制=0000 0001 0010 0011 0100 0101 0110 0111 1000 1001 1010 1011 1100 1101 1110 1111，按IP置换后=1100 1100 0000 0000 1100 1100 1111 1111 1111 0000 1010 1010 1111 0000 1010 1010=CC00CCFF F0AAF0AA。"),
    "HC-11": ("心跳包与长度字段",
        "步骤：长度字段2字节→16位→最大2^16-1=65535；接收端若按长度字段分配缓冲并拷贝，实际数据不足时越界读取内存(类似Heartbleed)。例题：payload字段写0xFFFF但实际只发1字节数据，接收端malloc(1+2+65535)并memcpy 65535字节→泄露约64KB内存。防护：校验实际长度与声明长度一致、限定上限、使用安全拷贝。"),
}

for cid, (title, must) in CHEATS.items():
    usr = f"""请生成"【{title}】"速查表（软考信息安全工程师下午案例用）。{must}
输出JSON：{{"html":"<table><tr><th>...</th></tr><tr><td>...</td></tr>...</table>","note":"40字内"}}
要求：至少6行；不得出现省略号"..."；只允许 <table><tr><th><td> 标签。"""
    d = chat(usr)
    html = str(d.get("html", ""))
    assert "<tr" in html and "..." not in html, cid
    for c in hb["cheats"]:
        if c["id"] == cid:
            c["title"] = title; c["html"] = html
    print("修复", cid, title, len(html))

for sid, (cat, title, must) in SCRIPTS.items():
    usr = f"""请为软考"下午案例题"写答题模板：分类【{cat}】场景【{title}】。{must}
输出JSON：{{"signal":"看到什么信号(60字内)","write":"写什么关键词(200字内)","example":"满分示例(200字内)","memo":"口诀(30字内)"}}
禁止输出占位符或省略号。"""
    d = chat(usr)
    html = "<p><b>信号：</b>%s</p><p><b>写：</b>%s</p><p><b>示例：</b>%s</p><p class=\"muted\">口诀：%s</p>" % (
        str(d.get("signal", ""))[:200], str(d.get("write", ""))[:400], str(d.get("example", ""))[:400], str(d.get("memo", ""))[:80])
    for s in hb["scripts"]:
        if s["id"] == sid:
            s["title"] = title; s["cat"] = cat; s["html"] = html
    print("修复", sid, title, len(html))

for cid, (title, must) in CALCS.items():
    usr = f"""请写"【{title}】"计算步骤卡（软考信息安全工程师）。{must}
输出JSON：{{"steps":"步骤(300字内)","example":"例题(300字内)","pitfalls":"易错点(120字内)"}}
禁止输出占位符或省略号。"""
    d = chat(usr)
    html = "<pre>%s</pre><p><b>例题：</b>%s</p><p class=\"muted\">易错点：%s</p>" % (
        str(d.get("steps", ""))[:700], str(d.get("example", ""))[:700], str(d.get("pitfalls", ""))[:300])
    for c in hb["calcs"]:
        if c["id"] == cid:
            c["title"] = title; c["html"] = html
    print("修复", cid, title, len(html))

io.open(HB_F, "w", encoding="utf-8").write("/*自动生成 请勿手改*/\nwindow.HANDBOOK=" +
    json.dumps(hb, ensure_ascii=False, separators=(",", ":")) + ";\n")
print("handbook.js 已更新")
