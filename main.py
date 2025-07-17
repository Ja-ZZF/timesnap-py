from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
from typing import List

from services.get_posts_by_user_interest_tags import get_recommended_posts
from services.keyword_extractor import extract_keywords
from services.user_interest import calculate_user_interest_tags

app = FastAPI()

class ExtractRequest(BaseModel):
    text: str
    top_k: int = 5

class UserInterestRequest(BaseModel):
    user_id: int
    top_k: int = 10

class RecommendPostsRequest(BaseModel):
    user_id: int
    num_posts: int = 20

@app.post("/extract_keywords")
def get_keywords(req: ExtractRequest):
    keywords = extract_keywords(req.text, req.top_k)
    return {"keywords": keywords}

@app.post("/user_interest_tags")
def get_user_interest_tags(req: UserInterestRequest):
    tags = calculate_user_interest_tags(req.user_id, req.top_k)
    if not tags:
        raise HTTPException(status_code=404, detail="No interest tags found for user")
    return {
        "user_id": req.user_id,
        "interest_tags": [{"tag": tag, "weight": weight} for tag, weight in tags]
    }

@app.post("/recommend_posts")
def recommend_posts(req: RecommendPostsRequest):
    print("Received request:", req)
    posts = get_recommended_posts(req.user_id, req.num_posts)
    if not posts:
        raise HTTPException(status_code=404, detail="No recommended posts found")
    return {"user_id": req.user_id, "recommended_post_ids": posts}
