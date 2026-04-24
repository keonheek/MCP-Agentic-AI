#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master script: Verify source files, parse, and generate 3 mock exams.
Run this to create all mock exams.

Usage:
    python verify_and_generate.py
"""

import re
import random
import os
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

# Absolute paths
BASE = Path(r"C:\Users\keonh\OneDrive\바탕 화면\MCP_Agentic AI\projects\study-materials")
SOURCES = {
    "1-3": BASE / "경제학개론_MCQ_1-3장.md",
    "4-6": BASE / "경제학개론_MCQ_4-6장.md",
    "7-9": BASE / "경제학개론_MCQ_7-9장.md",
}
OUTPUT_DIR = BASE / "mock"

OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

def verify_files():
    """Check if all source files exist."""
    print("Verifying source files...")
    for label, path in SOURCES.items():
        if path.exists():
            size = path.stat().st_size
            print(f"  ✓ Ch{label}: {path.name} ({size} bytes)")
        else:
            print(f"  ✗ Ch{label}: NOT FOUND - {path}")
            return False
    return True

def parse_questions(filepath: Path) -> List[Dict]:
    """Parse MCQ from markdown file."""
    if not filepath.exists():
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    questions = []
    current_ch = None
    current_diff = "기본"

    # Track chapter and difficulty headers
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if re.match(r'^##\s*(\d+)장', line):
            current_ch = int(re.search(r'(\d+)', line).group(1))
        if re.search(r'(기본|응용|함정)', line) and '###' in line:
            match = re.search(r'(기본|응용|함정)', line)
            if match:
                current_diff = match.group(1)

    # Parse questions: 질문 N: ... (until next question)
    pattern = r'질문\s+(\d+):(.*?)(?=질문\s+\d+:|$)'
    for match in re.finditer(pattern, content, re.DOTALL):
        before_pos = match.start()
        preceding = content[:before_pos]

        # Find chapter just before this question
        ch_matches = re.findall(r'##\s*(\d+)장', preceding)
        if ch_matches:
            current_ch = int(ch_matches[-1])

        # Find difficulty just before this question
        diff_matches = re.findall(r'###\s*[\d-]+\.\s*(기본|응용|함트)', preceding)
        if diff_matches:
            current_diff = diff_matches[-1]
        else:
            # Also try without the exact format
            diff_matches = re.findall(r'(기본|응용|함정)', preceding[-200:])
            if diff_matches:
                current_diff = diff_matches[-1]

        q_block = match.group(2).strip()
        q_lines = q_block.split('\n')

        # Question text
        q_text = q_lines[0].strip() if q_lines else ""
        if not q_text:
            continue

        # Choices A-D
        choices = {}
        answer = None
        explanation = ""

        for line in q_lines[1:]:
            line = line.strip()

            # Match A) B) C) D)
            if re.match(r'^[A-D]\)\s*', line):
                letter = line[0]
                text = re.sub(r'^[A-D]\)\s*', '', line)
                choices[letter] = text

            # Match answer
            if '정답' in line:
                ans_m = re.search(r'정답:\s*\[?([A-D])\]?', line)
                if ans_m:
                    answer = ans_m.group(1)

            # Match explanation
            if '해설' in line:
                idx = q_lines.index(line)
                expl = '\n'.join(q_lines[idx:])
                explanation = re.sub(r'^해설:\s*', '', expl, flags=re.IGNORECASE).strip()
                break

        # Validate
        if current_ch and len(choices) >= 4 and answer and answer in choices:
            questions.append({
                'ch': current_ch,
                'diff': current_diff,
                'text': q_text,
                'choices': {k: choices.get(k, '') for k in 'ABCD'},
                'ans': answer,
                'expl': explanation,
            })

    return questions

def load_all_questions() -> Tuple[List, Dict]:
    """Load and organize all questions."""
    all_qs = []
    for label, path in SOURCES.items():
        qs = parse_questions(path)
        all_qs.extend(qs)
        print(f"  Loaded {len(qs)} from Ch{label}")

    print(f"\nTotal: {len(all_qs)} questions\n")

    # Group by (chapter, difficulty)
    by_cd = defaultdict(list)
    for q in all_qs:
        key = (q['ch'], q['diff'])
        by_cd[key].append(q)

    # Stats
    print("📊 Distribution:")
    for ch in range(1, 10):
        cnt = sum(len(by_cd[(ch, d)]) for d in ['기본', '응용', '함정'])
        if cnt > 0:
            print(f"  Ch{ch}: {cnt} qs", end="")
            for d in ['기본', '응용', '함정']:
                c = len(by_cd[(ch, d)])
                if c > 0:
                    print(f" ({d}:{c})", end="")
            print()

    return all_qs, by_cd

def select_exam(all_qs, by_cd, mock_num):
    """Select 25 questions for one mock exam."""
    random.seed(mock_num * 42)

    targets = {1:3, 2:3, 3:2, 4:3, 5:3, 6:3, 7:3, 8:3, 9:2}
    weights = {
        1: {'기본': 0.70, '응용': 0.30, '함정': 0.0},
        2: {'기본': 0.40, '응용': 0.40, '함정': 0.20},
        3: {'기본': 0.20, '응용': 0.40, '함정': 0.40},
    }[mock_num]

    selected = []
    used_ids = set()

    for ch in sorted(targets.keys()):
        tgt = targets[ch]
        ch_qs = []

        # By difficulty weight
        for diff, w in sorted(weights.items()):
            need = int(tgt * w + 0.5)
            key = (ch, diff)
            avail = [q for q in by_cd[key] if id(q) not in used_ids]

            if need > 0 and avail:
                pick = random.sample(avail, min(need, len(avail)))
                ch_qs.extend(pick)
                for p in pick:
                    used_ids.add(id(p))

        # Fill gaps
        while len(ch_qs) < tgt:
            for diff in ['기본', '응용', '함정']:
                key = (ch, diff)
                avail = [q for q in by_cd[key] if id(q) not in used_ids]
                if avail:
                    pick = random.sample(avail, min(1, len(avail)))
                    ch_qs.extend(pick)
                    for p in pick:
                        used_ids.add(id(p))
                if len(ch_qs) >= tgt:
                    break

        selected.extend(ch_qs)

    random.shuffle(selected)
    return selected[:25]

def format_exam(qs, num):
    """Format as markdown."""
    lines = [
        f"# 경제학 개론 모의고사 {num}회 (25문제, 50분)",
        "",
        "목표 점수: 모의고사 1회 20/25, 2회 22/25, 3회 24/25",
        "",
    ]

    for i, q in enumerate(qs, 1):
        lines.append(f"질문 {i}: {q['text']}")
        lines.append(f"A) {q['choices']['A']}")
        lines.append(f"B) {q['choices']['B']}")
        lines.append(f"C) {q['choices']['C']}")
        lines.append(f"D) {q['choices']['D']}")
        lines.append(f"정답: {q['ans']}")
        lines.append(f"해설: {q['expl']}")
        lines.append("")

    # Answer key
    lines.append("# 정답표")
    lines.append("")
    ans = [q['ans'] for q in qs]
    lines.append(f"1-5: {' '.join(ans[0:5])}")
    lines.append(f"6-10: {' '.join(ans[5:10])}")
    lines.append(f"11-15: {' '.join(ans[10:15])}")
    lines.append(f"16-20: {' '.join(ans[15:20])}")
    lines.append(f"21-25: {' '.join(ans[20:25])}")

    return "\n".join(lines)

def main():
    print("\n" + "="*70)
    print("경제학 개론 모의고사 생성기")
    print("="*70 + "\n")

    if not verify_files():
        print("\n❌ Source files missing. Check paths and try again.")
        return False

    print("\n📖 Parsing source files...")
    all_qs, by_cd = load_all_questions()

    print("\n🎯 Generating 3 mock exams...\n")
    for mock_num in [1, 2, 3]:
        exam = select_exam(all_qs, by_cd, mock_num)

        # Stats
        ch_dist = defaultdict(int)
        diff_dist = defaultdict(int)
        for q in exam:
            ch_dist[q['ch']] += 1
            diff_dist[q['diff']] += 1

        print(f"Mock {mock_num}:")
        print(f"  Ch: {dict(sorted(ch_dist.items()))}")
        print(f"  Diff: {dict(sorted(diff_dist.items()))}")

        # Save
        md = format_exam(exam, mock_num)
        out = OUTPUT_DIR / f"모의고사_{mock_num}회.md"
        with open(out, 'w', encoding='utf-8') as f:
            f.write(md)
        print(f"  → {out.name}\n")

    print("="*70)
    print("✅ Done! All 3 mock exams generated.")
    print("="*70)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
