"""
Channel crawler: fetch all video IDs from a YouTube channel,
pull transcripts via MCP, then run Claude extraction on a topic.

Usage:
    python channel_crawler.py @nateherk --limit=20 --topic="ClickUp"
    python channel_crawler.py UC2ojq-nuP8ceeHqiroeKhBA --limit=50
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
TRANSCRIPT_DIR = BASE_DIR / "data" / "transcripts"


def fetch_video_ids(channel: str, limit: int = 20) -> list[dict]:
    try:
        import yt_dlp
    except ImportError:
        print("[ERROR] yt-dlp not installed. Run: pip install yt-dlp")
        sys.exit(1)

    # Normalize: handle @handle, /c/name, or raw channel ID
    if channel.startswith("UC"):
        url = f"https://www.youtube.com/channel/{channel}/videos"
    elif channel.startswith("@"):
        url = f"https://www.youtube.com/{channel}/videos"
    else:
        url = f"https://www.youtube.com/@{channel}/videos"

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "playlistend": limit,
    }

    videos = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info or "entries" not in info:
                print(f"[WARN] No entries found for {channel}")
                return []
            for entry in info["entries"][:limit]:
                if not entry or not entry.get("id"):
                    continue
                videos.append({
                    "id": entry["id"],
                    "url": f"https://www.youtube.com/watch?v={entry['id']}",
                    "title": entry.get("title", ""),
                    "duration": entry.get("duration") or 0,
                    "view_count": entry.get("view_count") or 0,
                    "upload_date": entry.get("upload_date", ""),
                })
    except Exception as e:
        print(f"[ERROR] Failed to list channel videos: {e}")

    return videos


def fetch_transcript_mcp(video_id: str) -> str | None:
    """
    Calls the youtube-transcript MCP tool.
    In Claude Code sessions this is available as mcp__youtube-transcript__get_transcript.
    Outside a session, falls back to youtube-transcript Python package.
    """
    # Try Python package fallback (works outside Claude Code)
    # v1.x uses instance-based API: YouTubeTranscriptApi().fetch(video_id)
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=["en", "en-US"])
        return " ".join(s.text for s in transcript)
    except Exception:
        pass

    # MCP path: not callable directly from Python — caller must use Claude Code session
    return None


def save_transcript(channel_dir: Path, video: dict, transcript: str) -> Path:
    channel_dir.mkdir(parents=True, exist_ok=True)
    date_prefix = video.get("upload_date", datetime.now().strftime("%Y%m%d"))
    safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in video["title"])[:60].strip()
    filename = f"{date_prefix}-{video['id']}-{safe_title}.json"
    path = channel_dir / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "id": video["id"],
            "url": video["url"],
            "title": video["title"],
            "duration": video["duration"],
            "view_count": video["view_count"],
            "upload_date": video.get("upload_date", ""),
            "transcript": transcript,
            "crawled_at": datetime.now(timezone.utc).isoformat(),
        }, f, ensure_ascii=False, indent=2)
    return path


def extract_topic_insights(channel_dir: Path, topic: str, channel_handle: str) -> Path:
    """
    Reads all saved transcripts, concatenates them, and calls Claude Sonnet
    to extract structured insights about the given topic.
    """
    try:
        import anthropic
    except ImportError:
        print("[WARN] anthropic not installed — skipping extraction pass")
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[WARN] ANTHROPIC_API_KEY not set - skipping extraction pass")
        return None

    # Load all transcripts
    transcripts = []
    for path in sorted(channel_dir.glob("*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("transcript"):
                transcripts.append(f"### {data['title']}\n{data['transcript']}\n")
        except Exception:
            continue

    if not transcripts:
        print("[WARN] No transcripts found to extract from")
        return None

    combined = "\n\n".join(transcripts)
    # Truncate to ~100k chars to stay within context
    if len(combined) > 100_000:
        combined = combined[:100_000] + "\n\n[TRUNCATED]"

    prompt = f"""You are analyzing YouTube transcripts from {channel_handle} to extract everything about: {topic}

From the transcripts below, extract and structure ALL mentions of {topic} into these sections:

## 1. System / Workspace Structure
- How they organize their {topic} workspace (spaces, folders, lists)
- Naming conventions they use

## 2. Automations & Workflows
- Specific automations they've set up
- Trigger → action patterns they recommend

## 3. Templates
- Any templates they use or recommend (with field names if mentioned)

## 4. Integrations
- What other tools they connect to {topic} (Zapier, Slack, Notion, etc.)

## 5. Tips & Best Practices
- Specific advice, mistakes to avoid, pro tips

## 6. Content Ideas for First Mover AI
- Which of these workflows/insights would make good YouTube Shorts or long-form videos?
- Frame each as a potential video title

Be specific. Quote exact terms they use. If something is mentioned multiple times, note the frequency.

---

TRANSCRIPTS:

{combined}"""

    client = anthropic.Anthropic(api_key=api_key)
    print(f"[Extract] Running Claude Sonnet extraction on {len(transcripts)} transcripts...")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    output = response.content[0].text
    out_path = channel_dir / f"{topic.lower().replace(' ', '-')}-system-extract.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# {topic} System Extract — {channel_handle}\n")
        f.write(f"_Generated: {datetime.now().strftime('%Y-%m-%d')}_\n")
        f.write(f"_Source videos: {len(transcripts)}_\n\n")
        f.write(output)

    print(f"[Extract] Saved → {out_path}")
    return out_path


def run(channel: str, limit: int = 20, topic: str = None, skip_existing: bool = True):
    handle = channel.lstrip("@")
    channel_dir = TRANSCRIPT_DIR / handle

    print(f"[Crawl] Fetching up to {limit} videos from {channel}...")
    videos = fetch_video_ids(channel, limit)
    print(f"[Crawl] Found {len(videos)} videos")

    fetched = 0
    skipped = 0
    failed = 0

    for video in videos:
        vid_id = video["id"]
        # Check if already saved
        if skip_existing:
            existing = list(channel_dir.glob(f"*{vid_id}*.json"))
            if existing:
                skipped += 1
                continue

        transcript = fetch_transcript_mcp(vid_id)
        if transcript:
            path = save_transcript(channel_dir, video, transcript)
            print(f"[OK] {video['title'][:60]} → {path.name}")
            fetched += 1
        else:
            print(f"[SKIP] No transcript: {video['title'][:60]}")
            failed += 1

    print(f"\n[Done] Fetched: {fetched} | Skipped (existing): {skipped} | No transcript: {failed}")

    if topic and fetched > 0:
        extract_topic_insights(channel_dir, topic, channel)
    elif topic and skipped > 0:
        # Re-run extraction on existing transcripts
        print(f"[Extract] Running extraction on existing transcripts...")
        extract_topic_insights(channel_dir, topic, channel)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl a YouTube channel and extract topic insights")
    parser.add_argument("channel", help="Channel handle (@nateherk), ID (UC...), or name")
    parser.add_argument("--limit", type=int, default=20, help="Max videos to fetch (default: 20)")
    parser.add_argument("--topic", type=str, default=None, help="Topic to extract insights on (e.g. 'ClickUp')")
    parser.add_argument("--no-skip", action="store_true", help="Re-fetch even if transcript already saved")
    args = parser.parse_args()

    run(
        channel=args.channel,
        limit=args.limit,
        topic=args.topic,
        skip_existing=not args.no_skip,
    )
