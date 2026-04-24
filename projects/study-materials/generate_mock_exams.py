#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import random
from pathlib import Path

# File paths
BASE = Path("/c/Users/keonh/OneDrive/바탕 화면/MCP_Agentic AI/projects/study-materials")
SOURCE_FILES = [
    BASE / "경제학개론_MCQ_1-3장.md",
    BASE / "경제학개론_MCQ_4-6장.md",
    BASE / "경제학개론_MCQ_7-9장.md",
]
OUTPUT_DIR = BASE / "mock"
OUTPUT_DIR.mkdir(exist_ok=True)

def parse_questions_from_file(filepath):
    """Parse MCQ questions from markdown file.

    Expected format:
    ## 1장
    ### 1-1. 기본
    질문 1: ...
    A) ...
    B) ...
    C) ...
    D) ...
    정답: [A]
    해설: ...

    Returns list of dicts: {
        'chapter': int,
        'difficulty': str ('기본', '응용', '함정'),
        'question_num': int,
        'text': str,
        'choices': {'A': str, 'B': str, 'C': str, 'D': str},
        'answer': str,
        'explanation': str,
    }
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    questions = []
    current_chapter = None
    current_difficulty = None

    # Split by question pattern
    pattern = r'질문 (\d+):\s*(.+?)(?=질문 \d+:|$)'
    matches = list(re.finditer(pattern, content, re.DOTALL))

    for match in matches:
        q_num = int(match.group(1))
        q_text_and_rest = match.group(2).strip()

        # Extract question text (first line)
        lines = q_text_and_rest.split('\n')
        question_text = lines[0].strip()
        rest = '\n'.join(lines[1:])

        # Extract choices
        choice_pattern = r'([A-D])\)\s*(.+?)(?=[A-D]\)|정답:|$)'
        choice_matches = list(re.finditer(choice_pattern, rest, re.DOTALL))

        choices = {}
        for cm in choice_matches:
            letter = cm.group(1)
            choice_text = cm.group(2).strip().split('\n')[0]  # First line only
            choices[letter] = choice_text

        # Extract answer
        answer_match = re.search(r'정답:\s*\[([A-D])\]', rest)
        answer = answer_match.group(1) if answer_match else None

        # Extract explanation
        expl_match = re.search(r'해설:\s*(.+?)(?=질문 \d+:|$)', rest, re.DOTALL)
        explanation = expl_match.group(1).strip() if expl_match else ""

        # Determine chapter and difficulty from context
        # Try to find chapter from earlier content
        chapter_search = re.search(r'##\s*(\d+)장', content[:match.start()])
        chapter = int(chapter_search.group(1)) if chapter_search else None

        # Try to find difficulty
        difficulty_search = re.search(r'###\s*\d+-\d+\.\s*(기본|응용|함정)', content[:match.start()])
        difficulty = difficulty_search.group(1) if difficulty_search else "기본"

        if chapter and choices.get('A') and answer:
            questions.append({
                'chapter': chapter,
                'difficulty': difficulty,
                'question_num': q_num,
                'text': question_text,
                'choices': choices,
                'answer': answer,
                'explanation': explanation,
                'file_source': filepath.name,
            })

    return questions

def load_all_questions():
    """Load all questions from all source files."""
    all_questions = []
    for filepath in SOURCE_FILES:
        if filepath.exists():
            questions = parse_questions_from_file(filepath)
            all_questions.extend(questions)
            print(f"Loaded {len(questions)} questions from {filepath.name}")
        else:
            print(f"Warning: File not found: {filepath}")

    # Group by chapter and difficulty
    by_chapter_difficulty = {}
    for q in all_questions:
        key = (q['chapter'], q['difficulty'])
        if key not in by_chapter_difficulty:
            by_chapter_difficulty[key] = []
        by_chapter_difficulty[key].append(q)

    print(f"\nTotal questions loaded: {len(all_questions)}")
    print(f"By chapter and difficulty: {[(k, len(v)) for k, v in sorted(by_chapter_difficulty.items())]}")

    return all_questions, by_chapter_difficulty

def select_mock_exam_questions(all_questions, by_chapter_difficulty, mock_num):
    """
    Select 25 questions for a mock exam.

    Distribution per mock:
    - Ch1-3: 8 questions (3+3+2)
    - Ch4-6: 9 questions (3+3+3)
    - Ch7-9: 8 questions (3+3+2)

    Mock 1: mostly 기본 + some 응용 (warm-up)
    Mock 2: mixed 기본/응용/함정 (realistic)
    Mock 3: mostly 응용 + 함정 (hardest)
    """
    selected = []
    random.seed(mock_num * 42)  # Deterministic per mock

    chapter_distributions = {
        1: (1, 3),  # Ch1: 3 questions
        2: (2, 3),  # Ch2: 3 questions
        3: (3, 2),  # Ch3: 2 questions
        4: (4, 3),
        5: (5, 3),
        6: (6, 3),
        7: (7, 3),
        8: (8, 3),
        9: (9, 2),
    }

    # Define difficulty weighting per mock
    if mock_num == 1:
        # Warm-up: 70% 기본, 30% 응용
        weights = {'기본': 0.7, '응용': 0.3, '함정': 0.0}
    elif mock_num == 2:
        # Realistic: 40% 기본, 40% 응용, 20% 함정
        weights = {'기본': 0.4, '응용': 0.4, '함정': 0.2}
    else:  # mock_num == 3
        # Hard: 20% 기본, 40% 응용, 40% 함정
        weights = {'기본': 0.2, '응용': 0.4, '함정': 0.4}

    for chapter, target_count in chapter_distributions.values():
        for difficulty, weight in weights.items():
            count_for_this = int(target_count * weight)
            key = (chapter, difficulty)

            if key in by_chapter_difficulty:
                available = by_chapter_difficulty[key]
                # Remove already selected questions
                available = [q for q in available if q not in selected]

                if available:
                    picked = random.sample(
                        available,
                        min(count_for_this, len(available))
                    )
                    selected.extend(picked)

        # Fill remaining slots if not enough questions of target difficulties
        total_selected_for_chapter = len([q for q in selected if q['chapter'] == chapter])
        if total_selected_for_chapter < target_count:
            needed = target_count - total_selected_for_chapter
            candidates = [q for q in all_questions
                         if q['chapter'] == chapter and q not in selected]
            if candidates:
                picked = random.sample(candidates, min(needed, len(candidates)))
                selected.extend(picked)

    # Shuffle to mix chapters
    random.shuffle(selected)

    return selected[:25]

def format_mock_exam(selected_questions, mock_num):
    """Format the mock exam in markdown."""
    lines = [
        f"# 경제학 개론 모의고사 {mock_num}회 (25문제, 50분)",
        "",
        "목표 점수: 모의고사 1회 20/25, 2회 22/25, 3회 24/25",
        "",
    ]

    for i, q in enumerate(selected_questions, 1):
        lines.append(f"질문 {i}: {q['text']}")
        lines.append(f"A) {q['choices'].get('A', '')}")
        lines.append(f"B) {q['choices'].get('B', '')}")
        lines.append(f"C) {q['choices'].get('C', '')}")
        lines.append(f"D) {q['choices'].get('D', '')}")
        lines.append(f"정답: {q['answer']}")
        lines.append(f"해설: {q['explanation']}")
        lines.append("")

    # Answer key
    lines.append("# 정답표")
    lines.append("")
    answer_key = " ".join([q['answer'] for q in selected_questions])
    for i in range(0, 25, 5):
        lines.append(f"1-5: {' '.join(answer_key.split()[i:i+5])}")
    for i in range(5, 25, 5):
        if i + 5 <= 25:
            lines.append(f"{i+1}-{i+5}: {' '.join(answer_key.split()[i:i+5])}")

    return "\n".join(lines)

def main():
    print("Loading questions...")
    all_questions, by_chapter_difficulty = load_all_questions()

    # Generate 3 mock exams
    for mock_num in [1, 2, 3]:
        print(f"\nGenerating Mock Exam {mock_num}...")
        selected = select_mock_exam_questions(all_questions, by_chapter_difficulty, mock_num)

        # Verify no duplicates across mocks (simplified check)
        formatted = format_mock_exam(selected, mock_num)

        output_file = OUTPUT_DIR / f"모의고사_{mock_num}회.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted)

        print(f"  Saved to {output_file.name}")
        print(f"  Selected {len(selected)} questions")
        print(f"  Chapters: {sorted(set(q['chapter'] for q in selected))}")
        print(f"  Difficulties: {dict((d, len([q for q in selected if q['difficulty'] == d])) for d in ['기본', '응용', '함정'])}")

if __name__ == "__main__":
    main()
