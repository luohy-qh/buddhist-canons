# -*- coding: utf-8 -*-
"""Find 'empty chunks': source chunks that contain text but produced 0 evidence cards.

A chunk is considered 'empty' (skipped) when:
  - chunk_text has CJK content AND length >= 200 chars
  - but no evidence_card references this chunk_id

Reports per-department counts + lists chunk_ids so user can decide
re-distillation scope.
"""
from __future__ import annotations
import os, json, ctypes, re, sys
ctypes.windll.kernel32.SetConsoleOutputCP(65001)
sys.stdout.reconfigure(encoding="utf-8")

CJK = re.compile(r"[\u4e00-\u9fff]")

CN = {
 "agama":"阿含","avadana":"本缘","prajnaparamita":"般若","lotus-avatamsaka":"法华·华严",
 "ratnakuta-nirvana":"宝积·涅槃","mahavaipulya":"大集","sutra-collection":"经集",
 "esoteric":"密教","dharani":"陀罗尼","vinaya":"律",
 "vinaya-commentary-treatise-commentary":"律疏·论疏","sutra-commentary":"释经论",
 "abhidharma":"毗昙","madhyamaka-yoga":"中观·瑜伽","treatise-collection":"论集",
 "schools":"经疏(诸宗)","history":"史传","misc-nonbuddhist-catalogue":"事汇·外教·目录",
 "apocrypha":"古逸·疑似",
}

BASE = r".lineage/courses"
print(f"{'部':<38}{'块数':>6}{'有卡':>7}{'被跳过':>9}{'跳过率':>8}")
print("-"*72)
tot_chunks = tot_used = tot_empty = 0
empty_by_dept = {}
for d in sorted(os.listdir(BASE)):
    cp = os.path.join(BASE, d, "text_sources", "chunks.jsonl")
    ep = os.path.join(BASE, d, "text_distillation", "evidence_cards.jsonl")
    if not (os.path.exists(cp) and os.path.exists(ep)):
        continue
    chunks = {}
    with open(cp, encoding="utf-8", errors="replace") as f:
        for ln in f:
            if not ln.strip(): continue
            try: c = json.loads(ln)
            except: continue
            cid = c.get("chunk_id")
            if cid: chunks[cid] = c
    used = set()
    with open(ep, encoding="utf-8", errors="replace") as f:
        for ln in f:
            if not ln.strip(): continue
            try: c = json.loads(ln)
            except: continue
            cid = c.get("chunk_id")
            if cid: used.add(cid)
    empties = []
    for cid, c in chunks.items():
        if cid in used: continue
        txt = c.get("text") or ""
        if len(txt) < 200: continue          # 太短跳过（可能是元数据/空 chunk）
        if not CJK.search(txt): continue     # 无中文跳过（很少见）
        empties.append((cid, len(txt), (txt[:50] + "...").replace("\n"," ")))
    n = len(chunks); u = len(used); e = len(empties)
    rate = (e / n * 100) if n else 0
    cn = CN.get(d, d)
    print(f"{d} ({cn})".ljust(38), f"{n:>6}{u:>7}{e:>9}{rate:>7.1f}%")
    tot_chunks += n; tot_used += u; tot_empty += e
    empty_by_dept[d] = (n, u, e, empties)
print("-"*72)
total_rate = (tot_empty/tot_chunks*100) if tot_chunks else 0
print(f"{'全库合计':<38}{tot_chunks:>6}{tot_used:>7}{tot_empty:>9}{total_rate:>7.2f}%")

# 详细：列出每个被跳过的 chunk_id（前5字符+长度+开头）
print(f"\n=== 被跳过 chunk 明细（前 60 条）===")
shown = 0
for d, (n, u, e, empties) in empty_by_dept.items():
    if not empties: continue
    print(f"\n--- {d} ({CN.get(d,d)}) {e} 条 ---")
    for cid, ln, snip in empties[:20]:
        print(f"  {cid[:10]}  {ln:>6}ch  {snip}")
        shown += 1
        if shown >= 60: break
    if shown >= 60: break