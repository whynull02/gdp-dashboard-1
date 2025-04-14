from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
import json
from datetime import datetime

class Post(BaseModel):
    title: str
    content: str
    date: Optional[str] = None

class PostResponse(Post):
    id: int

class PostList(BaseModel):
    posts: List[PostResponse] = Field(
        description="게시물 목록",
        example=[{
            "id": 1,
            "title": "첫 번째 게시물",
            "content": "내용입니다",
            "date": "2024-01-01"
        }]
    )

# CORS 설정 업데이트
origins = ["*"]  # 모든 오리진 허용

app = FastAPI(
    title="게시판 API",
    description="게시판 데이터를 위한 REST API",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI 활성화
    redoc_url="/redoc"  # ReDoc UI 활성화
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

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

# HTML 템플릿 추가
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>JSON 데이터 뷰어</title>
    <style>
        pre { background: #f4f4f4; padding: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>게시판 API 데이터 뷰어</h1>
    <div id="data"></div>
    <script>
        async function fetchData() {
            try {
                const response = await fetch('/api/posts');
                const data = await response.json();
                document.getElementById('data').innerHTML = `
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
            } catch (error) {
                console.error('Error:', error);
            }
        }
        fetchData();
    </script>
</body>
</html>
"""

# API 엔드포인트
@app.get("/api/posts", response_model=PostList, tags=["posts"])
async def get_posts():
    """
    ### 전체 게시물 목록을 조회합니다.
    
    Returns:
        PostList: 게시물 목록이 담긴 객체
    
    Example:
        ```json
        {
            "posts": [
                {
                    "id": 1,
                    "title": "게시물 제목",
                    "content": "내용",
                    "date": "2024-01-01"
                }
            ]
        }
        ```
    """
    return load_posts()

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

@app.get("/view", response_class=HTMLResponse)
async def view_json():
    """JSON 데이터를 웹 페이지에서 확인할 수 있는 뷰어를 제공합니다."""
    return HTMLResponse(content=HTML_TEMPLATE)

@app.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="게시판 API 문서",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

if __name__ == "__main__":
    import uvicorn
    # Streamlit Share에서 사용할 포트로 변경
    PORT = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        app, 
        host="0.0.0.0",
        port=PORT,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
