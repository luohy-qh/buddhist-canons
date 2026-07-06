# -*- coding: utf-8 -*-
"""Thorough coverage audit: every chunk is classified and the source-of-truth gap is quantified.

Classification of every source chunk:
  1) REAL_EMPTY  : text>=200 chars AND has CJK AND 0 evidence cards
                   → these were almost certainly attempted by the LLM but produced 0 cards
                     (LLM JSON failure, content rejected, or skipped by the driver)
  2) TOO_SHORT   : text<200 chars
                   → driver likely skipped them; not a coverage loss unless the source itself is short
  3) NO_CJK      : no CJK characters in text
                   → driver likely skipped (mostly metadata headers)
  4) COVERED     : ≥1 evidence card references this chunk

Plus, from the cards side:
  5) ORPHAN_CARD : card references a chunk_id not present in any chunks.jsonl
                   → these are leftover from old runs / overwrites; safe to ignore

Per source_ref (经文) aggregation:
  - which 经文 has 100% 0 卡?

Output: a per-department table + a per-经文 table for REAL_EMPTY, plus a final
decision matrix for "should we re-distill or accept".
"""
from __future__ import annotations
import os, json, re, sys, glob
from collections import defaultdict, Counter

BASE = r"D:\minimax\课程蒸馏\.lineage\courses"
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

def load_chunks(path):
    out = {}
    if not os.path.exists(path): return out
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            if not ln.strip(): continue
            try: c = json.loads(ln)
            except: continue
            cid = c.get("chunk_id")
            if cid: out[cid] = c
    return out

def load_card_chunks(path):
    used = set()
    if not os.path.exists(path): return used
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            if not ln.strip(): continue
            try: c = json.loads(ln)
            except: continue
            cid = c.get("chunk_id")
            if cid: used.add(cid)
    return used


print("=" * 90)
print("  全面 chunk 覆盖率审计 — 把每个 chunk 分到 4 类, 再加孤儿卡检查")
print("=" * 90)

grand = Counter()
per_dept = {}
orphan_card_total = 0
all_chunks_by_id = {}  # for orphan check across depts
all_used_chunk_ids = set()
real_empty_by_ref = defaultdict(list)  # source_ref -> [(dept, chunk_id, len, snip)]

for d in sorted(os.listdir(BASE)):
    cp = os.path.join(BASE, d, "text_sources", "chunks.jsonl")
    ep = os.path.join(BASE, d, "text_distillation", "evidence_cards.jsonl")
    if not (os.path.exists(cp) and os.path.exists(ep)):
        continue
    chunks = load_chunks(cp)
    used = load_card_chunks(ep)
    real_empty, too_short, no_cjk, covered, total = 0, 0, 0, 0, 0
    for cid, c in chunks.items():
        total += 1
        txt = c.get("text") or ""
        has_cjk = bool(CJK.search(txt))
        if cid in used:
            covered += 1
        elif len(txt) < 200:
            too_short += 1
        elif not has_cjk:
            no_cjk += 1
        else:
            real_empty += 1
            ref = c.get("source_ref") or c.get("source_path") or "?"
            snip = (txt[:50] + "...").replace("\n", " ")
            real_empty_by_ref[(d, ref)].append((cid, len(txt), snip))
    orphan_local = 0
    for cid in used:
        if cid not in chunks:
            orphan_local += 1
    orphan_card_total += orphan_local
    per_dept[d] = dict(total=total, covered=covered, too_short=too_short,
                       no_cjk=no_cjk, real_empty=real_empty, orphan=orphan_local)
    grand["total"] += total
    grand["covered"] += covered
    grand["too_short"] += too_short
    grand["no_cjk"] += no_cjk
    grand["real_empty"] += real_empty
    grand["orphan"] += orphan_local

print(f"\n{'部':<22}{'总块数':>8}{'已覆盖':>9}{'REAL_EMPTY':>13}{'TOO_SHORT':>11}{'NO_CJK':>8}{'孤儿卡':>8}{'真覆盖率':>10}")
print("-" * 95)
for d, s in sorted(per_dept.items(), key=lambda x: -x[1]["real_empty"]):
    cn = CN.get(d, d)
    real_rate = (s["covered"] / s["total"] * 100) if s["total"] else 0
    print(f"{d}({cn})".ljust(22),
          f"{s['total']:>8}{s['covered']:>9}{s['real_empty']:>13}"
          f"{s['too_short']:>11}{s['no_cjk']:>8}{s['orphan']:>8}{real_rate:>9.2f}%")
print("-" * 95)
tr = grand["total"]
real_rate = (grand["covered"] / tr * 100) if tr else 0
print(f"{'全库合计':<22}{tr:>8}{grand['covered']:>9}{grand['real_empty']:>13}"
      f"{grand['too_short']:>11}{grand['no_cjk']:>8}{grand['orphan']:>8}{real_rate:>9.2f}%")
print(f"\n注: '真覆盖率' = covered/total, 包含所有 4 类(REAL_EMPTY+TOO_SHORT+NO_CJK+COVERED=total)")
print(f"    'REAL_EMPTY' 是 LLM 应该抽但没抽出的真损失; 'TOO_SHORT'/'NO_CJK' 是设计上过滤掉的。")
print(f"    '孤儿卡' 是 evidence_cards 引用了已不存在的 chunk_id(可忽略)。")

# 按经文聚合 REAL_EMPTY (找整经文 0 卡的)
print(f"\n{'='*90}")
print(f"  按经文聚合: REAL_EMPTY chunks 分布(前 30 个经文,按 REAL_EMPTY 数排序)")
print(f"{'='*90}")
agg = []
for (d, ref), items in real_empty_by_ref.items():
    agg.append((d, ref, len(items), sum(t[1] for t in items)))
agg.sort(key=lambda x: -x[2])
print(f"{'部':<8}{'经文 (source_ref)':<35}{'REAL_EMPTY':>11}{'总字符':>10}")
print("-" * 70)
for d, ref, n, total_chars in agg[:30]:
    print(f"{d[:8]:<8}{ref[:34]:<35}{n:>11}{total_chars:>10}")
if len(agg) > 30:
    print(f"  ... 还有 {len(agg)-30} 部经文涉及 REAL_EMPTY")

# 整经文 0 卡
full_zero = [(d, ref, n) for (d, ref), n in [(k, len(v)) for k, v in real_empty_by_ref.items()] if n > 0]
# 真要看"整经文 0 卡" = 该经文的所有 chunk 都是 REAL_EMPTY
print(f"\n{'='*90}")
print(f"  整经文 0 卡 (该经文下所有 chunk 都没抽出卡) — 共 {len([(d,r) for (d,r) in real_empty_by_ref if len(real_empty_by_ref[(d,r)]) > 0])} 部候选")
print(f"{'='*90}")
# 计算: 找 source_ref 全部 chunk 都在 REAL_EMPTY 里的
source_ref_to_dept = defaultdict(set)
source_ref_chunks = defaultdict(list)  # (dept, ref) -> [chunk_ids]
for d in sorted(os.listdir(BASE)):
    cp = os.path.join(BASE, d, "text_sources", "chunks.jsonl")
    ep = os.path.join(BASE, d, "text_distillation", "evidence_cards.jsonl")
    if not (os.path.exists(cp) and os.path.exists(ep)):
        continue
    chunks = load_chunks(cp)
    used = load_card_chunks(ep)
    by_ref = defaultdict(list)
    for cid, c in chunks.items():
        ref = c.get("source_ref") or c.get("source_path") or "?"
        by_ref[ref].append((cid, c, cid in used, len(c.get("text") or ""), bool(CJK.search(c.get("text") or ""))))
    for ref, lst in by_ref.items():
        n = len(lst)
        cov = sum(1 for x in lst if x[2])
        if n >= 1 and cov == 0:
            tot_chars = sum(x[3] for x in lst)
            print(f"  {d[:18]:<20} {ref[:36]:<38} {n:>3} 块  共 {tot_chars:>6} 字")

# 决策建议
print(f"\n{'='*90}")
print(f"  决策建议")
print(f"{'='*90}")
re = grand["real_empty"]
if re == 0:
    print("  0 个 REAL_EMPTY, 完美覆盖, 不需要重蒸馏。")
elif re <= 5:
    print(f"  仅 {re} 个 REAL_EMPTY, 重蒸馏 ROI 太低, 接受现状即可。")
else:
    print(f"  REAL_EMPTY = {re} 个 chunk, 分布在 {len(real_empty_by_ref)} 部经文。")
    full_zero_count = sum(1 for d in per_dept if per_dept[d]["real_empty"] > 0 and per_dept[d]["covered"] == 0)
    if full_zero_count > 0:
        print(f"  其中 {full_zero_count} 个部完全没有 coverage, 建议重蒸馏这几个部(切小 chunk 或换模型)。")
    else:
        print(f"  没有「全 0 部」, REAL_EMPTY 是离散的, 可考虑: 1) 接受 2) 用更小 chunk 重切并重蒸馏这些 chunk。")
