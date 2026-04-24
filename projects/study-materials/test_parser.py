#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

BASE = "/c/Users/keonh/OneDrive/바탕 화면/MCP_Agentic AI/projects/study-materials"
file1 = os.path.join(BASE, "경제학개론_MCQ_1-3장.md")

# Just read and print first 3000 chars
if os.path.exists(file1):
    with open(file1, 'r', encoding='utf-8') as f:
        content = f.read(3000)
    print(content)
    print("\n" + "="*80 + "\n")
    print(f"File exists. Total size check:")
    with open(file1, 'r', encoding='utf-8') as f:
        full = f.read()
    print(f"Total chars: {len(full)}")
    print(f"Line count: {len(full.split(chr(10)))}")
else:
    print(f"File not found: {file1}")
    print(f"Path exists: {os.path.exists(BASE)}")
    print(f"Contents of {BASE}:")
    if os.path.exists(BASE):
        for item in os.listdir(BASE):
            print(f"  {item}")
