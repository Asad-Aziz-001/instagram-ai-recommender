import os
from typing import List
from urllib.parse import urlparse

from schemas import Post

RESERVED = {"p", "reel", "reels", "explore", "stories", "tv", "accounts"}


def extract_username(url: str) -> str:
    u = urlparse(url.strip())
    if "instagram.com" not in u.netloc:
        raise ValueError("Please provide a valid Instagram profile URL.")
    parts = [p for p in u.path.split("/") if p]
    if not parts or parts[0] in RESERVED:
        raise ValueError("URL must be a profile link, e.g. instagram.com/username/")
    return parts[0]


def _map_type(media_type: int) -> str:
    """instagrapi media_type: 1=photo, 2=video/reel, 8=carousel"""
    if media_type == 2:
        return "video"
    if media_type == 8:
        return "carousel"
    return "photo"


def fetch_posts_instagrapi(username: str, limit: int = 3) -> List[Post]:
    """Fetch last `limit` posts of a PUBLIC profile using instagrapi.
    Requires IG_USERNAME + IG_PASSWORD in .env (use a throwaway account)."""
    from instagrapi import Client

    ig_user = os.getenv("IG_USERNAME")
    ig_pass = os.getenv("IG_PASSWORD")

    if not ig_user or not ig_pass:
        raise ValueError(
            "Instagram login required. Set IG_USERNAME and IG_PASSWORD in .env "
            "(use a throwaway account, never your personal one)."
        )

    cl = Client()

    # Session file se login try karo (fast)
    session_file = f"session-{ig_user}.json"
    if os.path.exists(session_file):
        try:
            cl.load_settings(session_file)
            cl.login(ig_user, ig_pass)
            cl.get_timeline_feed()  # session verify
        except Exception:
            cl = Client()
            cl.login(ig_user, ig_pass)
            cl.dump_settings(session_file)
    else:
        cl.login(ig_user, ig_pass)
        cl.dump_settings(session_file)

    # Profile ka user_id nikaalo
    try:
        user_id = cl.user_id_from_username(username)
    except Exception as e:
        raise ValueError(f"Profile @{username} not found or inaccessible: {e}")

    # Last posts fetch karo
    try:
        medias = cl.user_medias(user_id, amount=limit)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch posts for @{username}: {e}")

    if not medias:
        raise RuntimeError(f"No public posts found for @{username}.")

    posts = []
    for m in medias:
        caption = m.caption_text or ""
        hashtags = [t for t in caption.split() if t.startswith("#")]
        hashtags = [h.lstrip("#") for h in hashtags]

        posts.append(
            Post(
                url=f"https://www.instagram.com/p/{m.code}/",
                type=_map_type(m.media_type),
                caption=caption,
                hashtags=hashtags,
                likes=m.like_count or 0,
                comments=m.comment_count or 0,
                timestamp=str(m.taken_at),
                image_url=str(m.thumbnail_url) if m.thumbnail_url else None,
            )
        )

    posts.sort(key=lambda p: p.timestamp or "", reverse=True)
    return posts[:limit]


def mock_posts() -> List[Post]:
    return [
        Post(
            type="video",
            caption="Morning routine that changed my skin 🌿 Save this for later!",
            hashtags=["skincare", "morningroutine", "glowup"],
            likes=18400,
            comments=612,
            timestamp="2026-10-13T16:10:00Z",
        ),
        Post(
            type="carousel",
            caption="5 mistakes you make while washing your face. Swipe ➡️",
            hashtags=["skincaretips", "facewash", "beautytips"],
            likes=9200,
            comments=240,
            timestamp="2026-10-11T14:30:00Z",
        ),
        Post(
            type="photo",
            caption="Soft light, soft heart ✨",
            hashtags=["aesthetic", "selfcare"],
            likes=5100,
            comments=90,
            timestamp="2026-10-09T18:45:00Z",
        ),
    ]


def fetch_posts(username: str, mock: bool = False, limit: int = 3) -> List[Post]:
    if mock:
        return mock_posts()
    return fetch_posts_instagrapi(username, limit)