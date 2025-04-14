from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import json
from datetime import datetime

app = FastAPI(
    title="게시판 API",
    description="게시판 데이터를 위한 REST API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터 모델
class Post(BaseModel):
    title: str
    content: str
    date: Optional[str] = None

class PostResponse(Post):
    id: int

# JSON 파일 경로 설정
POSTS_FILE = Path(__file__).parent / 'data/posts.json'

# 데이터 처리 함수
def load_posts():
    if not POSTS_FILE.exists():
        return {"posts": []}
    return json.loads(POSTS_FILE.read_text(encoding='utf-8'))

def save_posts(posts_data):
    POSTS_FILE.parent.mkdir(exist_ok=True)
    POSTS_FILE.write_text(json.dumps(posts_data, ensure_ascii=False, indent=4), encoding='utf-8')

# API 엔드포인트
@app.get("/api/posts", response_model=List[PostResponse], tags=["posts"])
async def get_posts():
    """모든 게시물을 조회합니다."""
    posts = load_posts()
    return posts["posts"]

@app.get("/api/posts/{post_id}", response_model=PostResponse, tags=["posts"])
async def get_post(post_id: int):
    """특정 ID의 게시물을 조회합니다."""
    posts = load_posts()
    for post in posts["posts"]:
        if post["id"] == post_id:
            return post
    raise HTTPException(status_code=404, detail="게시물을 찾을 수 없습니다")

@app.post("/api/posts", response_model=PostResponse, status_code=201, tags=["posts"])
async def create_post(post: Post):
    """새로운 게시물을 생성합니다."""
    posts = load_posts()
    new_post = post.dict()
    new_post["id"] = len(posts["posts"]) + 1
    new_post["date"] = datetime.now().strftime("%Y-%m-%d")
    posts["posts"].append(new_post)
    save_posts(posts)
    return new_post

@app.put("/api/posts/{post_id}", response_model=PostResponse, tags=["posts"])
async def update_post(post_id: int, post: Post):
    """특정 ID의 게시물을 수정합니다."""
    posts = load_posts()
    for i, existing_post in enumerate(posts["posts"]):
        if existing_post["id"] == post_id:
            updated_post = post.dict()
            updated_post["id"] = post_id
            updated_post["date"] = datetime.now().strftime("%Y-%m-%d")
            posts["posts"][i] = updated_post
            save_posts(posts)
            return updated_post
    raise HTTPException(status_code=404, detail="게시물을 찾을 수 없습니다")

@app.delete("/api/posts/{post_id}", tags=["posts"])
async def delete_post(post_id: int):
    """특정 ID의 게시물을 삭제합니다."""
    posts = load_posts()
    posts["posts"] = [p for p in posts["posts"] if p["id"] != post_id]
    save_posts(posts)
    return {"message": "게시물이 삭제되었습니다"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
