# -*- coding: utf-8 -*-
"""补齐剩余薄单元: 用要点合成正文; 父单元聚合子单元要点; 重导 LLM 清单 + regen_ids"""
import json, io, os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARDS_F = os.path.join(ROOT, "data", "cards.js")
LLM_F = os.path.join(ROOT, "scripts", "units_for_llm.json")
REGEN_F = os.path.join(ROOT, "scripts", "regen_ids.json")


def load_var(path, var):
    raw = io.open(path, encoding="utf-8").read()
    return json.loads(raw[raw.index(var + "=") + len(var) + 1: raw.rindex(";")])


def dump_var(path, var, obj):
    with io.open(path, "w", encoding="utf-8") as f:
        f.write("/*自动生成*/\n" + var + "=")
        f.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":")))
        f.write(";\n")


cards = load_var(CARDS_F, "window.CARDS")
units = cards["units"]
changed = []


def compose_from_points(u):
    parts = [u.get("define") or ""]
    for p in u.get("points") or []:
        d = (p.get("d") or "").strip()
        if d:
            parts.append(f"{p.get('t','')}：{d}")
    return "\n".join(x for x in parts if x).strip()


for u in units:
    if len(u.get("content") or "") < 30 and (u.get("points") or []):
        c = compose_from_points(u)
        if len(c) >= 30:
            u["content"] = c[:2800]
            u["chars"] = len(u["content"])
            changed.append(u["id"])

kids_of = defaultdict(list)
for u in units:
    if u["id"].startswith("U") and "." in u["no"]:
        kids_of[u["no"].rsplit(".", 1)[0]].append(u)

for u in sorted(units, key=lambda x: -x["no"].count(".")):
    if not u["id"].startswith("U"):
        continue
    kids = [k for k in kids_of.get(u["no"], []) if k["no"].count(".") == u["no"].count(".") + 1]
    if not kids or u.get("points") or len(u.get("content") or "") >= 80:
        continue
    pts = []
    for k in kids:
        if k.get("points"):
            for p in k["points"]:
                pts.append({"t": f"{k['no']} {p.get('t','')}", "d": (p.get("d") or "")[:240]})
        elif k.get("define"):
            pts.append({"t": f"{k['no']} {k['title']}", "d": k["define"][:240]})
    if not pts:
        continue
    u["points"] = pts[:14]
    c = compose_from_points(u)
    u["content"] = c[:2800]
    u["chars"] = len(u["content"])
    changed.append(u["id"])

dump_var(CARDS_F, "window.CARDS", cards)

slim = [{"id": u["id"], "no": u["no"], "title": u["title"], "ch": u.get("ch"), "content": u["content"][:1800]}
        for u in units if len(u.get("content") or "") >= 30]
with io.open(LLM_F, "w", encoding="utf-8") as f:
    json.dump(slim, f, ensure_ascii=False, indent=1)
with io.open(REGEN_F, "w", encoding="utf-8") as f:
    json.dump(sorted(set(changed)), f, ensure_ascii=False)

print("补正文单元:", len(set(changed)), "| LLM清单:", len(slim))
bad = [u for u in units if not u.get("points") and len(u.get("content") or "") < 80]
print("剩余无要点且<80字:", len(bad), [u["id"] for u in bad])
