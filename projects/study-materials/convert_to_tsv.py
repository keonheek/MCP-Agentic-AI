"""
Convert Korean economics MCQ markdown files to TSV for Google Sheets import.
Outputs:
  google_forms_script/questions_sheet_data.tsv  — all MCQ questions
  google_forms_script/mock_sheet_data.tsv        — all mock exam questions
"""

import re
import os

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "google_forms_script")

CIRCLE_TO_LETTER = {"①": "A", "②": "B", "③": "C", "④": "D"}

# Map 제N장 header → chapter number string
CHAPTER_MAP = {
    "제1장": "1", "제2장": "2", "제3장": "3",
    "제4장": "4", "제5장": "5", "제6장": "6",
    "제7장": "7", "제8장": "8", "제9장": "9",
}


def clean_field(text):
    """Strip whitespace, tabs→space, newlines→space."""
    text = text.strip()
    text = text.replace("\t", " ")
    text = text.replace("\n", " ")
    text = re.sub(r" {2,}", " ", text)
    return text


def parse_mcq_file(path):
    """
    Parse a MCQ markdown file into list of dicts:
    {chapter, question, A, B, C, D, answer, explanation}
    """
    with open(path, encoding="utf-8") as f:
        content = f.read()

    rows = []
    current_chapter = None

    # Split into blocks by "---" separator (each question ends with ---)
    # First, identify chapter transitions using ## 제N장 headers
    lines = content.splitlines()

    # Build a list of (line_index, chapter) for chapter headers
    chapter_boundaries = []
    for i, line in enumerate(lines):
        for key, val in CHAPTER_MAP.items():
            if line.startswith(f"## {key}"):
                chapter_boundaries.append((i, val))
                break

    def chapter_at_line(lineno):
        ch = None
        for (idx, val) in chapter_boundaries:
            if idx <= lineno:
                ch = val
        return ch

    # Rejoin and split by question blocks
    # Each question block starts with **N. ...** and ends before the next **N.
    # Use regex to find all question blocks

    # Pattern: bold question line, 4 choices, 정답, 해설
    question_pattern = re.compile(
        r"\*\*(\d+)\.\s*(.*?)\*\*\s*\n"   # **N. question text**
        r"①\s*(.*?)\n"
        r"②\s*(.*?)\n"
        r"③\s*(.*?)\n"
        r"④\s*(.*?)\n"
        r"\s*정답:\s*([①②③④])\s*\n"
        r"해설:\s*(.*?)(?=\n---|\n\*\*\d+\.|\Z)",
        re.DOTALL
    )

    for m in question_pattern.finditer(content):
        q_num = int(m.group(1))
        question = clean_field(m.group(2))
        a = clean_field(m.group(3))
        b = clean_field(m.group(4))
        c = clean_field(m.group(5))
        d = clean_field(m.group(6))
        raw_answer = m.group(7).strip()
        explanation = clean_field(m.group(8))

        answer_letter = CIRCLE_TO_LETTER.get(raw_answer, raw_answer)

        # Determine chapter from position in file
        start_pos = m.start()
        # Count newlines up to this position to get approximate line number
        line_at = content[:start_pos].count("\n")
        chapter = chapter_at_line(line_at)

        rows.append({
            "chapter": chapter or "",
            "question": question,
            "A": a,
            "B": b,
            "C": c,
            "D": d,
            "answer": answer_letter,
            "explanation": explanation,
        })

    return rows


def parse_mock_file(path, exam_number):
    """
    Parse a mock exam markdown file into list of dicts:
    {exam_number, question, A, B, C, D, answer, explanation}
    """
    with open(path, encoding="utf-8") as f:
        content = f.read()

    rows = []

    # Pattern: 질문 N: question\nA) ...\nB) ...\nC) ...\nD) ...\n정답: X\n해설: ...
    question_pattern = re.compile(
        r"질문\s+(\d+):\s*(.*?)\n"
        r"A\)\s*(.*?)\n"
        r"B\)\s*(.*?)\n"
        r"C\)\s*(.*?)\n"
        r"D\)\s*(.*?)\n"
        r"정답:\s*([A-D])\s*\n"
        r"해설:\s*(.*?)(?=\n질문\s+\d+:|\n#|\Z)",
        re.DOTALL
    )

    for m in question_pattern.finditer(content):
        question = clean_field(m.group(2))
        a = clean_field(m.group(3))
        b = clean_field(m.group(4))
        c = clean_field(m.group(5))
        d = clean_field(m.group(6))
        answer = m.group(7).strip()
        explanation = clean_field(m.group(8))

        rows.append({
            "exam_number": str(exam_number),
            "question": question,
            "A": a,
            "B": b,
            "C": c,
            "D": d,
            "answer": answer,
            "explanation": explanation,
        })

    return rows


def write_tsv(path, headers, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\t".join(headers) + "\n")
        for row in rows:
            line = "\t".join(row[h.lower()] for h in headers)
            f.write(line + "\n")


def main():
    mcq_files = [
        os.path.join(BASE, "경제학개론_MCQ_1-3장.md"),
        os.path.join(BASE, "경제학개론_MCQ_4-6장.md"),
        os.path.join(BASE, "경제학개론_MCQ_7-9장.md"),
    ]

    mock_files = [
        (os.path.join(BASE, "mock", "모의고사_1회.md"), 1),
        (os.path.join(BASE, "mock", "모의고사_2회.md"), 2),
        (os.path.join(BASE, "mock", "모의고사_3회.md"), 3),
    ]

    # --- MCQ questions ---
    all_mcq = []
    for path in mcq_files:
        rows = parse_mcq_file(path)
        print(f"  {os.path.basename(path)}: {len(rows)} questions parsed")
        all_mcq.extend(rows)

    mcq_out = os.path.join(OUT_DIR, "questions_sheet_data.tsv")
    # Header keys must match dict keys (lowercased for lookup)
    mcq_headers = ["Chapter", "Question", "A", "B", "C", "D", "Answer", "Explanation"]

    # Adjust write_tsv for mixed-case headers
    with open(mcq_out, "w", encoding="utf-8", newline="") as f:
        f.write("\t".join(mcq_headers) + "\n")
        for row in all_mcq:
            fields = [
                row["chapter"],
                row["question"],
                row["A"],
                row["B"],
                row["C"],
                row["D"],
                row["answer"],
                row["explanation"],
            ]
            f.write("\t".join(fields) + "\n")

    print(f"\nWrote {len(all_mcq)} rows to questions_sheet_data.tsv")

    # --- Mock exams ---
    all_mock = []
    for path, num in mock_files:
        rows = parse_mock_file(path, num)
        print(f"  모의고사_{num}회.md: {len(rows)} questions parsed")
        all_mock.extend(rows)

    mock_out = os.path.join(OUT_DIR, "mock_sheet_data.tsv")
    with open(mock_out, "w", encoding="utf-8", newline="") as f:
        f.write("ExamNumber\tQuestion\tA\tB\tC\tD\tAnswer\tExplanation\n")
        for row in all_mock:
            fields = [
                row["exam_number"],
                row["question"],
                row["A"],
                row["B"],
                row["C"],
                row["D"],
                row["answer"],
                row["explanation"],
            ]
            f.write("\t".join(fields) + "\n")

    print(f"Wrote {len(all_mock)} rows to mock_sheet_data.tsv")


if __name__ == "__main__":
    main()
