import json

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from pydantic import ValidationError

load_dotenv()

from analyzer import analyze_profile, recommend  # noqa: E402
from fetcher import extract_username, fetch_posts  # noqa: E402
from schemas import RecommendRequest, RecommendResponse  # noqa: E402

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.post("/recommend")
def recommend_route():
    try:
        req = RecommendRequest.model_validate(request.get_json(force=True))
    except ValidationError as e:
        return jsonify(error=json.loads(e.json())), 400
    except Exception:
        return jsonify(error="Invalid JSON body"), 400

    try:
        username = extract_username(req.url)
        posts = fetch_posts(username, mock=req.mock, limit=3)
        analysis = analyze_profile(username, posts)
        rec = recommend(username, analysis, posts, req.user_niche)
        resp = RecommendResponse(
            username=username,
            posts_analyzed=len(posts),
            analysis=analysis,
            recommendation=rec,
        )
        return jsonify(resp.model_dump())
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except Exception as e:
        return jsonify(error=f"Pipeline failed: {e}"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)