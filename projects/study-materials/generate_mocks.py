#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate 3 mock exams from MCQ source files.

Input: 3 source markdown files with 212 total MCQ questions (Ch1-9)
Output: 3 balanced mock exams, 25 questions each, no duplication

Distribution per exam:
- Ch1-3: 8 questions (3+3+2)
- Ch4-6: 9 questions (3+3+3)
- Ch7-9: 8 questions (3+3+2)

Difficulty weighting:
- Mock 1: 70% 기본, 30% 응용 (warm-up)
- Mock 2: 40% 기본, 40% 응용, 20% 함정 (realistic)
- Mock 3: 20% 기본, 40% 응용, 40% 함정 (hardest)
"""

import re
import random
import os
from pathlib import Path
from collections import defaultdict

# Configuration
BASE_DIR = Path("/c/Users/keonh/OneDrive/바탕 화면/MCP_Agentic AI/projects/study-materials")
SOURCE_FILES = [
    BASE_DIR / "경제학개론_MCQ_1-3장.md",
    BASE_DIR / "경제학개론_MCQ_4-6장.md",
    BASE_DIR / "경제학개론_MCQ_7-9장.md",
]
OUTPUT_DIR = BASE_DIR / "mock"
OUTPUT_DIR.mkdir(exist_ok=True)

class QuestionParser:
    """Parse MCQ questions from markdown files."""

    def __init__(self):
        self.questions = []

    def parse_file(self, filepath):
        """
        Parse a markdown file containing MCQ questions.

        Flexible parser that handles variations in formatting.
        Expected structure:
        - ## N장 (chapter header)
        - ### N-M. 기본/응용/함정 (difficulty section)
        - 질문 N: [question text]
        - A) [choice A]
        - B) [choice B]
        - C) [choice C]
        - D) [choice D]
        - 정답: [X]
        - 해설: [explanation]
        """
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            return 0

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        questions = []
        current_chapter = None
        current_difficulty = "기본"

        # Track chapter and difficulty as we parse
        for line in content.split('\n'):
            # Update chapter if header found
            ch_match = re.match(r'^##\s*(\d+)장', line)
            if ch_match:
                current_chapter = int(ch_match.group(1))

            # Update difficulty if section header found
            diff_match = re.match(r'^###\s*[\d-]+\.\s*(기본|응용|함정)', line)
            if diff_match:
                current_difficulty = diff_match.group(1)

        # Now parse questions using regex
        # Pattern: 질문 N: ... until next 질문 or EOF
        q_pattern = r'질문\s+(\d+):(.*?)(?=질문\s+\d+:|$)'
        q_matches = list(re.finditer(q_pattern, content, re.DOTALL))

        for match in q_matches:
            q_num = int(match.group(1))
            q_block = match.group(2).strip()

            # Get context before this question to infer chapter/difficulty
            before = content[:match.start()]

            # Extract chapter from last ## N장
            ch_search = re.findall(r'##\s*(\d+)장', before)
            if ch_search:
                current_chapter = int(ch_search[-1])

            # Extract difficulty from last ### ... (기본|응용|함정)
            diff_search = re.findall(r'###\s*[\d-]+\.\s*(기본|응용|함정)', before)
            if diff_search:
                current_difficulty = diff_search[-1]

            # Parse question text (first line)
            q_lines = q_block.split('\n')
            q_text = q_lines[0].strip()

            if not q_text:
                continue

            # Parse choices (A, B, C, D)
            choices = {}
            for line in q_lines[1:]:
                line_stripped = line.strip()
                choice_match = re.match(r'^([A-D])\)\s*(.+)$', line_stripped)
                if choice_match:
                    letter = choice_match.group(1)
                    text = choice_match.group(2)
                    choices[letter] = text

            # Parse answer (정답: X or 정답: [X])
            answer = None
            for line in q_lines[1:]:
                if '정답' in line:
                    ans_match = re.search(r'정답:\s*\[?([A-D])\]?', line)
                    if ans_match:
                        answer = ans_match.group(1)
                    break

            # Parse explanation (해설: ...)
            explanation = ""
            for i, line in enumerate(q_lines[1:]):
                if '해설' in line:
                    expl_lines = q_lines[1 + i:]
                    expl_text = '\n'.join(expl_lines)
                    explanation = re.sub(r'^해설:\s*', '', expl_text, flags=re.IGNORECASE).strip()
                    break

            # Validate and store
            if (current_chapter and
                len(choices) == 4 and
                answer and
                answer in choices):

                questions.append({
                    'chapter': current_chapter,
                    'difficulty': current_difficulty,
                    'text': q_text,
                    'choices': choices,
                    'answer': answer,
                    'explanation': explanation,
                    'q_num': q_num,
                })

        self.questions.extend(questions)
        return len(questions)

    def get_all_questions(self):
        """Return all parsed questions, grouped by (chapter, difficulty)."""
        by_ch_diff = defaultdict(list)
        for q in self.questions:
            key = (q['chapter'], q['difficulty'])
            by_ch_diff[key].append(q)
        return self.questions, by_ch_diff

    def print_stats(self):
        """Print parsing statistics."""
        total = len(self.questions)
        print(f"\n📊 Total questions parsed: {total}")

        by_ch = defaultdict(int)
        by_diff = defaultdict(int)
        for q in self.questions:
            by_ch[q['chapter']] += 1
            by_diff[q['difficulty']] += 1

        print(f"\n📖 By Chapter:")
        for ch in sorted(by_ch.keys()):
            print(f"   Ch{ch}: {by_ch[ch]} questions")

        print(f"\n🎯 By Difficulty:")
        for diff in sorted(by_diff.keys()):
            print(f"   {diff}: {by_diff[diff]} questions")


class MockExamGenerator:
    """Generate balanced mock exams from question pool."""

    # Chapter targets (always same distribution)
    CHAPTER_TARGETS = {
        1: 3, 2: 3, 3: 2,
        4: 3, 5: 3, 6: 3,
        7: 3, 8: 3, 9: 2,
    }

    # Difficulty weights by mock
    DIFFICULTY_WEIGHTS = {
        1: {'기본': 0.70, '응용': 0.30, '함정': 0.00},
        2: {'기본': 0.40, '응용': 0.40, '함정': 0.20},
        3: {'기본': 0.20, '응용': 0.40, '함정': 0.40},
    }

    def __init__(self, all_questions, by_ch_diff):
        self.all_questions = all_questions
        self.by_ch_diff = by_ch_diff
        self.used_questions = set()

    def generate_exam(self, mock_num):
        """Generate one mock exam with proper distribution and difficulty balance."""
        random.seed(mock_num * 2024)

        selected = []
        targets = self.CHAPTER_TARGETS
        weights = self.DIFFICULTY_WEIGHTS[mock_num]

        for chapter in sorted(targets.keys()):
            target_count = targets[chapter]
            chapter_selected = []

            # Try to fill with weighted distribution
            for difficulty in sorted(weights.keys()):
                weight = weights[difficulty]
                desired = int(target_count * weight + 0.5)

                if desired > 0:
                    key = (chapter, difficulty)
                    available = [q for q in self.by_ch_diff[key]
                               if id(q) not in self.used_questions]

                    if available:
                        picked = random.sample(available, min(desired, len(available)))
                        chapter_selected.extend(picked)
                        for p in picked:
                            self.used_questions.add(id(p))

            # Fill remaining slots if needed
            if len(chapter_selected) < target_count:
                needed = target_count - len(chapter_selected)
                for difficulty in ['기본', '응용', '함정']:
                    key = (chapter, difficulty)
                    available = [q for q in self.by_ch_diff[key]
                               if id(q) not in self.used_questions]

                    if available and needed > 0:
                        picked = random.sample(available, min(needed, len(available)))
                        chapter_selected.extend(picked)
                        needed -= len(picked)
                        for p in picked:
                            self.used_questions.add(id(p))

            selected.extend(chapter_selected)

        # Shuffle to mix chapters
        random.shuffle(selected)
        return selected[:25]

    def print_exam_stats(self, exam, mock_num):
        """Print statistics for generated exam."""
        by_ch = defaultdict(int)
        by_diff = defaultdict(int)
        for q in exam:
            by_ch[q['chapter']] += 1
            by_diff[q['difficulty']] += 1

        print(f"\n📋 Mock Exam {mock_num}:")
        print(f"   Chapters: {dict(sorted(by_ch.items()))}")
        print(f"   Difficulty: {dict(sorted(by_diff.items()))}")


def format_exam_markdown(questions, mock_num):
    """Format exam as markdown with answer key."""
    lines = [
        f"# 경제학 개론 모의고사 {mock_num}회 (25문제, 50분)",
        "",
        "목표 점수: 모의고사 1회 20/25, 2회 22/25, 3회 24/25",
        "",
    ]

    # Questions
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
    print("=" * 80)
    print("📚 경제학 개론 모의고사 생성기")
    print("=" * 80)

    # Parse all source files
    print("\n🔍 Parsing source files...")
    parser = QuestionParser()

    total_parsed = 0
    for filepath in SOURCE_FILES:
        count = parser.parse_file(filepath)
        if count > 0:
            print(f"✅ {filepath.name}: {count} questions")
            total_parsed += count

    if total_parsed == 0:
        print("❌ No questions parsed. Check file paths and format.")
        return

    parser.print_stats()

    # Generate mock exams
    print("\n" + "=" * 80)
    print("🎯 Generating Mock Exams")
    print("=" * 80)

    all_q, by_ch_diff = parser.get_all_questions()
    generator = MockExamGenerator(all_q, by_ch_diff)

    for mock_num in [1, 2, 3]:
        exam = generator.generate_exam(mock_num)
        generator.print_exam_stats(exam, mock_num)

        # Format and save
        formatted = format_exam_markdown(exam, mock_num)
        output_file = OUTPUT_DIR / f"모의고사_{mock_num}회.md"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted)

        print(f"   💾 Saved: {output_file}")

    print("\n" + "=" * 80)
    print("✅ Mock exams generated successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
