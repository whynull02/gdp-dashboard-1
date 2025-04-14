from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
import json

app = Flask(__name__)
CORS(app)  # 모든 도메인에서의 접근 허용

# JSON 파일 경로 설정
POSTS_FILE = Path(__file__).parent / 'data/posts.json'

def load_posts():
    if not POSTS_FILE.exists():
        return {"posts": []}
    return json.loads(POSTS_FILE.read_text(encoding='utf-8'))

def save_posts(posts_data):
    POSTS_FILE.parent.mkdir(exist_ok=True)
    POSTS_FILE.write_text(json.dumps(posts_data, ensure_ascii=False, indent=4), encoding='utf-8')

# 전체 게시물 조회
@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(load_posts())

# 특정 날짜의 게시물 조회
@app.route('/api/posts/<date>', methods=['GET'])
def get_posts_by_date(date):
    posts = load_posts()
    filtered_posts = {
        "posts": [post for post in posts["posts"] if post["date"] == date]
    }
    return jsonify(filtered_posts)

# 새 게시물 작성
@app.route('/api/posts', methods=['POST'])
def create_post():
    posts_data = load_posts()
    new_post = request.json
    new_post["id"] = len(posts_data["posts"]) + 1
    posts_data["posts"].append(new_post)
    save_posts(posts_data)
    return jsonify({"message": "게시물이 작성되었습니다.", "post": new_post}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
