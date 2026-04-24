"""
Layer 3: 해외 AI YouTube 영상 다운로드 (yt-dlp)
Local /loop 전용 — 원본 롱폼 저장
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[4]
RENDERS_DIR = BASE_DIR / "channels" / "first-mover-ai" / "renders"


def download_video(url: str, output_dir: Path = None, max_duration: int = 1800) -> dict:
    try:
        import yt_dlp
    except ImportError:
        return {"status": "error", "error": "yt-dlp 미설치"}

    if output_dir is None:
        output_dir = RENDERS_DIR / "originals"
    output_dir.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        "outtmpl": str(output_dir / "%(id)s.%(ext)s"),
        "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "merge_output_format": "mp4",
        "quiet": False,
        "match_filter": yt_dlp.utils.match_filter_func(f"duration <= {max_duration}"),
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en", "en-US"],
        "subtitlesformat": "srt",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            vid = info.get("id")
            matches = list(output_dir.glob(f"{vid}.*"))
            video_path = next((str(p) for p in matches if p.suffix == ".mp4"), None)
            return {
                "status": "ok",
                "video_id": vid,
                "video_path": video_path,
                "title": info.get("title"),
                "duration": info.get("duration"),
                "uploader": info.get("uploader"),
                "subtitle_files": [str(p) for p in matches if p.suffix in (".srt", ".vtt")],
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python downloader.py <youtube_url>")
        sys.exit(1)
    result = download_video(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
