import os

# Read all three source files to understand structure
files = [
    "/c/Users/keonh/OneDrive/바탕 화면/MCP_Agentic AI/projects/study-materials/경제학개론_MCQ_1-3장.md",
    "/c/Users/keonh/OneDrive/바탕 화면/MCP_Agentic AI/projects/study-materials/경제학개론_MCQ_4-6장.md",
    "/c/Users/keonh/OneDrive/바탕 화면/MCP_Agentic AI/projects/study-materials/경제학개론_MCQ_7-9장.md",
]

for filepath in files:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"\n{'='*80}")
            print(f"FILE: {filepath.split('/')[-1]}")
            print(f"{'='*80}")
            print(f"Length: {len(content)} chars")
            print(f"First 2000 chars:")
            print(content[:2000])
    else:
        print(f"File not found: {filepath}")
