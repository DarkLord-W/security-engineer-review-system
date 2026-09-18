# -*- coding: utf-8 -*-
import re, types, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
src = open('scripts/build_data.py', encoding='utf-8-sig').read()
src = src.replace('if __name__ == "__main__":\n    main()', '')
mod = types.ModuleType('bd'); mod.__dict__['__file__'] = 'scripts/build_data.py'
exec(compile(src, 'bd', 'exec'), mod.__dict__)
chapters = mod.parse_analysis_md('资料/MinerU_markdown_信息安全工程师2018至2022试题分析与解答_(清华大学出版社)_(z-library.sk,_1lib.sk,_z-lib.sk)_2093262293397954560.md')
NOANS = {(2018,1,1):[3], (2019,1,1):[2,23,33,48], (2020,2,1):[2,40,45],
         (2021,2,1):[27,34,47,55,57], (2022,2,1):[10,18,19,20,25,26,53,56,58,59]}
for num, year, half, subj, block in chapters:
    key = (year, half, subj)
    if key not in NOANS or subj != 1: continue
    ptext = mod.apply_marker_patches(mod.preprocess(block), year, half, subj)
    marks = [(m.start(), int(m.group(1))) for m in re.finditer(r'^#{0,2}\s*试题\s*[（(](\d+)[）)](?:\s*～\s*[（(](\d+)[）)])?\s*$', ptext, re.M)]
    posmap = dict((n, p) for p, n in marks)
    ordered = sorted(posmap.items())
    for n in NOANS[key]:
        me = posmap.get(n)
        if me is None: print(f'--- {key} #{n}: MARKER MISSING'); continue
        nxt = next((p for m, p in ordered if m > me), len(ptext))
        seg = ptext[me:nxt]
        # 找"参考答案"及其后80字符
        m = re.search(r'.{10}参考答案.{80}', seg, re.S)
        print(f'--- {year}-{half} #{n}: ' + (repr(m.group(0))[:180] if m else 'NO 参考答案 IN BLOCK'))
