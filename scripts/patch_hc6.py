# -*- coding: utf-8 -*-
"""手工修正 HC-6 DES 初始置换 IP"""
import json, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HB_F = os.path.join(ROOT, "data", "handbook.js")
hb = json.loads(io.open(HB_F, encoding="utf-8").read().split("=", 1)[1].rstrip().rstrip(";"))

html = ("<pre>步骤：\n"
        "1. DES 初始置换按 IP 表执行：输入 64 位明文，按表中编号逐位搬运（第 58 位→输出第 1 位、第 50 位→第 2 位……）。\n"
        "2. IP 表共 8 行 × 8 列 = 64 个位置，从左到右、从上到下依次对应输出第 1~64 位。\n"
        "3. 置换只改变比特位置，不改变比特值。</pre>"
        "<p><b>例题：</b>明文 M=0123456789ABCDEF（十六进制）转二进制：0000 0001 0010 0011 0100 0101 0110 0111 "
        "1000 1001 1010 1011 1100 1101 1110 1111；按 IP 表置换后："
        "1100 1100 0000 0000 1100 1100 1111 1111 1111 0000 1010 1010 1111 0000 1010 1010 = <b>CC00CCFF F0AAF0AA</b>。</p>"
        '<p class="muted">易错点：位编号从 1 开始；输入输出均为 64 位；逐位对照 IP 表，不要按字节整体搬移。</p>')

for c in hb["calcs"]:
    if c["id"] == "HC-6":
        c["title"] = "DES 初始置换 IP"
        c["html"] = html
        print("HC-6 已修正:", len(html))

io.open(HB_F, "w", encoding="utf-8").write("/*自动生成 请勿手改*/\nwindow.HANDBOOK=" +
    json.dumps(hb, ensure_ascii=False, separators=(",", ":")) + ";\n")
print("done")
