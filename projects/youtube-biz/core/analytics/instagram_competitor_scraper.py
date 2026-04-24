"""
Instagram competitor scraper using instagrapi.
Requires INSTAGRAM_USERNAME + INSTAGRAM_PASSWORD in .env (root of repo)
"""
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[4]  # MCP_Agentic_AI/
load_dotenv(REPO_ROOT / ".env")

MEDIA_TYPE_MAP = {1: "image", 8: "carousel"}


def _get_client():
    try:
        from instagrapi import Client
    except ImportError:
        raise RuntimeError("pip install instagrapi")

    username = os.getenv("INSTAGRAM_USERNAME", "")
    password = os.getenv("INSTAGRAM_PASSWORD", "")
    if not username or not password:
        raise ValueError("INSTAGRAM_USERNAME / INSTAGRAM_PASSWORD not set in .env")

    client = Client()
    session_path = REPO_ROOT / f".ig_session_{username}.json"
    if session_path.exists():
        print(f"  Loading saved session for {username}...")
        client.load_settings(str(session_path))
        client.login(username, password)
    else:
        print(f"  Logging in as {username}...")
        client.login(username, password)
    client.dump_settings(str(session_path))
    return client


def _detect_type(media) -> str:
    if media.media_type == 2:
        return "reel" if getattr(media, "product_type", "") == "clips" else "video"
    return MEDIA_TYPE_MAP.get(media.media_type, "image")


def _posts_per_week(posts: list[dict]) -> float | None:
    dated = [p for p in posts if p.get("date")]
    if len(dated) < 2:
        return None
    dates = sorted(dated, key=lambda p: p["date"])
    first = datetime.fromisoformat(dates[0]["date"])
    last = datetime.fromisoformat(dates[-1]["date"])
    span_weeks = max(1, (last - first).days / 7)
    return round(len(dated) / span_weeks, 1)


def scrape_account(client, username: str, n_posts: int = 12) -> dict:
    print(f"\n[{username}] Fetching profile...")
    try:
        user = client.user_info_by_username(username)
    except Exception as e:
        return {"username": username, "error": str(e)}

    print(f"  Followers: {user.follower_count:,} | fetching {n_posts} posts...")
    try:
        medias = client.user_medias(user.pk, amount=n_posts)
    except Exception as e:
        print(f"  Media fetch error: {e}")
        medias = []

    posts = []
    for m in medias:
        post_type = _detect_type(m)
        posts.append({
            "type": post_type,
            "likes": m.like_count,
            "comments": m.comment_count,
            "caption": (m.caption_text or "")[:500],
            "caption_length": len(m.caption_text or ""),
            "date": m.taken_at.isoformat() if m.taken_at else None,
            "url": f"https://www.instagram.com/p/{m.code}/",
        })
        print(f"  {len(posts)}/{n_posts}: {post_type} | likes={m.like_count:,}")

    return {
        "username": username,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "profile": {
            "full_name": user.full_name,
            "followers": user.follower_count,
            "following": user.following_count,
            "post_count": user.media_count,
            "bio": user.biography,
            "link_in_bio": str(user.external_url) if user.external_url else None,
        },
        "posts": posts,
    }


def compute_metrics(data: dict) -> dict:
    posts = data.get("posts", [])
    if not posts:
        return data

    followers = data["profile"].get("followers") or 1
    n = len(posts)
    types = [p["type"] for p in posts]

    avg_likes = sum(p.get("likes") or 0 for p in posts) / n
    avg_comments = sum(p.get("comments") or 0 for p in posts) / n
    avg_engagement = (avg_likes + avg_comments) / followers * 100
    avg_caption_len = sum(p.get("caption_length") or 0 for p in posts) / n
    carousel_ratio = types.count("carousel") / n
    reel_ratio = types.count("reel") / n

    edu, mag = 0, 0
    if avg_caption_len > 300:
        edu += 2
    elif avg_caption_len < 120:
        mag += 2
    else:
        edu += 1; mag += 1

    if carousel_ratio > 0.5:
        edu += 2
    if reel_ratio > 0.6:
        mag += 2

    caption_blob = " ".join(p.get("caption", "") or "" for p in posts).lower()
    edu_kw = ["저장", "save", "따라해", "방법", "how to", "step", "가이드", "알려드"]
    mag_kw = ["트렌드", "trend", "소식", "뉴스", "news", "출시", "공개"]
    edu += sum(1 for kw in edu_kw if kw in caption_blob)
    mag += sum(1 for kw in mag_kw if kw in caption_blob)

    data["metrics"] = {
        "reel_pct": round(reel_ratio * 100, 1),
        "carousel_pct": round(carousel_ratio * 100, 1),
        "image_pct": round(types.count("image") / n * 100, 1),
        "avg_likes": round(avg_likes),
        "avg_comments": round(avg_comments),
        "avg_engagement_rate_pct": round(avg_engagement, 3),
        "avg_caption_length": round(avg_caption_len),
        "posts_per_week": _posts_per_week(posts),
        "posts_analyzed": n,
        "edu_score": edu,
        "mag_score": mag,
        "positioning": "educational" if edu > mag else "magazine" if mag > edu else "mixed",
    }
    return data


def run(usernames: list[str], n_posts: int = 12) -> list[dict]:
    client = _get_client()
    results = []
    for username in usernames:
        data = scrape_account(client, username, n_posts)
        if "error" not in data:
            data = compute_metrics(data)
        results.append(data)
    return results
