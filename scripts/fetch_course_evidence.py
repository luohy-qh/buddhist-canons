#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch source-grounded evidence (chunk + cards) from a packaged Skill.

多课程合并版：跨所有 source_courses/<dept>/ 查找 chunk / card，
用于在引用高影响结论前回核原文。强制 UTF-8 输出。
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

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


def iter_dept_dirs(references: Path):
    sc = references / "source_courses"
    if sc.is_dir():
        for d in sorted(sc.iterdir()):
            if d.is_dir():
                yield d.name, d
    else:
        yield "", references


def compact_chunk(chunk: dict[str, Any], *, context_chars: int) -> dict[str, Any]:
    text = str(chunk.get("text") or "")
    if context_chars > 0 and len(text) > context_chars:
        text = text[:context_chars].rstrip() + "..."
    return {
        "chunk_id": chunk.get("chunk_id"),
        "source_id": chunk.get("source_id"),
        "source_path": chunk.get("source_path"),
        "source_ref": chunk.get("source_ref"),
        "chunk_index": chunk.get("chunk_index"),
        "char_start": chunk.get("char_start"),
        "char_end": chunk.get("char_end"),
        "content_sha256": chunk.get("content_sha256"),
        "text": text,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="回核原文：抓取 chunk 及关联证据卡。")
    ap.add_argument("--references-dir", default="../references", help="references 目录（相对本脚本）。")
    ap.add_argument("--chunk-id", help="源 chunk id。")
    ap.add_argument("--card-id", help="证据卡 id。")
    ap.add_argument("--context-chars", type=int, default=4000, help="打印的最大源文本字数。")
    args = ap.parse_args()

    if not args.chunk_id and not args.card_id:
        raise SystemExit("请提供 --chunk-id 或 --card-id")

    base = (Path(__file__).resolve().parent / args.references_dir).resolve()

    target_chunk_id: Optional[str] = args.chunk_id
    matched_cards: list[dict] = []
    hit_dept = ""

    # 1) 先定位卡（跨部）
    if args.card_id:
        for dept, ddir in iter_dept_dirs(base):
            for card in read_jsonl(ddir / "text_distillation" / "evidence_cards.jsonl"):
                if card.get("card_id") == args.card_id:
                    matched_cards.append(card)
                    target_chunk_id = str(card.get("chunk_id") or target_chunk_id or "")
                    hit_dept = dept
                    break
            if matched_cards:
                break
        if not matched_cards:
            raise SystemExit(f"未找到卡: {args.card_id}")

    # 2) 定位 chunk（跨部），并收集该 chunk 的所有卡
    chunk = None
    for dept, ddir in iter_dept_dirs(base):
        if hit_dept and dept != hit_dept:
            continue
        for row in read_jsonl(ddir / "text_sources" / "chunks.jsonl"):
            if row.get("chunk_id") == target_chunk_id:
                chunk = row
                hit_dept = dept
                break
        if chunk:
            break

    if not chunk:
        raise SystemExit(f"未找到 chunk: {target_chunk_id}")

    if not args.card_id:
        ddir = base / "source_courses" / hit_dept if (base / "source_courses").is_dir() else base
        matched_cards = [c for c in read_jsonl(ddir / "text_distillation" / "evidence_cards.jsonl")
                         if c.get("chunk_id") == target_chunk_id]

    payload = {
        "dept": hit_dept,
        "chunk": compact_chunk(chunk, context_chars=args.context_chars),
        "cards": matched_cards,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
