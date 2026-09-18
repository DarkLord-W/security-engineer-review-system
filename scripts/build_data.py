# -*- coding: utf-8 -*-
"""
软考信息安全工程师复习系统 - 数据构建管线 v2
源: 大纲MD / 试题分析MD(2018-2022) / 案例HTML(2016-2025) / 教程MD×3 / 教程HTML×3
出: data/questions.js / data/syllabus.js / data/textbook/*.js / assets/ / report_build.md
"""
import json, re, os, base64, hashlib, urllib.request, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data")
TB_OUT = os.path.join(OUT, "textbook")
IMG_OUT = os.path.join(ROOT, "assets", "img")
TBIMG_OUT = os.path.join(ROOT, "assets", "textbook")
REPORT = []

def log(msg):
    print(msg, flush=True)
    REPORT.append(str(msg))

CN_NUM = {"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8}
PAREN = '[（(]'; CPAREN = '[）)]'

def strip_ocr_noise(text):
    n = len(re.findall(r'The Ground Truth', text))
    text = re.sub(r'The Ground Truth[^\n]*(?:\n(?!\n)[^\n]*)*', '', text)
    if n: log(f"  [清理] Ground Truth 噪声段落 x{n}")
    return text

def preprocess(text):
    """黏连文本规范化: 参考答案/试题/【问题 标记换行"""
    text = re.sub(r'参考答案\s*[（(](\d+)[）)]\s*([A-D]{1,4})\s*(?=试题\s*[（(])', r'参考答案\n(\1) \2\n\n', text)
    text = re.sub(r'参考答案\s*[（(](\d+)[）)]\s*([A-D]{1,4})', r'参考答案\n(\1) \2', text)
    # "参考答案 (56) D" 同行答案 → 拆两行
    text = re.sub(r'(?m)^([ \t]*#{0,2}[ \t]*参考答案)[ \t]*[：:]?[ \t]+([（(]\d+[）)][ \t]*[A-D]{1,4}.*)$', r'\1\n\2', text)
    text = re.sub(r'(?<!\n)[ \t]*(试题\s*[（(]\d+[）)](?:\s*～\s*[（(]\d+[）)])?)(?=\s*$)', r'\n\1', text, flags=re.M)
    text = re.sub(r'(?<!\n)[ \t]*(试题\s*[（(]\d+[）)]分析)', r'\n\1', text)
    text = re.sub(r'(?<!\n)[ \t]*(试题[一二三四五六七八]\s*分析)', r'\n\1', text)
    text = re.sub(r'(?<!\n)[ \t]*(参考答案)(?![（(\d])', r'\n\1', text)
    text = re.sub(r'(?<!\n)[ \t]*(【问题\s*\d+】)', r'\n\1', text)
    return text

# OCR 吞掉 marker 的题: 在题干锚点前人工补 marker  (key: (year, half, subject))
MARKER_PATCHES = {
    (2018,1,1): [(7,  "S/Key 口令是一种一次性口令生成方案"),
               (14, "如果未经授权的实体得到了数据的访问权"),
               (42, "IP 地址分为全球地址和专用地址"),
               (67, "SM3 密码杂凑算法的消息分组长度")],
    (2022,2,1): [(52, "以下网络安全漏洞发现工具中"),
               (54, "文件型病毒不能感染的文件类型是")],
}
def apply_marker_patches(ptext, year, half, subject):
    for num, anchor in MARKER_PATCHES.get((year, half, subject), []):
        if f'试题（{num}）' in ptext and re.search(rf'^#{{0,2}}\s*试题\s*[（(]{num}[）)]\s*$', ptext, re.M):
            continue
        if anchor in ptext:
            ptext = ptext.replace(anchor, f'试题（{num}）\n{anchor}', 1)
            log(f"  [补丁] {year}-{half} 试题({num}) marker 已按锚点补插")
        else:
            log(f"  [补丁] {year}-{half} 试题({num}) 锚点未命中: {anchor[:20]}")
    return ptext

def clean_latex(s):
    if not s: return s
    s = re.sub(r'\\(?:mathrm|text|mathbb|mathbf|mathit)\{([^}]*)\}', r'\1', s)
    repl = {'\\|':'||','\\rightarrow':'→','\\leftarrow':'←','\\times':'×','\\div':'÷',
            '\\leq':'≤','\\geq':'≥','\\approx':'≈','\\neq':'≠','\\infty':'∞','\\sqrt':'√',
            '\\cup':'∪','\\cap':'∩','\\oplus':'⊕','\\leftrightarrow':'↔','\\Rightarrow':'⇒',
            "\\prime":"′",'\\ldots':'…','\\cdots':'…','\\circ':'°'}
    for k,v in repl.items(): s = s.replace(k, v)
    s = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    s = s.replace('$','').replace('\\\\',' ')
    s = re.sub(r'_\{([^}]*)\}', r'_\1', s)
    s = s.replace('{','').replace('}','')
    return s

def clean_text(s):
    if not s: return ""
    s = clean_latex(s)
    s = re.sub(r'[ \t]+\n', '\n', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()

def html_to_text(s):
    """HTML→统一文本(保留 <table>/<img>, br/p 转换行)"""
    if not s: return ""
    s = re.sub(r'<span class="tag[^"]*"[^>]*>.*?</span>', '', s, flags=re.S)
    keep = []
    def _kp(m):
        keep.append(m.group(0)); return f'\x00KP{len(keep)-1}\x00'
    s = re.sub(r'<table.*?</table>', _kp, s, flags=re.S | re.I)
    def _kp_img(m):
        keep.append(f'<img src="{m.group(1)}" style="max-width:100%">')
        return f'\x00KP{len(keep)-1}\x00'
    s = re.sub(r'<img[^>]+src="([^"]+)"[^>]*>', _kp_img, s, flags=re.I)
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.I)
    s = re.sub(r'</p>\s*<p[^>]*>', '\n', s, flags=re.I)
    s = re.sub(r'</div>\s*<div[^>]*>', '\n', s, flags=re.I)
    s = re.sub(r'<div class="figure-title"[^>]*>(.*?)</div>', r'\n[图] \1\n', s, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    for k,v in {'&nbsp;':' ','&amp;':'&','&lt;':'<','&gt;':'>','&quot;':'"','&#39;':"'"}.items():
        s = s.replace(k,v)
    s = re.sub(r'\n{3,}', '\n\n', s)
    s = re.sub(r'[ \t]+\n', '\n', s)
    for i,t in enumerate(keep): s = s.replace(f'\x00KP{i}\x00', '\n'+t+'\n')
    return s.strip()

def dl(url, path):
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=25) as r, open(path,"wb") as f:
            f.write(r.read())
        return True
    except Exception as e:
        log(f"    [下载失败] {url[:70]} -> {e}")
        return False

# ================================================================ A. 试题分析MD
def parse_analysis_md(path):
    raw = open(path, encoding="utf-8").read()
    raw = strip_ocr_noise(raw)
    cdn = sorted(set(re.findall(r'!\[[^\]]*\]\((https://cdn-mineru[^)]+)\)', raw)))
    log(f"  [图片] 真题MD外链 {len(cdn)} 张")
    os.makedirs(IMG_OUT, exist_ok=True)
    for url in cdn:
        h = hashlib.md5(url.encode()).hexdigest()[:16]
        fname = f"q_{h}.jpg"; path_ = os.path.join(IMG_OUT, fname)
        if not os.path.exists(path_): dl(url, path_)
        raw = raw.replace(f"]({url})", f"](assets/img/{fname})")
    raw = re.sub(r'!\[[^\]]*\]\(([^)]+)\)', r'<img src="\1" style="max-width:100%">', raw)
    chs = [(m.start(), int(m.group(1))) for m in re.finditer(r'^#{1,2}\s*第\s*(\d+)\s*章', raw, re.M)]
    out = []
    for i,(pos,num) in enumerate(chs):
        block = raw[pos: chs[i+1][0] if i+1 < len(chs) else len(raw)]
        head = re.sub(r'\s','', block[:400])
        ym = re.search(r'(\d{4})(上|下)半年', head) or re.search(r'(\d{4})(上|下)半年', re.sub(r'\s','',block[:3000]))
        year, half = int(ym.group(1)), (1 if ym.group(2)=="上" else 2)
        is_morning = ('上午' in head[:60]) or ('上午试题分析与解答' in re.sub(r'\s','',block[:2000]))
        out.append((num, year, half, 1 if is_morning else 2, block))
        log(f"  [章] 第{num}章 → {year}{'上下'[half-1]}半年 科目{1 if is_morning else 2} ({len(block)//1000}KB)")
    return out

def parse_group_questions(text, year, half):
    qs, groups = [], {}
    for m in re.finditer(r'^#{0,2}\s*试题\s*[（(](\d+)[）)]～\s*[（(](\d+)[）)]\s*$', text, re.M):
        n1, n2 = int(m.group(1)), int(m.group(2))
        nm = re.search(r'^#{0,2}\s*试题[一二三四五六七八]', text[m.end():], re.M)
        seg = text[m.end(): m.end()+nm.start()] if nm else text[m.end():]
        a_m = re.search(r'^#{0,2}\s*参考译文\s*$', seg, re.M)
        ans_m = re.search(r'^#{0,2}\s*参考答案\s*$', seg, re.M)
        passage = seg[:a_m.start()] if a_m else seg[:ans_m.start() if ans_m else len(seg)]
        trans = seg[a_m.end():ans_m.start()] if (a_m and ans_m) else (seg[a_m.end():] if a_m else "")
        ans_zone = seg[ans_m.end():] if ans_m else ""
        answers = dict(re.findall(r'[（(](\d{1,2})[)）]\s*[:：]?\s*([A-D]{1,4})(?![A-Za-z])', ans_zone))
        gid = f"G-{year}-{half}-{n1:03d}"
        groups[gid] = {"stem": clean_text(passage), "translation": clean_text(trans) or None}
        for n in range(n1, n2+1):
            om = re.search(rf'^[（(]{n}[）)]\s*(.*)$', seg, re.M)
            options = []
            if om:
                region = om.group(1)
                if n < n2:
                    nm2 = re.search(rf'^[（(]{n+1}[）)]', seg[om.end():], re.M)
                    if nm2: region += ' ' + seg[om.end(): om.end()+nm2.start()]
                else:
                    nm2 = re.search(r'^#{0,2}\s*(参考译文|参考答案)', seg[om.end():], re.M)
                    if nm2: region += ' ' + seg[om.end(): om.end()+nm2.start()]
                parts = re.split(r'([A-D])\s*[\.．、]\s*', region)
                for j in range(1, len(parts)-1, 2):
                    options.append({"key": parts[j], "text": re.sub(r'\s+', ' ', parts[j+1]).strip()})
            qs.append({"id": f"M-{year}-{half}-{n:03d}", "year": year, "half": half,
                       "subject":1, "num":n, "type":"choice", "stem":"", "options":options,
                       "answer": answers.get(str(n)), "analysis": None, "translation": None,
                       "group": gid, "knowledge": None, "source": "官方解析书"})
    return qs, groups

def parse_morning_chapter(text, year, half):
    text = re.sub(r'^#{1,2}\s*第\s*\d+\s*章.*$', '', text, flags=re.M)
    text = re.sub(r'^#\s*(上午|下午)试题分析与解答\s*$', '', text, flags=re.M)
    marks = [(m.start(), int(m.group(1)), m.group(2)) for m in
             re.finditer(r'^#{0,2}\s*试题\s*[（(](\d+)[）)](?:～\s*[（(](\d+)[）)])?\s*$', text, re.M)]
    qs = []
    for i,(pos,num,num2) in enumerate(marks):
        end = marks[i+1][0] if i+1 < len(marks) else len(text)
        if num2: continue  # 组题块: 由 parse_group_questions 处理, 仅作边界
        seg = text[pos:end]
        seg = re.sub(r'^#{0,2}\s*试题\s*[（(]\d+[）)]\s*$', '', seg, count=1, flags=re.M)
        a_m = re.search(r'^#{0,2}\s*试题\s*[（(]\d+[）)]分析\s*$', seg, re.M)
        ans_m = None
        for am in re.finditer(r'^#{0,2}\s*参考答案\s*$', seg, re.M):
            if (not a_m) or am.start() > a_m.start(): ans_m = am; break
        stem_zone = seg[:a_m.start()] if a_m else (seg[:ans_m.start()] if ans_m else seg)
        ana_zone  = seg[a_m.end():ans_m.start()] if (a_m and ans_m) else (seg[a_m.end():] if a_m else "")
        ans_zone  = seg[ans_m.end():] if ans_m else ""
        opt_start = None
        for lm in re.finditer(r'^(?:[（(]\d{1,2}[）)])?\s*(?=[A-D][\.．、])', stem_zone, re.M):
            opt_start = lm.start(); break
        options, stem = [], stem_zone
        if opt_start is not None:
            stem = stem_zone[:opt_start]
            opt_region = stem_zone[opt_start:]
            parts = re.split(r'(?:^|(?<=[^\x00-\x7f])|(?<=[)）])|\s)([A-D])\s*[\.．、]\s*', opt_region)
            for j in range(1, len(parts)-1, 2):
                options.append({"key": parts[j], "text": re.sub(r'\s+', ' ', parts[j+1]).strip()})
        stem = re.sub(r'\n+', ' ', stem).strip()
        stem = re.sub(r'^\d{1,2}[\.、．]\s*', '', stem)
        answers = dict(re.findall(r'[（(](\d{1,2})[)）]\s*[:：]?\s*([A-D]{1,4})(?![A-Za-z])', ans_zone))
        qs.append({"id": f"M-{year}-{half}-{num:03d}", "year": year, "half": half,
                   "subject":1, "num":num, "type":"choice", "stem": stem,
                   "options": options, "answer": answers.get(str(num)),
                   "analysis": clean_text(ana_zone) or None, "translation": None,
                   "group": None, "knowledge": None, "source": "官方解析书"})
    return qs

def parse_afternoon_chapter(text, year, half):
    text = re.sub(r'^#{1,2}\s*第\s*\d+\s*章.*$', '', text, flags=re.M)
    text = re.sub(r'^#\s*(上午|下午)试题分析与解答\s*$', '', text, flags=re.M)
    marks = [(m.start(), m.group(1), int(m.group(2))) for m in
             re.finditer(r'^#{0,2}\s*试题([一二三四五六七八])\s*[（(]\s*共\s*(\d+)\s*分\s*[）)]', text, re.M)]
    cases = []
    for i,(pos,cn,score) in enumerate(marks):
        end = marks[i+1][0] if i+1 < len(marks) else len(text)
        seg = text[pos:end]
        seg = re.sub(r'^#{0,2}\s*试题[一二三四五六七八]\s*[（(]\s*共\s*\d+\s*分\s*[）)]', '', seg, count=1, flags=re.M)
        a_m = re.search(r'^#{0,2}\s*试题[一二三四五六七八]分析\s*$', seg, re.M)
        ans_m = None
        for am in re.finditer(r'^#{0,2}\s*参考答案\s*$', seg, re.M):
            if (not a_m) or am.start() > a_m.start(): ans_m = am; break
        q_zone  = seg[:a_m.start()] if a_m else (seg[:ans_m.start()] if ans_m else seg)
        ana_zone = seg[a_m.end():ans_m.start()] if (a_m and ans_m) else (seg[a_m.end():] if a_m else "")
        ans_zone = seg[ans_m.end():] if ans_m else ""
        scenario = ""
        sm = re.search(r'【说明】', q_zone)
        if sm:
            scenario = q_zone[sm.end():]
        else:
            scenario = q_zone
        scenario = re.sub(r'^[^【\n]*说明[^。\n]*。', '', scenario.strip())
        scenario = re.sub(r'^阅读下列说明.*?对应栏内。', '', scenario.strip(), flags=re.M)
        qmarks = [(m.start(), int(m.group(1))) for m in re.finditer(r'^#{0,2}\s*【问题\s*(\d+)】', q_zone, re.M)]
        scen_end = qmarks[0][0] if qmarks else len(q_zone)
        if sm:
            scenario = q_zone[sm.end():scen_end]
        subs = []
        for j,(qp,qn) in enumerate(qmarks):
            qend = qmarks[j+1][0] if j+1 < len(qmarks) else len(q_zone)
            qtext = re.sub(r'^#{0,2}\s*【问题\s*\d+】', '', q_zone[qp:qend], count=1, flags=re.M)
            sc_m = re.search(r'[（(]\s*(\d+)\s*分\s*[）)]', qtext)
            sc = int(sc_m.group(1)) if sc_m else None
            qtext = re.sub(r'[（(]\s*\d+\s*分\s*[）)]', '', qtext).strip()
            subs.append({"no": qn, "text": clean_text(qtext), "score": sc,
                         "answer": None, "analysis": None, "reconstructed": False})
        amarks = [(m.start(), int(m.group(1))) for m in re.finditer(r'^#{0,2}\s*【问题\s*(\d+)】', ana_zone, re.M)]
        overview = clean_text(ana_zone[:amarks[0][0]]) if amarks else clean_text(ana_zone)
        for j,(ap,an) in enumerate(amarks):
            aend = amarks[j+1][0] if j+1 < len(amarks) else len(ana_zone)
            atxt = clean_text(re.sub(r'^#{0,2}\s*【问题\s*\d+】', '', ana_zone[ap:aend], count=1, flags=re.M))
            for s in subs:
                if s["no"] == an: s["analysis"] = atxt; break
        amarks = [(m.start(), int(m.group(1))) for m in re.finditer(r'^#{0,2}\s*【问题\s*(\d+)】', ans_zone, re.M)]
        overall = None
        if not amarks and ans_zone.strip(): overall = clean_text(ans_zone)
        for j,(ap,an) in enumerate(amarks):
            aend = amarks[j+1][0] if j+1 < len(amarks) else len(ans_zone)
            atxt = clean_text(re.sub(r'^#{0,2}\s*【问题\s*\d+】', '', ans_zone[ap:aend], count=1, flags=re.M))
            for s in subs:
                if s["no"] == an: s["answer"] = atxt; break
        cases.append({"id": f"C-{year}-{half}-{CN_NUM.get(cn,0)}", "year": year, "half": half,
                      "subject":2, "idx": CN_NUM.get(cn,0), "cn": cn, "score": score,
                      "title": None, "scenario": clean_text(scenario), "qs": subs,
                      "overview": overview or None, "overall_answer": overall,
                      "answerStatus": "official", "source": "官方解析书(2018-2022)"})
    return cases

# ================================================================ B. 案例HTML
def parse_case_html(path, source_tag):
    raw = open(path, encoding="utf-8").read()
    bm = re.search(r'<main>(.*)</main>', raw, re.S)
    body = bm.group(1) if bm else raw
    cases = []
    ym = [(m.start(), int(m.group(1)), 1 if m.group(2)=='上' else 2) for m in
          re.finditer(r'<h1 class="year"[^>]*>.*?(\d{4})年(上|下)半年', body, re.S)]
    for i,(pos,year,half) in enumerate(ym):
        yseg = body[pos: ym[i+1][0] if i+1 < len(ym) else len(body)]
        exm = [(m.start(), m.end(), m.group(1)) for m in re.finditer(r'<h2 class="exam"[^>]*>(.*?)</h2>', yseg, re.S)]
        for j,(spos,send,h2) in enumerate(exm):
            cseg = yseg[send: exm[j+1][0] if j+1 < len(exm) else len(yseg)]
            h2txt = html_to_text(h2)
            cnm = re.search(r'试题([一二三四五六七八])', h2txt)
            scm = re.search(r'（\s*(\d+)\s*分\s*）', h2txt)
            title = re.sub(r'^试题[一二三四五六七八]（[^）]*）[：:]?\s*', '', h2txt)
            cn = cnm.group(1) if cnm else "?"
            idx = CN_NUM.get(cn, j+1)
            note_m = re.search(r'<div class="note">(.*?)</div>\s*(?=<h3|<p>|<div class="figure|<img|<div class="answer)', cseg, re.S)
            note_html = note_m.group(1) if note_m else ""
            recon_case = 'tag-red' in note_html
            scenario = html_to_text(note_html)
            scenario = re.sub(r'^【说明】', '', scenario).strip()
            tokens = re.split(r'(<h3 class="q">.*?</h3>|<div class="answer">.*?</div>|<div class="analysis">.*?</div>)', cseg, flags=re.S)
            subs, cur, qseq = [], None, 0
            def flush():
                nonlocal cur
                if cur is not None: subs.append(cur); cur = None
            for t in tokens:
                if not t: continue
                if t.startswith('<h3 class="q"'):
                    flush(); qseq += 1
                    no_m = re.search(r'【问题\s*(\d+)', t)
                    cur = {"no": int(no_m.group(1)) if no_m else qseq,
                           "text": "", "score": None, "answer": None, "analysis": None,
                           "reconstructed": ('tag-red' in t) or recon_case}
                    head_txt = html_to_text(t)
                    head_txt = re.sub(r'^【问题\s*\d+】\s*', '', head_txt).strip()
                    if head_txt and not re.match(r'^\d+$', head_txt): cur["text"] = head_txt
                elif t.startswith('<div class="answer"'):
                    if cur is not None:
                        cur["answer"] = html_to_text(re.sub(r'^<div class="answer">|</div>$','',t)) or None
                elif t.startswith('<div class="analysis"'):
                    if cur is not None:
                        txt = html_to_text(re.sub(r'^<div class="analysis">|</div>$','',t))
                        cur["analysis"] = clean_text(re.sub(r'^📝\s*解析[：:]\s*','',txt)) or None
                else:
                    if cur is not None:
                        txt = html_to_text(t)
                        if txt:
                            if txt.startswith('问题：') and 'null' in txt:
                                cur["missing"] = True
                            else:
                                cur["text"] = (cur["text"] + "\n" + txt).strip()
            flush()
            missing = [s["no"] for s in subs if s.get("missing")]
            subs = [s for s in subs if not s.get("missing")]
            for s in subs: s.pop("missing", None)
            status = "official"
            if year == 2025: status = "reference"
            elif year >= 2023: status = "compiled"
            elif year <= 2017: status = "compiled"
            cases.append({"id": f"C-{year}-{half}-{idx}", "year": year, "half": half,
                          "subject":2, "idx": idx, "cn": cn,
                          "score": int(scm.group(1)) if scm else None,
                          "title": title or None, "scenario": scenario, "qs": subs,
                          "overview": None, "overall_answer": None,
                          "answerStatus": status, "missing_subs": missing, "source": source_tag})
    return cases

# ================================================================ C. 教程
TB_PARTS = [
    (1, "资料/MinerU_markdown_信息安全工程师教程（第2版）_(蒋建春)_1-200页.md",
        "资料/MinerU_html_信息安全工程师教程（第2版）_(蒋建春)_1-200页.html", (1,9)),
    (2, "资料/MinerU_markdown_信息安全工程师教程（第2版）_(蒋建春)_201-400页.md",
        "资料/MinerU_html_信息安全工程师教程（第2版）_(蒋建春)_201-400页.html", (10,18)),
    (3, "资料/MinerU_markdown_信息安全工程师教程（第2版）_(蒋建春)_401-599页.md",
        "资料/MinerU_html_信息安全工程师教程（第2版）_(蒋建春)_401-599.html", (19,26)),
]

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def md_inline(ln):
    ln = re.sub(r'!\[[^\]]*\]\(([^)]+)\)', r'<img src="\1" style="max-width:100%">', ln)
    ln = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', ln)
    ln = re.sub(r'`([^`]+)`', r'<code>\1</code>', ln)
    return ln

def md_to_html(md):
    out, in_code = [], False
    for ln in md.split('\n'):
        if ln.strip().startswith('```'):
            out.append('</pre>' if in_code else '<pre>'); in_code = not in_code; continue
        if in_code:
            out.append(esc(ln)); continue
        st = ln.strip()
        if not st: out.append(''); continue
        if st.startswith('<table') or st.startswith('</table') or st.startswith('<tr'):
            out.append(ln); continue
        hm = re.match(r'^#{1,6}\s+(.*)$', st)
        if hm:
            t = hm.group(1).strip()
            if re.match(r'^第\s*\d+\s*章', t): continue
            sm = re.match(r'^(\d+(?:\.\d+)+)\s*(.*)$', t)
            if sm:
                lvl = min(sm.group(1).count('.') + 2, 5)
                out.append(f'<h{lvl}>{sm.group(1)} {md_inline(esc(sm.group(2)))}</h{lvl}>'); continue
            out.append(f'<h4>{md_inline(esc(t))}</h4>'); continue
        if re.match(r'^[-*•]\s+', st):
            out.append(f'<p>• {md_inline(esc(re.sub(r"^[-*•]\s+", "", st)))}</p>'); continue
        if re.match(r'^\d+\.\s+', st) and len(st) < 120:
            out.append(f'<p><b>{md_inline(esc(st))}</b></p>'); continue
        out.append(f'<p>{md_inline(esc(ln))}</p>')
    html = '\n'.join(out)
    html = re.sub(r'<pre>\n?</pre>', '', html)
    html = re.sub(r'\n{3,}', '\n\n', html)
    return html.strip()

def process_textbook():
    os.makedirs(TB_OUT, exist_ok=True); os.makedirs(TBIMG_OUT, exist_ok=True)
    stats = {"b64":0, "cdn":0, "fail":0}
    ch_segs = {}   # num -> [title, seg, part]
    for part, md_f, html_f, rng in TB_PARTS:
        md = open(os.path.join(ROOT, md_f), encoding="utf-8").read()
        html = open(os.path.join(ROOT, html_f), encoding="utf-8").read()
        html_imgs = re.findall(r'<img[^>]+src="([^"]+)"[^>]*>', html)
        refs = [(m.start(), m.end(), m.group(1)) for m in re.finditer(r'!\[[^\]]*\]\((https?://[^)]+)\)', md)]
        log(f"  [教程] 册{part}: MD图 {len(refs)} / HTML图 {len(html_imgs)}")
        pieces, last = [], 0
        for i,(s,e,url) in enumerate(refs):
            local = None
            if i < len(html_imgs) and html_imgs[i].startswith('data:image/'):
                mm = re.match(r'data:image/([^;]+);base64,(.*)', html_imgs[i], re.S)
                if mm and mm.group(2).strip():
                    ext = {'jpeg':'jpg','svg+xml':'svg'}.get(mm.group(1), mm.group(1))
                    fname = f"tb{part}_{i+1:03d}.{ext}"
                    fpath = os.path.join(TBIMG_OUT, fname)
                    if not os.path.exists(fpath):
                        try:
                            open(fpath,'wb').write(base64.b64decode(re.sub(r'\s','',mm.group(2))))
                        except Exception as ex:
                            log(f"    [b64解码失败] 册{part}#{i+1}: {ex}"); fpath=None
                    if fpath and os.path.exists(fpath):
                        local = f"assets/textbook/{fname}"; stats["b64"] += 1
            if not local:
                m2 = re.search(r'\.(jpe?g|png|gif|svg)$', url.split('?')[0])
                ext = ('.'+m2.group(1)) if m2 else '.jpg'
                ext = ext.replace('.jpeg','.jpg')
                fname = f"tb{part}_{i+1:03d}{ext}"
                fpath = os.path.join(TBIMG_OUT, fname)
                if not os.path.exists(fpath):
                    if dl(url, fpath): stats["cdn"] += 1
                    else: stats["fail"] += 1; fname=None
                if fname and os.path.exists(fpath):
                    local = f"assets/textbook/{fname}"
            pieces.append(md[last:s]); pieces.append(f"![img]({local})" if local else f"![img缺失#{i+1}]({url})")
            last = e
        pieces.append(md[last:])
        md2 = ''.join(pieces)
        heads = {}
        for m in re.finditer(r'^#{1,2}\s*第\s*(\d+)\s*章\s*(.*)$', md2, re.M):
            num = int(m.group(1))
            if rng[0] <= num <= rng[1]:
                heads[num] = (m.start(), re.sub(r'\s+','',m.group(2)))
        if not heads:
            log(f"  [教程] 册{part}: 未找到章标题!"); continue
        ordered = sorted(heads.items(), key=lambda kv: kv[1][0])
        first_pos = ordered[0][1][0]
        leftover = md2[:first_pos]
        for k,(num,(pos,title)) in enumerate(ordered):
            end = ordered[k+1][1][0] if k+1 < len(ordered) else len(md2)
            seg = md2[pos:end]
            if num in ch_segs:
                ch_segs[num][1] += "\n" + seg
            else:
                ch_segs[num] = [title, seg, part]
        if part > 1 and len(leftover.strip()) > 150 and ch_segs:
            prev_num = max(n for n in ch_segs if n < rng[0]) if any(n < rng[0] for n in ch_segs) else None
            if prev_num:
                log(f"  [教程] 册{part} 开头残留 {len(leftover)} 字 → 并入第{prev_num}章")
                ch_segs[prev_num][1] += "\n" + leftover
    manifest = {}
    for num in sorted(ch_segs):
        title, seg, part = ch_segs[num]
        seg = re.sub(r'^#{1,2}\s*第\s*\d+\s*章\s*.*$', '', seg, count=1, flags=re.M)
        secs, seen = [], set()
        for sm in re.finditer(r'^#{1,6}\s+(\d+(?:\.\d+)+)\s+(.+)$', seg, re.M):
            no, t = sm.group(1), re.sub(r'\s+',' ',sm.group(2)).strip()
            if t not in seen:
                seen.add(t); secs.append({"no": no, "title": t, "level": no.count('.')+2})
        fname = f"ch{num:02d}.js"
        html_content = md_to_html(seg)
        n_imgs = len(re.findall(r'<img ', html_content))
        manifest[str(num)] = {"no": num, "title": title, "part": part, "file": fname,
                              "sections": secs, "chars": len(seg), "images": n_imgs}
        with open(os.path.join(TB_OUT, fname), 'w', encoding='utf-8') as f:
            f.write(f'/*教程第{num}章 自动生成*/\nwindow.TEXTBOOK=window.TEXTBOOK||{{}};window.TEXTBOOK["{num}"]=')
            f.write(json.dumps({"no":num,"title":title,"html":html_content}, ensure_ascii=False, separators=(',',':')))
            f.write(';\n')
        log(f"  [章{num:02d}] {title} | 节{len(secs)} 图{n_imgs} {len(seg)//1024}KB")
    with open(os.path.join(TB_OUT, "manifest.js"), 'w', encoding='utf-8') as f:
        f.write('window.TB_MANIFEST=')
        f.write(json.dumps(manifest, ensure_ascii=False, separators=(',',':')))
        f.write(';\n')
    log(f"  [图片统计] base64:{stats['b64']} CDN:{stats['cdn']} 失败:{stats['fail']}")
    return manifest, stats, ch_segs

# ================================================================ C2. 知识点单元 (教程全量覆盖)
def condense(md, limit=3000):
    md = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', md)
    md = re.sub(r'<img[^>]*>', '', md)
    md = re.sub(r'<table.*?</table>', '［表格］', md, flags=re.S | re.I)
    lines = []
    for ln in md.split('\n'):
        ln = re.sub(r'^#{1,6}\s+', '', ln.strip())
        if ln: lines.append(ln)
    txt = re.sub(r'\n{2,}', '\n', '\n'.join(lines))
    return (txt[:limit] + '…') if len(txt) > limit else txt

S2CH = {22:5, 23:6, 24:7, 25:8, 26:9}

def build_units(ch_segs, syllabus, syb_raw):
    units = []
    # ---- A) 教程全量单元 (N.N 与 N.N.N; 节内编号条目转为要点) ----
    for num in sorted(ch_segs):
        title, seg, part = ch_segs[num]
        seg = re.sub(r'^#{1,2}\s*第\s*\d+\s*章\s*.*$', '', seg, count=1, flags=re.M)
        heads = [(m.start(), m.group(1), re.sub(r'\s+',' ',m.group(2)).strip()) for m in
                 re.finditer(r'^#{1,6}\s+(\d+(?:\.\d+)*)\s+(.+)$', seg, re.M)]
        sec_heads = [(p,n,t) for (p,n,t) in heads if '.' in n and n.startswith(str(num)+'.') and len(t)<=60]
        for k,(pos,no,ttl) in enumerate(sec_heads):
            end = sec_heads[k+1][0] if k+1 < len(sec_heads) else len(seg)
            body = seg[pos:end]
            body = re.sub(r'^#{1,6}\s+'+re.escape(no)+r'\s+.*$', '', body, count=1, flags=re.M)
            # 节内编号条目 -> 要点
            points = []
            imarks = [(m.start(), m.end(), m.group(1), re.sub(r'\s+',' ',m.group(2)).strip()) for m in
                      re.finditer(r'^#{1,6}\s+(\d+)[\.、]\s*([^\d.][^\n]{1,50})$', body, re.M)]
            if imarks:
                for j,(sp,ep,inum,ittl) in enumerate(imarks):
                    iend = imarks[j+1][0] if j+1 < len(imarks) else len(body)
                    ictnt = condense(body[ep:iend], 400)
                    points.append({"t": f"{inum}. {ittl}", "d": ictnt})
            body_nopoints = body
            if imarks: body_nopoints = body[:imarks[0][0]]
            plain = condense(body_nopoints, 2800)
            paras = [p.strip() for p in plain.split('\n') if p.strip()]
            define = paras[0][:220] if paras else ""
            extra_bullets = []
            for bl in re.finditer(r'^(?:[•\-◆]\s*|\d+[）)].{1}\s*)(.{3,80})$', body, re.M):
                extra_bullets.append(bl.group(1).strip())
            if len(paras) > 1 or (points or extra_bullets):
                pass
            level = no.count('.')
            units.append({
                "id": "U"+no, "no": no, "title": ttl, "ch": num,
                "subject": 1 if num <= 21 else 2,
                "s2ch": S2CH.get(num),
                "level": level,
                "define": define, "points": points,
                "bullets": extra_bullets[:12],
                "content": plain, "chars": len(plain),
            })
    # ---- B) 大纲兜底单元: S2 ch1-4 (实践章) 与 S1 ch22 专业英语 ----
    for c in syllabus["subject2"]:
        if int(c["no"]) > 4: continue
        for child in c["children"]:
            bl = [child["title"]]
            units.append({"id": "G2-"+child["no"], "no": "2."+child["no"], "title": c["title"]+"·"+child["title"],
                          "ch": None, "subject": 2, "s2ch": int(c["no"]), "level": 1,
                          "define": "实践性章节（教程无对应正文），以大纲要求与相关案例掌握。",
                          "points": [], "bullets": bl[:10],
                          "content": "大纲要求: "+child["title"], "chars": 20})
    units.append({"id": "G1-22", "no": "22", "title": "网络信息安全专业英语", "ch": None,
                  "subject": 1, "s2ch": None, "level": 1,
                  "define": "上午卷第71-75题英语阅读，考查安全领域英文术语与短文理解。",
                  "points": [{"t": "应试策略", "d": "积累高频安全术语(如 attack/vulnerability/encryption/authentication/firewall/malware)，先读题干空格前后句再回原文定位。"}],
                  "bullets": [], "content": "历年真题英语组题共5套(71-75题)，见真题卷练习。", "chars": 30})
    # ---- C) 大纲叶条目归属 ----
    for b in parse_syllabus_bullets(syb_raw):
        sec = b["sec"]
        target = next((u for u in units if u["no"]==sec), None)
        if not target:
            parent = '.'.join(sec.split('.')[:2])
            target = next((u for u in units if u["no"]==parent), None)
        if target is not None and len(target.get("bullets",[])) < 14:
            target.setdefault("bullets", []).append(b["text"])
    return units

def extract_exam_point(analysis):
    m = re.search(r'本(?:题|问题)考[查察]\s*([^。\n]{2,70})', analysis or '')
    return m.group(1).strip() if m else None

def tokset(t):
    return set(x for x in tokenize(t) if len(x) >= 2)

def map_unit(text, units, prefer_ch=None):
    """按单元标题+要点关键词匹配最佳单元; prefer_ch 优先同章"""
    ts = tokset(text)
    best, bs = None, 0
    for u in units:
        sc = 0
        ut = tokset(u["title"])
        for k in ts:
            for t in ut:
                if k in t or t in k: sc += 1; break
        if prefer_ch and u["ch"] == prefer_ch: sc += 1
        if sc > bs: best, bs = u, sc
    return best if bs >= 2 else None

def q_types(q):
    text = (q.get("stem") or '') + ' ' + (q.get("analysis") or '')
    tags = []
    if re.search(r'RSA|密钥长度|分组长度|\d+\s*比特|\d+\s*字节|模运算|进制|余数|指数|私钥|公钥为|公钥密码体制中|加密结果|循环左移|S盒', text): tags.append("计算")
    if re.search(r'条例|办法|规定|国家标准|GB/?T? ?\d|ISO/?IEC|网络安全法|密码法|等级保护|管理办法|指导意见|政策|法律', text): tags.append("法规")
    if re.search(r'nmap|Snort|snort|Wireshark|tcpdump|Tcpdump|John|L0phtCrack|Tripwire|netstat|fport|OllyDbg|GDB|strings|tracert|JMeter|LoadRunner|Nessus|GetAcct|分布式,|扫描器|防火墙工具|下列(工具|命令)', text): tags.append("工具")
    if re.search(r'某公司|某单位|某企业|某机构|如图|下图|图中|案例中|网络结构|拓扑', text): tags.append("场景")
    if not tags: tags.append("原理")
    return tags

def build_textbook_sections(ch_segs):
    secs = {}
    for num in sorted(ch_segs):
        title, seg, part = ch_segs[num]
        seg = re.sub(r'^#{1,2}\s*第\s*\d+\s*章\s*.*$', '', seg, count=1, flags=re.M)
        heads = [(m.start(), m.group(1), re.sub(r'\s+',' ',m.group(2)).strip()) for m in
                 re.finditer(r'^#{1,6}\s+(\d+(?:\.\d+)+)\s+(.+)$', seg, re.M)]
        for k,(pos,no,ttl) in enumerate(heads):
            if not no.startswith(str(num)+'.'): continue
            if len(ttl) > 60: continue
            end = heads[k+1][0] if k+1 < len(heads) else len(seg)
            body = re.sub(r'^#{1,6}\s+'+re.escape(no)+r'\s+.*$', '', seg[pos:end], count=1, flags=re.M)
            content = condense(body)
            if len(content) < 40: continue
            secs[no] = {"no": no, "title": ttl, "ch": num, "content": content, "level": no.count('.')}
    return secs

def parse_syllabus_bullets(raw):
    s1 = raw.find('考试科目 1：网络信息安全基础知识和技术')
    s2 = raw.find('考试科目 2：网络信息安全工程与综合应用实践')
    e3 = raw.find('三、题型举例')
    out = []
    for subject, seg in ((1, raw[s1:s2] if 0<s1<s2 else ""), (2, raw[s2:e3] if 0<s2<e3 else "")):
        cur_sec = None
        for ln in seg.split('\n'):
            t = ln.strip()
            hmm = re.match(r'^#{0,2}\s*(\d{1,2}\.\d{1,2})(?:\.\d{1,2})?\s+\S', t)
            if hmm: cur_sec = hmm.group(1); continue
            bm = re.match(r'^[•\-◆·]\s*(.+)$', t)
            if bm and cur_sec:
                txt = bm.group(1).strip()
                if 2 < len(txt) < 80:
                    out.append({"sec": cur_sec, "subject": subject, "text": txt})
    return out

CH_KW = {
 (1,1):"机密性 完整性 可用性 抗抵赖 可控性 CIA 信息安全目标 网络安全法 等级保护 法律 法规 政策 管理 网络安全战略",
 (1,2):"端口扫描 口令破解 缓冲区溢出 拒绝服务 DDoS 网络钓鱼 SQL注入 会话劫持 嗅探 社会工程 攻击树 APT 跨站 XSS 后门 隐藏 攻击过程",
 (1,3):"密码 加密 解密 DES AES RSA SM2 SM3 SM4 SM9 国密 哈希 Hash 散列 数字签名 数字证书 PKI 密钥 对称 公钥 私钥 分组 序列 ECB CBC CFB OFB SSL SSH Diffie 消息摘要 杂凑 一次性口令",
 (1,4):"安全模型 BLP BiBa 信息流 纵深防御 分层防护 生存 安全策略 体系框架 ISO27000 成熟度 信息保障",
 (1,5):"物理安全 机房 防雷 防静电 电磁 供电 存储介质 通信线路 防震 防水 接地",
 (1,6):"认证 口令认证 智能卡 生物特征 Kerberos 单点登录 身份认证 鉴别 认证技术",
 (1,7):"访问控制 DAC MAC RBAC 自主访问 强制访问 基于角色 最小特权 参考监视器 授权",
 (1,8):"防火墙 包过滤 代理 NAT 地址转换 Web防火墙 下一代防火墙 区域隔离 安全区域",
 (1,9):"VPN IPSec PPTP L2TP IKE 隧道 远程访问 安全专网",
 (1,10):"入侵检测 IDS IPS 误用 异常检测 Snort HIDS NIDS 分布式入侵 报警关联",
 (1,11):"物理隔离 网闸 摆渡 协议隔离 单向传输 物理断开 内外网",
 (1,12):"审计 Syslog tcpdump 日志 电子取证 流量采集 端口镜像 安全审计",
 (1,13):"漏洞 CVE CNVD CNNVD OWASP 漏洞扫描 加固 补丁 漏洞库 漏洞发布",
 (1,14):"恶意代码 病毒 蠕虫 木马 特洛伊 僵尸网络 勒索 Rootkit 宏病毒 逻辑炸弹 间谍软件 陷门",
 (1,15):"入侵阻断 白名单 流量清洗 可信计算 数字水印 攻击陷阱 入侵容忍 隐私保护 威胁情报 同态加密 蜜罐 主动防御",
 (1,16):"风险评估 资产识别 威胁识别 脆弱性 风险计算 风险分析 风险评估工具 风险处置",
 (1,17):"应急响应 应急预案 应急演练 事件分级 CTF 红蓝对抗 事件报告 处置流程",
 (1,18):"测评 等级保护测评 渗透测试 代码审查 协议分析 JMeter LoadRunner 验收测评 测评标准 测评流程",
 (1,19):"Windows Linux UNIX 操作系统 注册表 账户 口令策略 系统加固 国产操作系统",
 (1,20):"数据库 Oracle SQLServer MySQL 数据库审计 数据库加密 脱敏 数据库防火墙",
 (1,21):"交换机 路由器 网络设备 VTY SNMP MAC地址 网络设备漏洞",
 (1,22):"英语 English 英文",
 (2,1):"风险评估实践 需求分析 日志分析 数据收集 syslog 协议分析器",
 (2,2):"方案设计 安全增强方案 保护方案 监控方案 常用方案",
 (2,3):"部署 产品技术资料 安装 配置与使用 设备部署",
 (2,4):"安全配置 运维 管理 Apache IIS 配置与管理",
 (2,5):"网站 Web Apache IIS SQL注入 XSS 文件上传 目录遍历 网站安全 网站保护",
 (2,6):"云计算 云平台 虚拟机 多租户 IaaS PaaS SaaS 云运维 云服务",
 (2,7):"工控 工业控制 SCADA PLC DCS 工控协议 工控防火墙 数控",
 (2,8):"移动 Android iOS App 沙箱 移动办公 移动应用 逆向",
 (2,9):"大数据 数据安全 数据脱敏 差分隐私 数据溯源 跨境 数据分类分级",
}
def tokenize(t):
    t = re.sub(r'[（(][^）)]*[）)]', ' ', t)
    parts = re.split(r'[^\u4e00-\u9fa5A-Za-z0-9]+', t)
    out = []
    for p in parts:
        if len(p) >= 2: out.append(p)
        if len(p) >= 6:
            for glue in ('与','和','及'):
                if glue in p: out += [x for x in p.split(glue) if len(x) >= 2]
    return out

def build_ch_index(syllabus):
    idx = []
    for s, key in ((1,'subject1'), (2,'subject2')):
        for c in syllabus[key]:
            kws = set(tokenize(c["title"]))
            for k in c["children"]: kws |= set(tokenize(k["title"]))
            kws |= set(tokenize(CH_KW.get((s, int(c["no"])), '')))
            idx.append({"s": s, "ch": int(c["no"]), "kw": kws})
    return idx

def map_ch(text, idx):
    best, bs = None, 0
    for e in idx:
        sc = sum(1 for k in e["kw"] if k in text)
        if sc > bs: best, bs = {"subject": e["s"], "ch": e["ch"]}, sc
    return best if bs >= 2 else None

# ================================================================ D. 大纲
S1_CH = ["网络信息安全概述","网络攻击原理与常用方法","密码学基本理论","网络安全体系与网络安全模型",
 "物理与环境安全技术","认证技术原理与应用","访问控制技术原理与应用","防火墙技术原理与应用",
 "VPN技术原理与应用","入侵检测技术原理与应用","网络物理隔离技术原理与应用","网络安全审计技术原理与应用",
 "网络安全漏洞防护技术原理与应用","恶意代码防范技术原理","网络安全主动防御技术原理与应用",
 "网络安全风险评估技术原理与应用","网络安全应急响应技术原理与应用","网络安全测评技术与标准",
 "操作系统安全保护","数据库系统安全","网络设备安全","网络信息安全专业英语"]
S2_CH = ["网络安全风险评估与需求分析","网络安全常用方案设计","网络安全设备部署与使用",
 "网络信息系统安全配置与管理","网站安全需求分析与安全保护工程","云计算安全需求分析与安全保护工程",
 "工控安全需求分析与安全保护工程","移动应用安全需求分析与安全保护工程","大数据安全需求分析与安全保护工程"]
TB2SYL = {**{n:(1,n) for n in range(1,22)}, 22:(2,5), 23:(2,6), 24:(2,7), 25:(2,8), 26:(2,9)}

def parse_syllabus(path):
    raw = open(path, encoding="utf-8").read()
    s1 = raw.find('考试科目 1：网络信息安全基础知识和技术')
    s2 = raw.find('考试科目 2：网络信息安全工程与综合应用实践')
    e3 = raw.find('三、题型举例')
    def build(seg, chapters, subject):
        secs = {}
        for m in re.finditer(r'^#{0,2}\s*(\d{1,2})\.(\d{1,2})\s+(.+)$', seg, re.M):
            a, b, t = int(m.group(1)), int(m.group(2)), m.group(3).strip()
            secs.setdefault(a, []).append((f"{a}.{b}", re.sub(r'\s+',' ',t)))
        out = []
        for i, ch in enumerate(chapters, 1):
            kids, seen = [], set()
            for no, t in secs.get(i, []):
                if t not in seen: seen.add(t); kids.append({"no": no, "title": t})
            tb = [k for k,v in TB2SYL.items() if v==(subject,i)]
            out.append({"no": str(i), "title": ch, "subject": subject, "children": kids,
                        "tb": tb, "qcount": 0})
        return out
    return {"subject1": build(raw[s1:s2] if 0<s1<s2 else "", S1_CH, 1),
            "subject2": build(raw[s2:e3] if 0<s2<e3 else "", S2_CH, 2)}

# ================================================================ main
def main():
    for d in (OUT, TB_OUT, IMG_OUT, TBIMG_OUT): os.makedirs(d, exist_ok=True)
    MD = "资料/MinerU_markdown_信息安全工程师2018至2022试题分析与解答_(清华大学出版社)_(z-library.sk,_1lib.sk,_z-lib.sk)_2093262293397954560.md"
    H1 = "资料/信息安全工程师2016-2022下午案例真题整理版-内嵌图片版-修复版-内嵌图片版.html"
    H2 = "资料/2023-2025年信息安全工程师下午案例真题整理版-2016-2022样式-内嵌图片版-修复版-内嵌图片版.html"
    SYB = "资料/MinerU_markdown_信息安全工程师考试大纲_(全国计算机专业技术资格考试办公室)_(z-library.sk,_1lib.sk,_z-lib.sk)_2095059888814444544.md"

    log("== 1/6 试题分析MD ==")
    chapters = parse_analysis_md(os.path.join(ROOT, MD))
    all_q, all_groups, all_cases, md_years = [], {}, [], set()
    for num, year, half, subject, block in chapters:
        ptext = apply_marker_patches(preprocess(block), year, half, subject)
        if subject == 1:
            gq, gs = parse_group_questions(ptext, year, half)
            rq = parse_morning_chapter(ptext, year, half)
            seen = {q["num"] for q in gq}
            rq = [q for q in rq if q["num"] not in seen]
            all_q += gq + rq; all_groups.update(gs)
            log(f"  [上午]{year}-{half}: 常规{len(rq)} 组题{len(gq)}")
        else:
            cs = parse_afternoon_chapter(ptext, year, half)
            all_cases += cs; md_years.add((year,half))
            log(f"  [下午]{year}-{half}: 案例{len(cs)}")

    log("== 2/6 案例HTML(主源) ==")
    c16 = parse_case_html(os.path.join(ROOT, H1), "整理版HTML(2016-2022)")
    c23 = parse_case_html(os.path.join(ROOT, H2), "整理版HTML(2023-2025)")
    log(f"  HTML案例: 2016-2022册 {len(c16)} 个 / 2023-2025册 {len(c23)} 个")
    md_map = {(c["year"], c["half"], c["idx"]): c for c in all_cases}
    merged = []
    for hc in c16 + c23:
        md = md_map.get((hc["year"], hc["half"], hc["idx"]))
        if md:
            hc["md_overview"] = md.get("overview")
            for s in hc["qs"]:
                ms = next((x for x in md["qs"] if x["no"] == s["no"]), None)
                if ms:
                    if not s["answer"] and ms["answer"]: s["answer"] = ms["answer"]
                    if not s["analysis"] and ms["analysis"]: s["analysis"] = ms["analysis"]
        merged.append(hc)
    all_cases = merged
    log(f"  [合并] HTML主源 {len(all_cases)} 例, MD总述补配 {sum(1 for c in all_cases if c.get('md_overview'))} 例")

    log("== 3/6 教程切片 ==")
    tb_manifest, tb_stats, ch_segs = process_textbook()

    log("== 4/6 大纲 ==")
    syb_raw = open(os.path.join(ROOT, SYB), encoding="utf-8").read()
    syllabus = parse_syllabus(os.path.join(ROOT, SYB))
    log(f"  科目1 {len(syllabus['subject1'])}章 / 科目2 {len(syllabus['subject2'])}章")

    log("== 4.5/6 知识点单元(教程全量) ==")
    units = build_units(ch_segs, syllabus, syb_raw)
    for u in units:
        u["scopeCh"] = u["ch"] if u["subject"] == 1 else (u["s2ch"] or 0)
    thin = sum(1 for u in units if u["chars"] < 120)
    log(f"  单元总数 {len(units)} (二级 {sum(1 for u in units if u['level']==1)} / 三级 {sum(1 for u in units if u['level']==2)}) 薄内容 {thin}")
    # "本题考查X" 精准映射
    chidx = build_ch_index(syllabus)
    qch, cch, qunit, cunit, qtype, qpoint = {}, {}, {}, {}, {}, {}
    eng_n, ep_n = 0, 0
    for q in all_q:
        if q["group"]:
            qch[q["id"]] = {"subject":1, "ch":22}; qunit[q["id"]] = "G1-22"; eng_n += 1; continue
        m = map_ch((q["stem"] or '') + ' ' + (q["analysis"] or ''), chidx)
        if m: qch[q["id"]] = m
        ep = extract_exam_point(q["analysis"])
        if ep:
            ep_n += 1; qpoint[q["id"]] = ep
            pref = m["ch"] if m else None
            u = map_unit(ep, units, prefer_ch=pref if (m and m["subject"]==1) else None)
            if u: qunit[q["id"]] = u["id"]
        if not qunit.get(q["id"]) and m:
            u2 = map_unit((q["stem"] or ''), units, prefer_ch=m["ch"] if m["subject"]==1 else None)
            if u2: qunit[q["id"]] = u2["id"]
        qtype[q["id"]] = q_types(q)
    for c in all_cases:
        for s in c["qs"]:
            key = f'{c["id"]}#{s["no"]}'
            m = map_ch((c["scenario"] or '') + ' ' + (s["text"] or '') + ' ' + (s["analysis"] or ''), chidx)
            if m: cch[key] = m
            ep = extract_exam_point(s.get("analysis") or c.get("md_overview"))
            u = None
            if ep:
                u = map_unit(ep + ' ' + (s["text"] or '')[:60], units, prefer_ch=(m["ch"] if (m and m["subject"]==1) else None))
            if not u and m:
                u = map_unit((s["text"] or '')[:80], units, prefer_ch=m["ch"] if m["subject"]==1 else None)
            if u: cunit[key] = u["id"]
    # 考频写入单元
    freq = {}
    for qid, uid in qunit.items(): freq[uid] = freq.get(uid, 0) + 1
    for k, uid in cunit.items(): freq[uid] = freq.get(uid, 0) + 1
    for u in units: u["freq"] = freq.get(u["id"], 0)
    freq_n = sum(1 for u in units if u["freq"] > 0)
    log(f"  『本题考查』提取 {ep_n}/{len(all_q)} → 真题单元映射 {len(qunit)}/{len(all_q)}; 案例单元映射 {len(cunit)}/{sum(len(c['qs']) for c in all_cases)}; 有考频单元 {freq_n}")
    cards = {"version": 3, "units": units,
             "meta": {"qch": qch, "cch": cch, "qunit": qunit, "cunit": cunit,
                      "qtype": qtype, "qpoint": qpoint, "generated": datetime.date.today().isoformat()}}
    with open(os.path.join(OUT,"cards.js"), "w", encoding="utf-8") as f:
        f.write("/*自动生成*/\nwindow.CARDS=")
        f.write(json.dumps(cards, ensure_ascii=False, separators=(',',':'))); f.write(";\n")
    # 导出LLM预生成清单
    slim = [{"id":u["id"], "no":u["no"], "title":u["title"], "ch":u["ch"], "content":u["content"][:1800]}
            for u in units if u["chars"] >= 60]
    with open(os.path.join(ROOT,"scripts","units_for_llm.json"), "w", encoding="utf-8") as f:
        json.dump(slim, f, ensure_ascii=False, indent=1)
    log(f"  LLM预生成清单导出: {len(slim)} 单元")

    log("== 5/6 组装 ==")
    papers = {}
    def add_paper(year, half, subject, qid=None, cid=None):
        pid = f"P-{year}-{half}-{subject}"
        p = papers.setdefault(pid, {"id":pid,"year":year,"half":half,"subject":subject,
                                    "title":"","qids":[],"cids":[]})
        if qid: p["qids"].append(qid)
        if cid: p["cids"].append(cid)
    for q in all_q: add_paper(q["year"], q["half"], 1, qid=q["id"])
    for c in all_cases: add_paper(c["year"], c["half"], 2, cid=c["id"])
    for p in papers.values():
        h = "上半年" if p["half"]==1 else "下半年"
        p["title"] = f"{p['year']}{h} 科目{'一(上午)' if p['subject']==1 else '二(下午)'}"
        p["qids"].sort(); p["cids"].sort(key=lambda x:(len(x), x))
    papers_list = sorted(papers.values(), key=lambda p:(p["year"],p["half"],p["subject"]))

    # 知识树题目计数预填
    for q in all_q:
        pass  # 批次2 LLM标注后回填
    db = {"version":2, "generated": datetime.date.today().isoformat(),
          "papers": papers_list,
          "questions": {q["id"]: q for q in all_q},
          "groups": all_groups,
          "cases": {c["id"]: c for c in all_cases}}
    with open(os.path.join(OUT,"questions.js"), "w", encoding="utf-8") as f:
        f.write("/*自动生成 请勿手改*/\nwindow.DB=")
        f.write(json.dumps(db, ensure_ascii=False, separators=(',',':'))); f.write(";\n")
    with open(os.path.join(OUT,"syllabus.js"), "w", encoding="utf-8") as f:
        f.write("/*自动生成*/\nwindow.SYLLABUS=")
        f.write(json.dumps(syllabus, ensure_ascii=False, separators=(',',':'))); f.write(";\n")

    tpl = {"_说明":"导入缺失真题(如2023-2025上午)。填好在[设置→导入真题]选择此文件",
           "papers":[{"year":2023,"half":2,"subject":1,"title":"2023下半年 上午(导入)"}],
           "questions":[{"num":1,"stem":"题干","options":[{"key":"A","text":"A内容"},{"key":"B","text":"B内容"},{"key":"C","text":"C内容"},{"key":"D","text":"D内容"}],"answer":"B","analysis":"可选"}]}
    with open(os.path.join(OUT,"import_template.json"),"w",encoding="utf-8") as f:
        json.dump(tpl, f, ensure_ascii=False, indent=2)

    log("== 6/6 质检 ==")
    warn = 0
    for p in papers_list:
        if p["subject"] == 1:
            qs = [db["questions"][i] for i in p["qids"]]
            nums = {q["num"] for q in qs}
            miss = sorted(q["num"] for q in qs if not q["answer"])
            gap = sorted(set(range(1,76)) - nums)
            no4 = sorted(q["num"] for q in qs if len(q.get("options") or []) not in (0,4))
            noana = sorted(q["num"] for q in qs if not q["analysis"] and not q["group"])
            short = sorted(q["num"] for q in qs if len(q["stem"])<15 and not q["group"])
            if miss or gap or no4 or short: warn += 1
            log(f"[卷] {p['title']}: {len(qs)}题 缺答案{miss} 缺号{gap} 选项≠4:{no4} 缺解析:{noana[:12]} 短题干:{short[:8]}")
        else:
            for cid in p["cids"]:
                c = db["cases"][cid]
                noans = [s["no"] for s in c["qs"] if not s["answer"]]
                noq = [s["no"] for s in c["qs"] if not s["text"]]
                if noans or noq: warn += 1
                log(f"[案] {p['title']} {c['id']}({c.get('source','')[:12]}): 小题{len(c['qs'])} 缺答案{noans} 缺题干{noq} 缺失题{c.get('missing_subs',[])} [{c['answerStatus']}]")
    total_q = len(all_q); total_c = len(all_cases)
    log(f"\n=== 汇总: 选择题{total_q} 组题{len(all_groups)} 案例{total_c} 卷{len(papers_list)} 教程章{len(tb_manifest)} 图片(b64 {tb_stats['b64']}/cdn {tb_stats['cdn']}/fail {tb_stats['fail']}) 需人工复核项:{warn} ===")
    with open(os.path.join(ROOT,"资料","report_build.md"),"w",encoding="utf-8") as f:
        f.write("# 构建质检报告 " + datetime.date.today().isoformat() + "\n\n```\n" + "\n".join(REPORT) + "\n```\n")
    print("BUILD DONE")

if __name__ == "__main__":
    main()
