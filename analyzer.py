"""Provider-agnostic LLM layer."""
import base64
import json
import os
import re
from datetime import datetime
from typing import List, Optional, Type, TypeVar

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

from schemas import Post, ProfileAnalysis, Recommendation

load_dotenv()

BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
API_KEY = os.getenv("LLM_API_KEY")
MODEL = os.getenv("LLM_MODEL")
USE_VISION = os.getenv("USE_VISION", "true").lower() == "true"
TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))

T = TypeVar("T", bound=BaseModel)


def _post(payload: dict) -> requests.Response:
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    return requests.post(f"{BASE_URL}/chat/completions", headers=headers,
                         json=payload, timeout=TIMEOUT)


def _chat(system: str, content: list) -> str:
    payload = {
        "model": MODEL,
        "temperature": 0.4,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": content},
        ],
        "response_format": {"type": "json_object"},
    }
    r = _post(payload)
    if r.status_code == 400 and "response_format" in r.text:
        payload.pop("response_format")
        r = _post(payload)
    if r.status_code in (401, 403):
        raise RuntimeError("LLM auth failed. Check LLM_API_KEY in .env")
    if r.status_code == 429:
        raise RuntimeError("LLM rate limit hit (free tier). Wait a minute and retry.")
    if r.status_code >= 400:
        raise RuntimeError(f"LLM error {r.status_code}: {r.text[:300]}")
    return r.json()["choices"][0]["message"]["content"]


def _extract_json(text: str) -> str:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    start, end = text.find("{"), text.rfind("}")
    return text[start:end + 1] if start != -1 and end != -1 else text


def _call_json(system: str, content: list, model_cls: Type[T], retries: int = 1) -> T:
    schema = json.dumps(model_cls.model_json_schema())
    system = (f"{system}\n\nReturn ONLY one valid JSON object matching this schema. "
              f"No markdown, no commentary.\nSchema: {schema}")
    last_err = None
    for _ in range(retries + 1):
        text = _chat(system, content)
        try:
            return model_cls.model_validate_json(_extract_json(text))
        except ValidationError as e:
            last_err = e
    raise RuntimeError(f"Model returned invalid JSON: {last_err}")


def _image_part(url: Optional[str]):
    if not (USE_VISION and url):
        return None
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        media = r.headers.get("content-type", "image/jpeg").split(";")[0]
        if media not in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
            media = "image/jpeg"
        b64 = base64.b64encode(r.content).decode()
        return {"type": "image_url", "image_url": {"url": f"data:{media};base64,{b64}"}}
    except Exception:
        return None


def analyze_profile(username: str, posts: List[Post]) -> ProfileAnalysis:
    content, has_images = [], False
    for i, p in enumerate(posts, 1):
        img = _image_part(p.image_url)
        if img:
            content.append(img)
            has_images = True
        content.append({
            "type": "text",
            "text": (f"Post {i} | type={p.type} | likes={p.likes} | comments={p.comments} "
                     f"| posted={p.timestamp}\nCaption: {p.caption}\n"
                     f"Hashtags: {', '.join(p.hashtags)}"),
        })
    content.append({
        "type": "text",
        "text": (f"These are the most recent posts of Instagram account @{username}. "
                 "Analyze their niche, tone, visual style, content pattern, which format "
                 "performs best (use the engagement numbers), top hashtags and recent themes."),
    })
    system = "You are a social media analyst. Base every insight on the evidence given."
    try:
        return _call_json(system, content, ProfileAnalysis)
    except RuntimeError:
        if not has_images:
            raise
        text_only = [c for c in content if c["type"] == "text"]
        return _call_json(system, text_only, ProfileAnalysis)


def recommend(username: str, analysis: ProfileAnalysis, posts: List[Post],
              user_niche: Optional[str] = None) -> Recommendation:
    now = datetime.now()
    text = (
        f"Today is {now:%A, %d %B %Y}.\n"
        f"Inspiration account: @{username}\n"
        f"Their profile analysis: {analysis.model_dump_json()}\n"
        f"Their recent posts (type/likes/comments/time): "
        f"{[(p.type, p.likes, p.comments, p.timestamp) for p in posts]}\n"
        f"User's own niche/brand: {user_niche or 'not specified (assume similar niche)'}\n\n"
        "Recommend what the USER should post TODAY, inspired by the style, themes and "
        "formats that are working for this account. Do NOT copy their posts; give an "
        "original idea in the same spirit. Explain the reason using the engagement "
        "pattern. Never promise guaranteed reach; use 'likely' language."
    )
    system = "You are a content strategist for creators and influencers."
    return _call_json(system, [{"type": "text", "text": text}], Recommendation)