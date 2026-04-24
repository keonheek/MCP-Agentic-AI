# 3D Landing Page Action Plan — Final (Score: 7.7/10)

_Autoresearch loop: 12 iterations | completeness=7.2 | specificity=8.1 | actionability=7.8_

---

# 온기 카페 — Cinematic 3D Landing Page: Complete Action Plan
### April 7–13, 2026 | Portfolio Piece → Testimonial → Case Study

---

## Master Overview

| Dimension | Target | Method |
|---|---|---|
| Goal | Free mockup → testimonial → paid client | Deploy before outreach |
| Timeline | 7 days (April 7–13) | Day-by-day schedule below |
| Stack | Nano Banana → Cling 3.0 → Antigravity → Vercel | Viktor Oddy workflow |
| Conversion layer | Ryan Mathews framework | Applied section by section |
| Viral layer | Figma/browser recording → Twitter | After deploy |

---

## Pre-Work: Gather Raw Materials (Sunday, April 6 — 1 hour)

Do this the night before so Monday morning is unblocked.

**Action 1 — Screenshot 온기 카페's existing digital presence**
- Open Google Maps → search "온기 카페" → screenshot their listing photos (save 10–15 images)
- Open their Instagram → screenshot 6–8 of their best food/atmosphere photos
- Open Naver Map → search "온기 카페" → screenshot their Naver Place page (you will embed this later)
- Save all screenshots into one folder: `/onggi-cafe/raw-assets/`
- **Time:** 20 minutes
- **Output:** 20–25 reference images of the real café

**Action 2 — Record the current state of their web presence**
- If they have a website, screen-record a 30-second scroll through it (this becomes your "before" footage)
- If no website exists, screenshot their Instagram bio page — this IS the before
- Save as `before-onggi.mp4` or `before-onggi.png`
- **Time:** 10 minutes
- **Output:** "Before" asset for case study comparison video

**Action 3 — Write down the café's core details**
Open a plain text file and write these now so you don't stop mid-build to look them up:
```
카페 이름: 온기 카페
주소: [fill in exact address from Naver Map]
영업시간: [fill in from their Naver Place or Instagram]
대표 메뉴: [e.g., 시그니처 라떼, 크로플, 스콘 — fill from their posts]
인스타그램: @[handle]
카카오채널: [if they have one]
Naver Place URL: [copy full URL from Naver Map]
```
- **Time:** 10 minutes
- **Output:** `cafe-details.txt` — your single source of truth for all copy

**Action 4 — Install/confirm all accounts are active**
- Log into Nano Banana → confirm credits are loaded (you need ~20 generations)
- Log into Cling 3.0 → confirm subscription is active (need image-to-video, start/end frame mode)
- Log into Antigravity → confirm Gemini 3.1 builder is available (NOT the old version)
- Log into Vercel → confirm free account is active
- Download screen recorder: **OBS Studio** (free, no watermark) if you don't have one
- **Time:** 20 minutes
- **Output:** All four tools confirmed ready — zero Monday morning blockers

---

## Day 1 — Monday, April 7: Reference Design + Hero Image Generation

**Total estimated time: 4–5 hours**

---

### Step 1.1 — Find and Capture Reference Design (Viktor Oddy Step 1)
**Time:** 45 minutes

This is the most important step. You are NOT starting from a blank canvas. The reference design is what you will feed to Antigravity as your visual brief. Do not skip this.

**Where to search (in this order):**

1. **Awwwards.com** → Filter by: Industry = Food & Drink → Sort by: Awards → Look for sites with dark, cinematic aesthetics (moody, warm amber tones match 온기 카페's warmth concept)
2. **Land-book.com** → Search "cafe" or "restaurant" → filter for full-page hero layouts
3. **Lapa.ninja** → Category: Food → look for sites where the hero is a full-bleed video or parallax image
4. **Godly.website** → Search "cafe" → premium tier, very cinematic

**What you are looking for — exact criteria:**
- Full-bleed hero image or video background (scroll-driven)
- Minimal navigation (logo left, 1–2 links right, CTA button)
- Large serif or display headline over the hero
- Dark or warm-toned color palette (not white/clinical)
- Visible scroll-based animations (parallax, fade-in sections)
- At least one social proof element visible (review count, award badge, press logo)

**When you find the right reference:**
- Take a full-page screenshot using browser extension **GoFullPage** (Chrome extension, free)
- Screenshot should be saved as `reference-design.png` into `/onggi-cafe/reference/`
- Also copy the URL into `cafe-details.txt` under "Reference URL"
- Optionally find a second reference for a specific section (e.g., a testimonial section you like from a different site) — save as `reference-testimonials.png`

**Output:** 1–2 full-page reference screenshots that will be pasted directly into Antigravity

---

### Step 1.2 — Write Hero Image Generation Prompts (Nano Banana Pre-Work)
**Time:** 20 minutes

Before opening Nano Banana, write your prompts in a text file. Prompt quality determines everything downstream.

**Prompt Template (copy and customize each one):**

```
Prompt 1 — Wide establishing shot:
"Cinematic wide-angle interior of a cozy Korean cafe, warm amber
and golden light, wooden furniture, ceramic cups on marble counter,
steam rising from coffee, shallow depth of field, film grain,
35mm photography style, moody and intimate atmosphere, no people,
ultra high resolution"

Prompt 2 — Close-up hero detail:
"Extreme close-up of a hand-crafted latte with latte art in a
ceramic mug, warm amber bokeh background, Korean cafe interior,
steam wisps, cinematic lighting, golden hour warmth, photorealistic,
8K detail"

Prompt 3 — Overhead flat lay:
"Top-down overhead shot of Korean cafe table setting, ceramic cups,
croffle pastry, wooden tray, marble surface, warm morning light,
lifestyle photography, editorial quality, film grain"

Prompt 4 — Exterior golden hour:
"Exterior of a small Korean cafe at golden hour, warm light spilling
through windows, Seoul street, minimal signage, cinematic lens flare,
35mm film photography, intimate and inviting"

Prompt 5 — Atmospheric mood:
"Interior of Korean cafe, bokeh lights in background, foreground
coffee cup, deep shadows and warm highlights, noir-adjacent mood,
quiet morning, no people, cinematic color grading, anamorphic lens"
```

**Save this file as** `nano-banana-prompts.txt`

---

### Step 1.3 — Generate Hero Images in Nano Banana (Viktor Oddy Step 2)
**Time:** 60–90 minutes

**Exact process:**

1. Open Nano Banana → New Project → name it "온기 카페 Hero"
2. Paste **Prompt 1** into the generation field
3. Set image dimensions to **1920×1080** (landscape, 16:9) — this is required for Cling 3.0 compatibility
4. Generate → wait for output (typically 30–60 seconds per generation)
5. Generate the same prompt **3 times** → you want variations to choose from
6. Repeat for all 5 prompts (you will generate ~15 total images)
7. Download ALL generations — do not curate yet
8. Save into `/onggi-cafe/hero-images/raw/`

**Curation round (after all generations complete):**
- Select your top **3 images** based on these criteria:
  - ✅ Strong focal point (the eye knows where to look immediately)
  - ✅ Good color temperature (warm amber — matches 온기 카페 brand warmth)
  - ✅ Space at top for text overlay (headline needs breathing room — avoid images where the busiest area is at the top center)
  - ✅ High detail at edges (edges move during parallax — they must hold up)
  - ❌ Reject: any with visible text, watermarks, or distorted objects

- Name your top 3: `hero-A.png`, `hero-B.png`, `hero-C.png`
- Save into `/onggi-cafe/hero-images/selected/`

**Output:** 3 hero images at 1920×1080, no text, cinematic quality

---

### Step 1.4 — Generate Start/End Frame Pairs for Cling 3.0 (Preparation)
**Time:** 30 minutes

Cling 3.0's image-to-video mode works best when you define a clear start state and end state. You need to create a second "end frame" image for each hero image that represents where the camera will be AFTER the scroll animation.

**Method — use Nano Banana again with a modified prompt:**

For each of your 3 selected hero images, generate an "end frame" that simulates:
- **Very slight zoom in** (camera has crept forward ~5–10%)
- **Very slight upward tilt** (camera has risen slightly)
- Identical color/mood/content — only the camera position changes

**End Frame Prompt Template:**
```
"[Same prompt as the start frame], but slightly zoomed in,
camera slightly elevated, same scene, same lighting,
subtle perspective shift as if camera slowly moved forward and up"
```

Generate 3 end frames (one per hero) → save as `hero-A-end.png`, `hero-B-end.png`, `hero-C-end.png`

**Output:** 3 start/end frame pairs ready for Cling 3.0

---

## Day 2 — Tuesday, April 8: Cling 3.0 Animation + JPEG Sequence Export

**Total estimated time: 4–5 hours**

---

### Step 2.1 — Animate Images in Cling 3.0 (Viktor Oddy Step 3)
**Time:** 60–90 minutes (includes waiting for renders)

**Exact process:**

1. Open Cling 3.0 → Select **Image-to-Video** mode
2. For Hero A:
   - Upload `hero-A.png` as the **Start Frame**
   - Upload `hero-A-end.png` as the **End Frame**
   - Duration: **6 seconds** (minimum needed for a smooth JPEG sequence)
   - Motion intensity: **Low** (you want subtle, cinematic movement — not a jarring zoom)
   - Prompt field: type `"slow cinematic camera push-in, subtle zoom, warm cafe interior, no cuts"`
   - Click Generate
3. Repeat for Hero B and Hero C
4. While renders are processing (5–15 minutes each), move on to Step 2.2

**Settings reference:**
| Setting | Value | Why |
|---|---|---|
| Mode | Image-to-Video (start/end frame) | Controls exact motion path |
| Duration | 6 seconds | Enough frames for smooth JPEG sequence |
| Resolution | 1920×1080 | Matches hero images |
| Motion intensity | Low | Cinematic, not jarring |
| FPS output | 24 fps | Standard cinematic; gives 144 frames at 6 sec |

5. Download all 3 rendered videos → save as `hero-A.mp4`, `hero-B.mp4`, `hero-C.mp4` into `/onggi-cafe/animations/`

**Output:** 3 animated MP4 videos, 6 seconds each, cinematic slow push-in

---

**⚠️ Troubleshooting — Cling 3.0 Common Issues:**

| Problem | Likely Cause | Fix |
|---|---|---|
| Output looks choppy/stuttery | Motion intensity too high | Re-generate at "Low" or "Minimal" |
| Start and end frames look disconnected | End frame is too different from start | Re-generate end frame with closer framing |
| Output is only 3 seconds | Credit/plan limitation | Check plan tier — you may need 6-second minimum plan |
| Faces or text appear distorted | Cling hallucinating content | Use only abstract/atmospheric images, no close human faces |
| Render fails | Server queue | Wait 10 min and resubmit; avoid peak hours (9am–12pm PST) |

---

### Step 2.2 — Extract JPEG Sequence from MP4 (Viktor Oddy Step 4)
**Time:** 30–45 minutes

You will convert each MP4 into a folder of numbered JPEG frames. These frames become your scroll-driven background — as the user scrolls, JavaScript cycles through these frames to create the illusion of a smooth cinematic scroll.

**Tool: FFmpeg (free, command-line)**

If FFmpeg is not installed:
- Mac: open Terminal → type `brew install ffmpeg` → press Enter → wait ~3 minutes
- Windows: download from ffmpeg.org → extract ZIP → add to PATH (Google "ffmpeg add to PATH Windows" — 5 minutes)

**Commands — run these in Terminal/Command Prompt:**

```bash
# First, navigate to your animations folder
cd /path/to/onggi-cafe/animations/

# Create output folders
mkdir hero-A-frames
mkdir hero-B-frames
mkdir hero-C-frames

# Extract frames from Hero A at 24fps, high quality JPEG
ffmpeg -i hero-A.mp4 -vf fps=24 -q:v 2 hero-A-frames/frame_%04d.jpg

# Extract frames from Hero B
ffmpeg -i hero-B.mp4 -vf fps=24 -q:v 2 hero-B-frames/frame_%04d.jpg

# Extract frames from Hero C
ffmpeg -i hero-C.mp4 -vf fps=24 -q:v 2 hero-C-frames/frame_%04d.jpg
```

**What these flags mean:**
- `-vf fps=24` → extract exactly 24 frames per second
- `-q:v 2` → JPEG quality level 2 (scale 1–31, lower = higher quality; use 2 for web)
- `frame_%04d.jpg` → names files `frame_0001.jpg`, `frame_0002.jpg`, etc.

**Expected output:**
- Hero A: ~144 JPEG files (6 sec × 24 fps)
- Hero B: ~144 JPEG files
- Hero C: ~144 JPEG files
- Each file: roughly 200–400KB at 1920×1080, quality 2

**Optimization step — resize for web performance:**
```bash
# Resize to 1280×720 to reduce load time
cd hero-A-frames
for file in *.jpg; do ffmpeg -i "$file" -vf scale=1280:720 "optimized_$file"; done
```
> **Note:** If this loop syntax fails on Windows CMD, use PowerShell or skip resizing — 1920×1080 will still work, just slightly slower to load. Prioritize working over optimizing.

**Output:** 3 folders of numbered JPEGs → `/onggi-cafe/animations/hero-A-frames/`, etc.

---

**⚠️ Troubleshooting — FFmpeg JPEG Extraction:**

| Problem | Fix |
|---|---|
| `ffmpeg: command not found` | Not installed or not in PATH — reinstall following steps above |
| Frames are blurry | Increase quality: change `-q:v 2` to `-q:v 1` |
| Too many frames (>200) | Reduce FPS: change `fps=24` to `fps=15` — still smooth enough |
| Folder is empty after command | Check that the MP4 path is correct; use `ls` (Mac) or `dir` (Windows) to confirm |
| Files named incorrectly | The `%04d` pattern is correct — if files are named differently, they will still work |

---

### Step 2.3 — Select Primary Hero Sequence + Organize File Structure
**Time:** 20 minutes

**Select your primary hero sequence:**
- Open all three frame folders in Finder/File Explorer
- Preview `frame_0001.jpg`, `frame_0072.jpg` (midpoint), and `frame_0144.jpg` (end) for each sequence
- Choose the sequence where:
  - ✅ The motion