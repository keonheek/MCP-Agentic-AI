#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import random
import os
from pathlib import Path
from collections import defaultdict

# Paths
BASE_PATH = "/c/Users/keonh/OneDrive/바탕 화면/MCP_Agentic AI/projects/study-materials"
SOURCE_1_3 = os.path.join(BASE_PATH, "경제학개론_MCQ_1-3장.md")
SOURCE_4_6 = os.path.join(BASE_PATH, "경제학개론_MCQ_4-6장.md")
SOURCE_7_9 = os.path.join(BASE_PATH, "경제학개론_MCQ_7-9장.md")
OUTPUT_DIR = os.path.join(BASE_PATH, "mock")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_markdown_questions(filepath):
    """
    Parse MCQ from markdown. Flexible parser that handles variations.
    Returns list of question dicts.
    """
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    questions = []

    # Pattern: 질문 N: ... through ... 정답: [X]  해설: ...
    # Split by 질문 markers
    pattern = r'질문\s+(\d+):(.*?)(?=질문\s+\d+:|$)'
    matches = re.finditer(pattern, content, re.DOTALL)

    # Extract chapter info as we go
    current_chapter = None
    current_difficulty = None

    for match in matches:
        q_num = int(match.group(1))
        q_block = match.group(2).strip()

        # Try to infer chapter from preceding text
        preceding = content[:match.start()]
        ch_match = re.search(r'##\s*(\d+)장', preceding)
        if ch_match:
            current_chapter = int(ch_match.group(1))

        # Try to infer difficulty
        diff_match = re.search(r'###\s*[\d-]+\.\s*(기본|응용|함정)', preceding[max(0, len(preceding)-500):])
        if diff_match:
            current_difficulty = diff_match.group(1)
        else:
            current_difficulty = "기본"  # default

        # Extract question text (first line after 질문 N:)
        lines = q_block.split('\n')
        question_text = lines[0].strip()

        # Find choices and answer
        choices = {}
        answer = None
        explanation = ""

        for line in lines[1:]:
            line = line.strip()

            # Match choice lines: A) ..., B) ..., etc.
            choice_match = re.match(r'^([A-D])\)\s*(.+)$', line)
            if choice_match:
                letter = choice_match.group(1)
                choice_text = choice_match.group(2)
                choices[letter] = choice_text

            # Match answer line: 정답: [A], 정답: A, etc.
            if '정답' in line:
                ans_match = re.search(r'정답:\s*\[?([A-D])\]?', line)
                if ans_match:
                    answer = ans_match.group(1)

            # Match explanation: 해설: ...
            if '해설' in line:
                expl_idx = lines.index(line)
                explanation = '\n'.join(lines[expl_idx:])
                explanation = re.sub(r'^해설:\s*', '', explanation)
                break

        # Validate and store
        if current_chapter and 'A' in choices and answer:
            questions.append({
                'chapter': current_chapter,
                'difficulty': current_difficulty,
                'text': question_text,
                'choices': {k: choices.get(k, '') for k in ['A', 'B', 'C', 'D']},
                'answer': answer,
                'explanation': explanation.strip(),
            })

    return questions

def load_all_questions():
    """Load from all 3 source files."""
    all_q = []

    for fpath, label in [(SOURCE_1_3, "1-3장"), (SOURCE_4_6, "4-6장"), (SOURCE_7_9, "7-9장")]:
        qs = parse_markdown_questions(fpath)
        all_q.extend(qs)
        print(f"Loaded {len(qs)} questions from {label}")

    print(f"\nTotal: {len(all_q)} questions")

    # Statistics
    by_ch = defaultdict(int)
    by_diff = defaultdict(int)
    for q in all_q:
        by_ch[q['chapter']] += 1
        by_diff[q['difficulty']] += 1

    print(f"By chapter: {dict(sorted(by_ch.items()))}")
    print(f"By difficulty: {dict(sorted(by_diff.items()))}")

    return all_q

def select_mock_exam(all_q, mock_num):
    """
    Select 25 questions with proper distribution and difficulty weighting.

    Distribution (always):
    - Ch1-3: 8 questions (3+3+2)
    - Ch4-6: 9 questions (3+3+3)
    - Ch7-9: 8 questions (3+3+2)

    Difficulty profile:
    - Mock 1: 70% 기본, 30% 응용, 0% 함정
    - Mock 2: 40% 기본, 40% 응용, 20% 함정
    - Mock 3: 20% 기본, 40% 응용, 40% 함정
    """
    # Set seed for reproducibility
    random.seed(mock_num * 2024)

    # Define what we want per chapter
    chapter_targets = {
        1: 3, 2: 3, 3: 2,
        4: 3, 5: 3, 6: 3,
        7: 3, 8: 3, 9: 2,
    }

    # Difficulty weights
    if mock_num == 1:
        weights = {'기본': 0.70, '응용': 0.30, '함정': 0.00}
    elif mock_num == 2:
        weights = {'기본': 0.40, '응용': 0.40, '함정': 0.20}
    else:  # 3
        weights = {'기본': 0.20, '응용': 0.40, '함정': 0.40}

    # Group questions by (chapter, difficulty)
    by_ch_diff = defaultdict(list)
    for q in all_q:
        by_ch_diff[(q['chapter'], q['difficulty'])].append(q)

    selected = []
    selected_indices = set()

    for chapter in sorted(chapter_targets.keys()):
        target_count = chapter_targets[chapter]
        chapter_selected = []

        # Try to select by difficulty weight
        for difficulty, weight in sorted(weights.items()):
            desired = int(target_count * weight + 0.5)  # round
            key = (chapter, difficulty)
            available = [q for i, q in enumerate(by_ch_diff[key])
                        if id(q) not in selected_indices]

            if desired > 0 and available:
                picked = random.sample(available, min(desired, len(available)))
                chapter_selected.extend(picked)
                for p in picked:
                    selected_indices.add(id(p))

        # If still short, fill with any remaining from this chapter
        if len(chapter_selected) < target_count:
            needed = target_count - len(chapter_selected)
            for difficulty in ['기본', '응용', '함정']:
                key = (chapter, difficulty)
                available = [q for q in by_ch_diff[key]
                           if id(q) not in selected_indices]
                if available:
                    picked = random.sample(available, min(needed, len(available)))
                    chapter_selected.extend(picked)
                    needed -= len(picked)
                    for p in picked:
                        selected_indices.add(id(p))
                if needed == 0:
                    break

        selected.extend(chapter_selected)

    # Shuffle to mix chapters
    random.shuffle(selected)

    return selected[:25]

def format_exam(questions, mock_num):
    """Format questions as markdown."""
    lines = [
        f"# 경제학 개론 모의고사 {mock_num}회 (25문제, 50분)",
        "",
        "목표 점수: 모의고사 1회 20/25, 2회 22/25, 3회 24/25",
        "",
    ]

    for i, q in enumerate(questions, 1):
        lines.append(f"질문 {i}: {q['text']}")
        lines.append(f"A) {q['choices']['A']}")
        lines.append(f"B) {q['choices']['B']}")
        lines.append(f"C) {q['choices']['C']}")
        lines.append(f"D) {q['choices']['D']}")
        lines.append(f"정답: {q['answer']}")
        lines.append(f"해설: {q['explanation']}")
        lines.append("")

    # Answer key
    lines.append("# 정답표")
    lines.append("")
    answers = [q['answer'] for q in questions]
    lines.append(f"1-5: {' '.join(answers[0:5])}")
    lines.append(f"6-10: {' '.join(answers[5:10])}")
    lines.append(f"11-15: {' '.join(answers[10:15])}")
    lines.append(f"16-20: {' '.join(answers[15:20])}")
    lines.append(f"21-25: {' '.join(answers[20:25])}")

    return "\n".join(lines)

def main():
    print("Parsing source files...")
    all_questions = load_all_questions()

    print("\nGenerating mock exams...")

    for mock_num in [1, 2, 3]:
        print(f"\nMock {mock_num}:")
        selected = select_mock_exam(all_questions, mock_num)

        # Stats
        ch_dist = defaultdict(int)
        diff_dist = defaultdict(int)
        for q in selected:
            ch_dist[q['chapter']] += 1
            diff_dist[q['difficulty']] += 1

        print(f"  Chapters: {dict(sorted(ch_dist.items()))}")
        print(f"  Difficulty: {dict(sorted(diff_dist.items()))}")

        # Format and save
        formatted = format_exam(selected, mock_num)
        output_path = os.path.join(OUTPUT_DIR, f"모의고사_{mock_num}회.md")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted)

        print(f"  Saved: {output_path}")

    print("\nDone!")

if __name__ == "__main__":
    main()
