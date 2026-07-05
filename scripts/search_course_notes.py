#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Keyword search over packaged course evidence cards (multi-course aware).

给别人用友好版：
- 强制 UTF-8 输出（Windows 控制台不再乱码）
- 自动遍历合并 skill 的 source_courses/<dept>/ 或单课程布局
- 默认只返回高置信卡片（--confidence 调整）
- 明确区分【原文】(quote) 与【AI归纳】(其它卡型)
- 通过 citation_index.json 回填可追溯出处（经名+卷+朝代+译者，或经号+来源URL）
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# Windows 默认控制台可能是 GBK，主动切到 UTF-8，避免中文输出乱码。
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

CONF_ORDER = {"high": 3, "medium": 2, "low": 1}
QUOTE_TYPES = {"quote"}


def read_jsonl(path: Path):
    if not path.exists():
        return
    with path.open(encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                yield item


def find_card_files(references: Path):
    sc = references / "source_courses"
    if sc.is_dir():
        for d in sorted(sc.iterdir()):
            f = d / "text_distillation" / "evidence_cards.jsonl"
            if f.exists():
                yield d.name, f
    else:
        f = references / "text_distillation" / "evidence_cards.jsonl"
        if f.exists():
            yield "", f


def load_citation_index(references: Path) -> dict:
    p = references / "citation_index.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def card_haystack(card: dict) -> str:
    return " ".join(
        str(card.get(k) or "")
        for k in ("card_type", "title", "summary", "quote", "source_ref")
    ).lower()


def resolve_citation(card: dict, cidx: dict, dept: str) -> str:
    sid = card.get("source_id")
    info = cidx.get(sid) if sid else None
    if info:
        cite = info["citation"]
        if info.get("weak") and info.get("url"):
            cite += f" [来源: {info['url']}]"
    else:
        ref = card.get("source_ref") or card.get("source_path") or "?"
        cite = ref[:-4] if ref.lower().endswith(".txt") else ref
    ci = card.get("chunk_index")
    span = f" · 段#{ci}" if ci is not None else ""
    prefix = f"{dept} · " if dept else ""
    return f"{prefix}{cite}{span}"


def main() -> None:
    ap = argparse.ArgumentParser(description="搜索课程证据卡（多课程合并版）。")
    ap.add_argument("query", help="搜索关键词。")
    ap.add_argument("--references-dir", default="../references", help="references 目录（相对本脚本）。")
    ap.add_argument("--type", dest="card_type", help="按卡型过滤，如 method/concept/quote/diagnostic/rubric。")
    ap.add_argument("--dept", help="按部（source course）过滤，如 esoteric/agama。")
    ap.add_argument("--confidence", default="high", choices=["high", "medium", "low", "all"],
                    help="最低置信度，默认 high（给别人用更稳）。all=不过滤。")
    ap.add_argument("--limit", type=int, default=20, help="最多显示条数，默认 20。")
    args = ap.parse_args()

    base = (Path(__file__).resolve().parent / args.references_dir).resolve()
    cidx = load_citation_index(base)
    query = args.query.lower()
    min_conf = 0 if args.confidence == "all" else CONF_ORDER[args.confidence]

    hits = []
    for dept, f in find_card_files(base):
        if args.dept and dept != args.dept:
            continue
        for card in read_jsonl(f):
            if args.card_type and card.get("card_type") != args.card_type:
                continue
            conf = card.get("confidence", "")
            if min_conf and CONF_ORDER.get(conf, 0) < min_conf:
                continue
            if query in card_haystack(card):
                hits.append((dept, card))

    if not hits:
        print(f"未命中：'{args.query}'（置信≥{args.confidence}，卡型={args.card_type or '全部'}）")
        print("提示：放宽 --confidence all，或换关键词/去掉 --type。")
        return

    # quote 原文优先，其次按置信降序
    hits.sort(key=lambda dc: (
        0 if dc[1].get("card_type") in QUOTE_TYPES else 1,
        -CONF_ORDER.get(dc[1].get("confidence", ""), 0),
    ))

    total = len(hits)
    shown = hits[:args.limit]
    print(f"命中 {total} 条（显示前 {len(shown)}；置信≥{args.confidence}）\n")
    for dept, card in shown:
        ctype = card.get("card_type", "?")
        is_quote = ctype in QUOTE_TYPES
        tag = "【原文】" if is_quote else "【AI归纳】"
        conf = card.get("confidence", "?")
        title = card.get("title", "")
        body = (card.get("quote") if is_quote else card.get("summary")) or card.get("summary") or card.get("quote") or ""
        body = body.strip().replace("\n", " ")
        if len(body) > 200:
            body = body[:200] + "…"
        head = f"{tag} [{ctype}] 置信:{conf}"
        if title:
            head += f" — {title}"
        print(head)
        print(f"  {body}")
        print(f"  ⟨出处⟩ {resolve_citation(card, cidx, dept)}")
        print()

    if total > len(shown):
        print(f"… 还有 {total - len(shown)} 条，用 --limit 调大或 --dept/--type 收窄。")
    print("说明：【原文】为经文原句；【AI归纳】为蒸馏模型的概括/改写，引用时请回核原文（scripts/fetch_course_evidence.py --card-id <id>）。")


if __name__ == "__main__":
    main()
