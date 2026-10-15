from typing import List, Optional
from pydantic import BaseModel, Field


class Post(BaseModel):
    url: Optional[str] = None
    type: str = "photo"  # photo | video | carousel
    caption: str = ""
    hashtags: List[str] = Field(default_factory=list)
    likes: int = 0
    comments: int = 0
    timestamp: Optional[str] = None
    image_url: Optional[str] = None


class ProfileAnalysis(BaseModel):
    niche: str
    tone: str
    visual_style: str
    content_pattern: str
    best_performing_format: str
    top_hashtags: List[str]
    engagement_insight: str
    recent_themes: List[str]

class Recommendation(BaseModel):
    post_idea: str
    format: str = Field(..., description="Must be exactly one of: reel, carousel, photo. Do NOT use 'video'.")
    caption_draft: str
    hashtags: List[str]
    best_time: str = Field(..., description="Human-readable time, e.g. '4:00 PM UTC' or '9:00 PM PKT'")
    reason: str

class RecommendRequest(BaseModel):
    url: str
    user_niche: Optional[str] = None  # optional: the user's own niche/brand
    mock: bool = False  # True = skip scraping, use demo posts


class RecommendResponse(BaseModel):
    username: str
    posts_analyzed: int
    analysis: ProfileAnalysis
    recommendation: Recommendation
