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
import os

# 페이지 설정
st.set_page_config(
    page_title='간단한 게시판',
    page_icon='📝'
)

def find_available_port(start_port=8000, max_port=9000):
    """사용 가능한 포트를 찾습니다."""
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                continue
    return None

# API 설정
STREAMLIT_URL = "gdp-dashboard-6l4nu6gox2c.streamlit.app"
API_BASE_URL = f"https://{STREAMLIT_URL}"
API_PORT = find_available_port() or int(os.getenv("PORT", 8000))
API_HOST = os.getenv("HOST", "0.0.0.0")
server_started = False

# 포트 사용 가능 여부 확인 함수
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# FastAPI 앱 설정
api = FastAPI(
    title="게시판 API",
    description="게시판 데이터를 위한 REST API",
    root_path=os.getenv("ROOT_PATH", "")
)
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
            uvicorn.run(api, host=API_HOST, port=API_PORT, log_level="error")
            server_started = True
        except Exception as e:
            st.error(f"API 서버 시작 실패: {str(e)}")
            return False
    return True

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

# API 설정 수정
@st.cache_data
def get_json_data():
    """JSON 데이터를 직접 반환하는 함수"""
    return load_posts()

# 직접 JSON 데이터 제공을 위한 함수 추가
@st.cache_data
def get_api_data():
    return load_posts()

# 메인 페이지 시작 전에 API 요청 처리
if "api" in st.query_params and st.query_params["api"] == "posts":
    st.json(get_api_data())
    st.stop()

# Streamlit 라우트 추가
if 'api/posts' in st.query_params.get('page', ['']):
    st.write(get_json_data())
    st.stop()

# 헤더 섹션 수정
st.title('📝 간단한 게시판')

# API URL 정보 추가
st.info("""
## 🌐 API 접근 URL
데이터를 JSON 형식으로 받아보실 수 있습니다:

- JSON 뷰어 페이지: `/json_viewer`
- API 엔드포인트: `/api/posts`
```
""")

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
        server_url = st.text_input("서버 URL", STREAMLIT_URL)
        API_BASE_URL = f"https://{server_url}"
        st.info(f"""
        ### 현재 API URL:
        ```
        {API_BASE_URL}/api/posts
        ```
        """)
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
            ### API 테스트 방법
            
            1. 터미널에서 실행:
            ```bash
            # Windows PowerShell
            curl {get_url}
            
            # Linux/Mac Terminal
            curl -X GET {get_url}
            ```
            
            2. Postman에서 테스트:
            - URL 입력: {get_url}
            - Method: GET
            - Send 클릭
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
st.info(f"""
### API 접속 정보
현재 API 서버 URL: `{API_BASE_URL}`

#### API 엔드포인트
- 전체 게시물: `{API_BASE_URL}/api/posts`
- 특정 게시물: `{API_BASE_URL}/api/posts/{{id}}`
- API 문서: `{API_BASE_URL}/docs`

#### 사용 예시 (curl)
```bash
# 전체 게시물 조회
curl {API_BASE_URL}/api/posts

# 새 게시물 작성
curl -X POST {API_BASE_URL}/api/posts \\
     -H "Content-Type: application/json" \\
     -d '{{"title": "제목", "content": "내용"}}'
```
""")
