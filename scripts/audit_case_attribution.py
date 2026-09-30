# -*- coding: utf-8 -*-
"""案例归属核对：用《试题分析与解答》(清华版) 的章节区间校验题库案例年份/题号。
输出 资料/case_attribution_audit.md
"""
import io, os, re, glob, json

ROOT = r'D:\A_Work\软考\复习系统'
BOOK = glob.glob(os.path.join(ROOT, '资料', '*试题分析与解答*.md'))
OUT = os.path.join(ROOT, '资料', 'case_attribution_audit.md')
QJS = os.path.join(ROOT, 'data', 'questions.js')

def load(p):
    return io.open(p, encoding='utf-8').read()

def chapters(t):
    """章节：第N章 YYYY[上|下]半年 …；先按标题行判定上午/下午，未标注的按同年成对顺序推断。"""
    out = []
    for m in re.finditer(r'#{1,3}\s*第(\d+)章\s*(\d{4})(上|下)半年[^\n]{0,60}', t):
        line = m.group(0)
        period = '上午' if '上午' in line else ('下午' if '下午' in line else '?')
        out.append({'pos': m.start(), 'no': int(m.group(1)), 'year': int(m.group(2)), 'half': 1 if m.group(3) == '上' else 2, 'period': period})
    out.sort(key=lambda x: x['pos'])
    # 同年同半年的章节成对时：前者上午、后者下午
    groups = {}
    for c in out:
        groups.setdefault((c['year'], c['half']), []).append(c)
    for key, arr in groups.items():
        if len(arr) >= 2:
            arr[0]['period'] = '上午'; arr[1]['period'] = '下午'
    return out

def chapter_span(ch, year, half, period):
    """返回某年某半年某场次的字节区间 [start, end)"""
    arr = [c for c in ch if c['year'] == year and c['half'] == half and c['period'] == period]
    if not arr:
        return None
    c = arr[0]
    nxt = [x for x in ch if x['pos'] > c['pos']]
    end = nxt[0]['pos'] if nxt else len(open(QJS, encoding='utf-8').read())
    return (c['pos'], end)

def strip_html(s):
    s = re.sub(r'<[^>]+>', ' ', s or '')
    s = s.replace('\\n', ' ').replace('\\"', '"').replace('\\/', '/')
    s = re.sub(r'\s+', '', s)
    return s

def cases(qt):
    out = []
    for m in re.finditer(r'"id":"(C-\d{4}-\d-\d)","year":(\d{4}),"half":(\d),".*?"cn":"([^"]{1,4})"', qt):
        sid = m.group(1)
        seg = qt[m.start(): m.start() + 60000]
        probe = ''
        for sm in re.finditer(r'"no":\d+,"text":"((?:[^"\\]|\\.){0,3000}?)"', seg):
            cand = strip_html(sm.group(1))
            cand = re.sub(r'[A-Za-z0-9+/=]{40,}', '', cand)          # 去除 base64 残块
            cand = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9（）()？?。（）。]', '', cand)
            if len(cand) >= 16:
                probe = cand; break
        out.append({'id': sid, 'year': int(m.group(2)), 'half': int(m.group(3)), 'cn': m.group(4), 'probe': probe})
    return out

def find_in_book(t, probe):
    for n in (32, 26, 20, 14):
        s = probe[:n]
        if len(s) < 6:
            break
        i = t.find(s)
        if i >= 0:
            return i, n
    return -1, 0

def main():
    if not BOOK:
        print('未找到解析书'); return
    t = load(BOOK[0]); ch = chapters(t); qt = load(QJS); cs = cases(qt)
    rows = []
    for c in cs:
        span = chapter_span(ch, c['year'], c['half'], '下午')
        if not span:
            rows.append((c, None, '➖ 不在解析书范围（据其他真题整理版）', ''))
            continue
        if not c['probe']:
            rows.append((c, None, '❔ 无特征串（需人工）', ''))
            continue
        # 只在该案例“自己标注年份的下午章区间”内查找
        if c['probe'][:26] and c['probe'][:26] in t[span[0]:span[1]]:
            rows.append((c, None, '✅ 一致（在该年下午章内命中）', '前26字'))
            continue
        hit = next((n for n in (20, 16, 12) if c['probe'][:n] and c['probe'][:n] in t[span[0]:span[1]]), 0)
        if hit:
            rows.append((c, None, '✅ 一致（在该年下午章内命中）', '前%d字' % hit))
        else:
            rows.append((c, None, '❔ 该书该年下午章未命中（文本差异，需人工）', ''))
    # 统计
    tot = len(rows); okn = sum(1 for r in rows if r[2].startswith('✅'))
    warn = [r for r in rows if r[2].startswith('⚠')]
    unk = [r for r in rows if r[2].startswith('❔')]
    L = ['# 案例归属核对报告（对照清华版《2018-2022 试题分析与解答》）', '',
         '- 生成时间：自动生成', '- 核对方法：以解析书章节（同年"上午章 → 下午章"成对）为年份界标；用每案例首问文本在书中定位，取落在其前的最近章节判断归属',
         '- 样本：题库案例 %d 个；**一致 %d**；疑错标 %d；未定位 %d' % (tot, okn, len(warn), len(unk)), '',
         '| 案例ID | 题库标注 | 书中所在章 | 结论 | 备注 |', '|---|---|---|---|---|']
    for c, prev, verdict, note in rows:
        label = '%d%s 第%s题' % (c['year'], '上' if c['half'] == 1 else '下', c['cn'])
        where = ('第%d章 %d%s半年·%s' % (prev['no'], prev['year'], '上' if prev['half'] == 1 else '下', prev['period'])) if prev else '—'
        L.append('| %s | %s | %s | %s | %s |' % (c['id'], label, where, verdict, note))
    if warn:
        L += ['', '## 疑错标清单（需人工确认）', '']
        for c, prev, verdict, note in warn:
            L.append('- **%s**（题库标注 %d%s 第%s题）→ 书中落在 %d%s半年·%s：%s' % (c['id'], c['year'], '上' if c['half']==1 else '下', c['cn'], prev['year'], '上' if prev['half']==1 else '下', prev['period'], verdict))
    if unk:
        L += ['', '## 未定位（书中可能未收录或文本差异较大）', '']
        for c, prev, verdict, note in unk:
            L.append('- %s（%d%s 第%s题）：%s' % (c['id'], c['year'], '上' if c['half']==1 else '下', c['cn'], verdict))
    io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    print('案例总数 %d | 一致 %d | 疑错标 %d | 未定位 %d' % (tot, okn, len(warn), len(unk)))
    for c, prev, verdict, note in warn[:12]:
        print('  ⚠', c['id'], c['year'], c['half'], c['cn'], '→', (prev and (prev['year'], prev['half'], prev['period'])))
    for c, prev, verdict, note in unk[:12]:
        print('  ❔', c['id'], c['year'], c['half'], c['cn'], verdict)

main()
