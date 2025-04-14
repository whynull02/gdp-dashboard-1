import streamlit as st
from datetime import datetime
import json, requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from threading import Thread
from pathlib import Path
import time, socket
import threading

# 페이지 설정
st.set_page_config(
    page_title='간단한 게시판',
    page_icon='📝'
)

# API 설정
API_PORT = 8000
API_BASE_URL = f"http://localhost:{API_PORT}"
server_started = False

# 포트 사용 가능 여부 확인 함수
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# FastAPI 앱 설정
api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# JSON 파일 경로 설정
POSTS_FILE = Path(__file__).parent / 'data/posts.json'

def load_posts():
    if not POSTS_FILE.exists():
        return {"posts": []}
    return json.loads(POSTS_FILE.read_text(encoding='utf-8'))

def save_posts(posts_data):
    POSTS_FILE.parent.mkdir(exist_ok=True)
    POSTS_FILE.write_text(json.dumps(posts_data, ensure_ascii=False, indent=4), encoding='utf-8')

# FastAPI 라우트
@api.get("/api/posts")
async def get_posts():
    return load_posts()

@api.get("/api/posts/{date}")
async def get_posts_by_date(date: str):
    posts = load_posts()
    filtered_posts = {
        "posts": [post for post in posts["posts"] if post["date"] == date]
    }
    return filtered_posts

# API 서버 시작 함수 수정
def start_api_server():
    global server_started
    if not server_started:
        try:
            # 외부 접속을 위한 host 설정
            uvicorn.run(api, host="0.0.0.0", port=API_PORT, log_level="error")
            server_started = True
        except Exception as e:
            st.error(f"API 서버 시작 실패: {str(e)}")

# API 서버 상태 확인
def check_api_server():
    try:
        response = requests.get(f"{API_BASE_URL}/api/posts")
        return response.status_code == 200
    except:
        return False

# API 서버 시작
if not check_api_server():
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    # 서버 시작 대기
    for _ in range(5):
        if check_api_server():
            break
        time.sleep(1)

# Streamlit 앱 코드
posts_data = load_posts()

# 헤더 섹션 수정
st.title('📝 간단한 게시판')

# 네비게이션 추가
st.sidebar.title('메뉴')
page = st.sidebar.radio('페이지 선택', ['게시판', 'JSON 데이터'])

if page == '게시판':
    # 기존 게시판 코드
    st.header('새 게시물 작성', divider='gray')
    with st.form("new_post"):
        title = st.text_input("제목")
        content = st.text_area("내용")
        submitted = st.form_submit_button("게시물 작성")
        
        if submitted and title and content:
            new_id = len(posts_data["posts"]) + 1
            posts_data["posts"].append({
                "id": new_id,
                "title": title,
                "content": content,
                "date": datetime.now().strftime("%Y-%m-%d")
            })
            save_posts(posts_data)
            st.success("게시물이 작성되었습니다!")
            st.rerun()

    # 게시물 목록
    st.header('게시물 목록', divider='gray')
    for post in reversed(posts_data["posts"]):
        with st.expander(f"#{post['id']} {post['title']} ({post['date']})"):
            st.write(post['content'])
else:
    st.header('🔍 API 문서', divider='gray')
    
    # API URL 설정 추가
    col1, col2 = st.columns([3, 1])
    with col1:
        server_ip = st.text_input("서버 IP 주소", "localhost")
        API_BASE_URL = f"http://{server_ip}:8000"
    with col2:
        st.markdown("### 서버 상태")
        try:
            response = requests.get(f"{API_BASE_URL}/api/posts")
            st.success("연결됨")
        except:
            st.error("연결 안됨")
    
    # API 테스트 섹션
    st.header("API 테스트", divider="gray")
    test_tabs = st.tabs(["GET", "POST", "PUT", "DELETE"])
    
    with test_tabs[0]:
        st.markdown("### GET 테스트")
        col1, col2 = st.columns([3, 1])
        with col1:
            get_url = f"{API_BASE_URL}/api/posts"
            st.code(get_url)
            st.markdown("""
            외부 접속 방법:
            ```bash
            curl -X GET {get_url}
            ```
            """)
        with col2:
            if st.button("GET 테스트", key="get_test"):
                try:
                    response = requests.get(get_url, timeout=5)
                    if response.status_code == 200:
                        st.success("성공!")
                        st.json(response.json())
                    else:
                        st.error(f"API 오류: {response.status_code}")
                except requests.RequestException as e:
                    st.error(f"API 서버 연결 실패: {str(e)}")
    
    with test_tabs[1]:
        st.markdown("### POST 테스트")
        with st.form("post_test"):
            test_title = st.text_input("제목")
            test_content = st.text_area("내용")
            if st.form_submit_button("POST 테스트"):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/posts",
                        json={"title": test_title, "content": test_content}
                    )
                    st.json(response.json())
                except:
                    st.error("API 서버 연결 실패")
    
    with test_tabs[2]:
        st.markdown("### PUT 테스트")
        with st.form("put_test"):
            post_id = st.number_input("게시물 ID", min_value=1, step=1)
            test_title = st.text_input("새 제목")
            test_content = st.text_area("새 내용")
            if st.form_submit_button("PUT 테스트"):
                try:
                    response = requests.put(
                        f"{API_BASE_URL}/api/posts/{post_id}",
                        json={"title": test_title, "content": test_content}
                    )
                    st.json(response.json())
                except:
                    st.error("API 서버 연결 실패")
    
    with test_tabs[3]:
        st.markdown("### DELETE 테스트")
        col1, col2 = st.columns([3, 1])
        with col1:
            delete_id = st.number_input("삭제할 게시물 ID", min_value=1, step=1)
        with col2:
            if st.button("DELETE 테스트"):
                try:
                    response = requests.delete(f"{API_BASE_URL}/api/posts/{delete_id}")
                    st.success("게시물이 삭제되었습니다")
                except:
                    st.error("API 서버 연결 실패")
    
    # 기존 API 문서 표시
    st.header("API 문서", divider="gray")
    
    st.markdown("""
    ### REST API 엔드포인트 문서

    #### 1. 게시물 조회 API
    1) 전체 게시물 목록
    ```http
    GET /api/posts
    ```
    
    2) 특정 게시물 조회
    ```http
    GET /api/posts/{post_id}
    ```

    #### 2. 게시물 생성 API
    ```http
    POST /api/posts
    Content-Type: application/json

    {
        "title": "게시물 제목",
        "content": "게시물 내용"
    }
    ```

    #### 3. 게시물 수정 API
    ```http
    PUT /api/posts/{post_id}
    Content-Type: application/json

    {
        "title": "수정된 제목",
        "content": "수정된 내용"
    }
    ```

    #### 4. 게시물 삭제 API
    ```http
    DELETE /api/posts/{post_id}
    ```

    ### 코드 예시

    #### Python
    ```python
    import requests

    # 전체 게시물 조회
    response = requests.get(f"{API_BASE_URL}/api/posts")
    posts = response.json()

    # 특정 게시물 조회
    post_id = 1
    response = requests.get(f"{API_BASE_URL}/api/posts/{post_id}")
    post = response.json()

    # 새 게시물 작성
    new_post = {
        "title": "새 게시물",
        "content": "내용입니다"
    }
    response = requests.post(f"{API_BASE_URL}/api/posts", json=new_post)

    # 게시물 수정
    update_data = {
        "title": "수정된 제목",
        "content": "수정된 내용"
    }
    response = requests.put(f"{API_BASE_URL}/api/posts/{post_id}", json=update_data)

    # 게시물 삭제
    response = requests.delete(f"{API_BASE_URL}/api/posts/{post_id}")
    ```

    #### JavaScript/Fetch
    ```javascript
    const API_BASE_URL = 'http://localhost:8000';

    // 전체 게시물 조회
    fetch(`${API_BASE_URL}/api/posts`)
        .then(res => res.json())
        .then(data => console.log(data));

    // 새 게시물 작성
    fetch(`${API_BASE_URL}/api/posts`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            title: "새 게시물",
            content: "내용입니다"
        })
    });

    // 게시물 수정
    fetch(`${API_BASE_URL}/api/posts/1`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            title: "수정된 제목",
            content: "수정된 내용"
        })
    });

    // 게시물 삭제
    fetch(`${API_BASE_URL}/api/posts/1`, {
        method: 'DELETE'
    });
    ```

    ### API 응답 형식
    ```json
    {
        "id": 1,
        "title": "게시물 제목",
        "content": "게시물 내용",
        "date": "2024-01-01"
    }
    ```
    """)
    
    try:
        # JSON 데이터 표시 옵션
        view_option = st.radio(
            "데이터 표시 방식",
            ["데이터 테이블", "Raw JSON"]
        )
        
        if view_option == "데이터 테이블":
            st.dataframe(posts_data['posts'])
        else:
            st.json(posts_data)
        
        # JSON 다운로드 버튼
        st.download_button(
            label="JSON 파일 다운로드",
            data=json.dumps(posts_data, ensure_ascii=False, indent=4),
            file_name="posts.json",
            mime="application/json"
        )

    except json.JSONDecodeError:
        st.error("JSON 파일 형식이 올바르지 않습니다.")

# API 문서에 외부 접속 정보 추가
st.info("""
### 외부 접속 정보
- API 서버: `http://<서버IP>:8000/api/posts`
- API 문서: `http://<서버IP>:8000/docs`
- ReDoc 문서: `http://<서버IP>:8000/redoc`

주의: <서버IP>는 실제 서버의 IP 주소로 변경하세요.
""")
