#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build 3 mock exams from MCQ source files.

This script:
1. Verifies source files exist
2. Parses all MCQ questions from 3 source files
3. Generates 3 balanced mock exams (25 questions each)
4. Outputs to mock/ directory as markdown files

Distribution (always):
- Ch1-3: 8 qs (3+3+2)
- Ch4-6: 9 qs (3+3+3)
- Ch7-9: 8 qs (3+3+2)

Difficulty (varies by mock):
- Mock 1: 70% 기본, 30% 응용
- Mock 2: 40% 기본, 40% 응용, 20% 함정
- Mock 3: 20% 기본, 40% 응용, 40% 함정
"""

import re
import random
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set

# Configuration
BASE_DIR = Path(r"C:\Users\keonh\OneDrive\바탕 화면\MCP_Agentic AI\projects\study-materials")
SOURCE_FILES = {
    "Ch1-3": BASE_DIR / "경제학개론_MCQ_1-3장.md",
    "Ch4-6": BASE_DIR / "경제학개론_MCQ_4-6장.md",
    "Ch7-9": BASE_DIR / "경제학개론_MCQ_7-9장.md",
}
OUTPUT_DIR = BASE_DIR / "mock"

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


class Question:
    """Represents one MCQ question."""

    def __init__(self, chapter: int, difficulty: str, text: str,
                 choices: Dict[str, str], answer: str, explanation: str):
        self.chapter = chapter
        self.difficulty = difficulty
        self.text = text
        self.choices = choices  # {'A': '...', 'B': '...', 'C': '...', 'D': '...'}
        self.answer = answer  # 'A', 'B', 'C', or 'D'
        self.explanation = explanation
        self.id = id(self)

    def to_markdown(self, question_num: int) -> str:
        """Format as markdown for exam."""
        lines = [
            f"질문 {question_num}: {self.text}",
            f"A) {self.choices['A']}",
            f"B) {self.choices['B']}",
            f"C) {self.choices['C']}",
            f"D) {self.choices['D']}",
            f"정답: {self.answer}",
            f"해설: {self.explanation}",
            "",
        ]
        return "\n".join(lines)


class QuestionParser:
    """Parse questions from markdown files."""

    @staticmethod
    def parse_file(filepath: Path) -> List[Question]:
        """Parse a single markdown file."""
        if not filepath.exists():
            print(f"  ✗ File not found: {filepath}")
            return []

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        questions = []

        # Extract chapter/difficulty context as we parse
        current_chapter = None
        current_difficulty = "기본"

        # First pass: find all chapter and difficulty headers to build map
        header_map = {}  # position -> (chapter, difficulty)
        for match in re.finditer(r'^##\s*(\d+)장', content, re.MULTILINE):
            current_chapter = int(match.group(1))
            header_map[match.start()] = ('ch', current_chapter)

        for match in re.finditer(r'^###\s*[\d-]+\.\s*(기본|응용|함정)', content, re.MULTILINE):
            current_difficulty = match.group(1)
            header_map[match.start()] = ('diff', current_difficulty)

        # Second pass: parse questions with context
        current_chapter = None
        current_difficulty = "기본"

        for match in re.finditer(r'^##\s*(\d+)장', content, re.MULTILINE):
            current_chapter = int(match.group(1))

        for match in re.finditer(r'^###\s*[\d-]+\.\s*(기본|응용|함정)', content, re.MULTILINE):
            current_difficulty = match.group(1)

        # Parse actual questions
        q_pattern = r'질문\s+(\d+):(.*?)(?=질문\s+\d+:|$)'

        for q_match in re.finditer(q_pattern, content, re.DOTALL):
            # Determine chapter and difficulty from context before this question
            before_text = content[:q_match.start()]

            # Get most recent chapter
            ch_matches = list(re.finditer(r'##\s*(\d+)장', before_text))
            if ch_matches:
                current_chapter = int(ch_matches[-1].group(1))

            # Get most recent difficulty
            diff_matches = list(re.finditer(r'###\s*[\d-]+\.\s*(기본|응용|함정)', before_text))
            if diff_matches:
                current_difficulty = diff_matches[-1].group(1)

            # Parse question block
            q_block = q_match.group(2).strip()
            q_lines = q_block.split('\n')

            if not q_lines:
                continue

            # Extract question text (first line)
            q_text = q_lines[0].strip()
            if not q_text:
                continue

            # Extract choices
            choices = {}
            answer = None
            explanation = ""

            for line in q_lines[1:]:
                line = line.strip()
                if not line:
                    continue

                # Match choice: A) text, B) text, etc.
                choice_match = re.match(r'^([A-D])\)\s*(.+)$', line)
                if choice_match:
                    letter = choice_match.group(1)
                    text = choice_match.group(2)
                    choices[letter] = text
                    continue

                # Match answer: 정답: A or 정답: [A]
                if '정답' in line:
                    ans_match = re.search(r'정답:\s*\[?([A-D])\]?', line)
                    if ans_match:
                        answer = ans_match.group(1)
                    continue

                # Match explanation: 해설: ...
                if '해설' in line:
                    # Get all remaining lines as explanation
                    expl_idx = q_lines.index(line)
                    expl_lines = q_lines[expl_idx:]
                    expl_text = '\n'.join(expl_lines)
                    explanation = re.sub(r'^해설:\s*', '', expl_text, flags=re.IGNORECASE).strip()
                    break

            # Validate and create question
            if (current_chapter is not None and
                len(choices) == 4 and
                answer and
                answer in choices):

                questions.append(Question(
                    chapter=current_chapter,
                    difficulty=current_difficulty,
                    text=q_text,
                    choices=choices,
                    answer=answer,
                    explanation=explanation,
                ))

        return questions


def load_all_questions() -> Tuple[List[Question], Dict]:
    """Load all questions from source files."""
    all_questions = []
    by_ch_diff = defaultdict(list)

    print("📖 Loading questions from source files...\n")

    for label, filepath in SOURCE_FILES.items():
        questions = QuestionParser.parse_file(filepath)
        all_questions.extend(questions)

        if questions:
            print(f"  ✓ {label}: {len(questions)} questions")

            # Stats for this file
            for q in questions:
                by_ch_diff[(q.chapter, q.difficulty)].append(q)
        else:
            print(f"  ✗ {label}: 0 questions (check file)")

    print(f"\n✅ Total: {len(all_questions)} questions loaded\n")

    # Print distribution
    print("📊 Distribution by Chapter & Difficulty:")
    for ch in range(1, 10):
        row = []
        for diff in ['기본', '응용', '함정']:
            count = len(by_ch_diff[(ch, diff)])
            if count > 0:
                row.append(f"{diff}:{count}")
        if row:
            print(f"  Ch{ch}: {' | '.join(row)}")

    return all_questions, by_ch_diff


class ExamGenerator:
    """Generate balanced mock exams."""

    # Always the same chapter distribution
    CHAPTER_TARGETS = {
        1: 3, 2: 3, 3: 2,
        4: 3, 5: 3, 6: 3,
        7: 3, 8: 3, 9: 2,
    }

    # Difficulty weighting by mock level
    DIFFICULTY_WEIGHTS = {
        1: {'기본': 0.70, '응용': 0.30, '함정': 0.00},  # Warm-up
        2: {'기본': 0.40, '응용': 0.40, '함정': 0.20},  # Realistic
        3: {'기본': 0.20, '응용': 0.40, '함정': 0.40},  # Hard
    }

    def __init__(self, all_questions: List[Question], by_ch_diff: Dict):
        self.all_questions = all_questions
        self.by_ch_diff = by_ch_diff
        self.used_ids: Set[int] = set()

    def generate(self, mock_num: int) -> List[Question]:
        """Generate one mock exam."""
        # Reset used questions for this exam
        self.used_ids.clear()

        # Use deterministic seed for reproducibility
        random.seed(mock_num * 12345)

        selected = []
        targets = self.CHAPTER_TARGETS
        weights = self.DIFFICULTY_WEIGHTS[mock_num]

        # For each chapter, select questions by difficulty weight
        for chapter in sorted(targets.keys()):
            target_count = targets[chapter]
            chapter_questions = []

            # Try to select with difficulty weights
            for difficulty in sorted(weights.keys()):
                weight = weights[difficulty]
                desired_count = int(target_count * weight + 0.5)

                if desired_count > 0:
                    key = (chapter, difficulty)
                    available = [q for q in self.by_ch_diff[key]
                                if q.id not in self.used_ids]

                    if available:
                        picked = random.sample(available, min(desired_count, len(available)))
                        chapter_questions.extend(picked)
                        for q in picked:
                            self.used_ids.add(q.id)

            # Fill any remaining slots
            if len(chapter_questions) < target_count:
                needed = target_count - len(chapter_questions)
                for difficulty in ['기본', '응용', '함정']:
                    if needed <= 0:
                        break
                    key = (chapter, difficulty)
                    available = [q for q in self.by_ch_diff[key]
                                if q.id not in self.used_ids]

                    if available:
                        picked = random.sample(available, min(needed, len(available)))
                        chapter_questions.extend(picked)
                        needed -= len(picked)
                        for q in picked:
                            self.used_ids.add(q.id)

            selected.extend(chapter_questions)

        # Shuffle to mix chapters
        random.shuffle(selected)

        return selected[:25]

    def print_stats(self, exam: List[Question], mock_num: int):
        """Print exam statistics."""
        ch_dist = defaultdict(int)
        diff_dist = defaultdict(int)

        for q in exam:
            ch_dist[q.chapter] += 1
            diff_dist[q.difficulty] += 1

        print(f"\n📋 Mock Exam {mock_num}:")
        print(f"   Chapters: {dict(sorted(ch_dist.items()))}")
        print(f"   Difficulty: {dict(sorted(diff_dist.items()))}")


def format_exam_markdown(questions: List[Question], mock_num: int) -> str:
    """Format exam as complete markdown file."""
    lines = [
        f"# 경제학 개론 모의고사 {mock_num}회 (25문제, 50분)",
        "",
        "목표 점수: 모의고사 1회 20/25, 2회 22/25, 3회 24/25",
        "",
    ]

    # Questions
    for i, question in enumerate(questions, 1):
        lines.append(question.to_markdown(i))

    # Answer key
    lines.append("# 정답표")
    lines.append("")
    answers = [q.answer for q in questions]
    lines.append(f"1-5: {' '.join(answers[0:5])}")
    lines.append(f"6-10: {' '.join(answers[5:10])}")
    lines.append(f"11-15: {' '.join(answers[10:15])}")
    lines.append(f"16-20: {' '.join(answers[15:20])}")
    lines.append(f"21-25: {' '.join(answers[20:25])}")

    return "\n".join(lines)


def main():
    print("\n" + "="*70)
    print("🎓 경제학 개론 모의고사 생성 시스템")
    print("="*70)

    # Load all questions
    all_questions, by_ch_diff = load_all_questions()

    if not all_questions:
        print("\n❌ Failed to load any questions. Check source files.")
        return False

    # Generate 3 mock exams
    print("\n" + "="*70)
    print("🎯 Generating Mock Exams")
    print("="*70)

    generator = ExamGenerator(all_questions, by_ch_diff)

    for mock_num in [1, 2, 3]:
        exam = generator.generate(mock_num)
        generator.print_stats(exam, mock_num)

        # Format and save
        markdown = format_exam_markdown(exam, mock_num)
        output_file = OUTPUT_DIR / f"모의고사_{mock_num}회.md"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"   💾 Saved: {output_file.name}")

    print("\n" + "="*70)
    print("✅ Successfully generated all 3 mock exams!")
    print("="*70 + "\n")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
