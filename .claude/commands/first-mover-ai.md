# /first-mover-ai — First Mover AI 컨텐츠 파이프라인

Run the First Mover AI content generation pipeline.

Usage:
- `/first-mover-ai youtube` — Run YouTube longform pipeline (discover candidates + generate translation scripts)
- `/first-mover-ai instagram` — Run Instagram carousel pipeline (5 carousels, 2/2/1 split)
- `/first-mover-ai download [idx]` — Download chosen YouTube video (Layer 3, local only)
- `/first-mover-ai all` — Run both YouTube discover + Instagram

Steps:
1. Change to working directory: `projects/youtube-biz/`
2. Run the appropriate Python pipeline:
   - youtube: `python pipelines/first_mover_ai_youtube.py --stage=discover`
   - instagram: `python pipelines/first_mover_ai_instagram.py`
   - download: `python pipelines/first_mover_ai_youtube.py --stage=download --idx=$ARGUMENTS`
3. Report the output paths and summaries back to Keonhee
4. If drafts look good, suggest next manual steps (review, record, edit, upload)

Output locations:
- YouTube drafts: `channels/first-mover-ai/drafts/youtube/YYYY-MM-DD-scripts.json`
- Instagram drafts: `channels/first-mover-ai/drafts/instagram/YYYY-MM-DD-carousels.json`
- Downloaded videos: `channels/first-mover-ai/renders/originals/`
