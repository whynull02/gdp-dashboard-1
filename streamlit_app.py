import streamlit as st
from datetime import datetime
import json, requests
import subprocess, time, atexit
from pathlib import Path

# 페이지 설정 (반드시 첫 번째 Streamlit 명령어여야 함)
st.set_page_config(
    page_title='간단한 게시판',
    page_icon='📝'
)

# Flask API URL 설정
API_URL = "http://localhost:5000"

# Flask 서버 관리
@st.cache_resource
def start_flask_server():
    """Flask 서버를 백그라운드로 실행"""
    try:
        requests.get(f"{API_URL}/api/posts")
        return None
    except requests.RequestException:
        process = subprocess.Popen(['python', 'api_server.py'])
        for _ in range(5):
            time.sleep(1)
            try:
                requests.get(f"{API_URL}/api/posts")
                break
            except requests.RequestException:
                continue
        atexit.register(lambda: process.terminate())
        return process

# Flask 서버 시작
flask_process = start_flask_server()

from pathlib import Path

@st.cache_data
def load_posts_from_api():
    try:
        response = requests.get(f"{API_URL}/api/posts")
        return response.json()
    except requests.RequestException:
        st.error("API 서버에 연결할 수 없습니다. Flask 서버가 실행 중인지 확인해주세요.")
        return {"posts": []}

# JSON 파일 경로 설정
POSTS_FILE = Path(__file__).parent / 'data/posts.json'

# JSON 파일 읽기/쓰기 함수
def load_posts():
    if not POSTS_FILE.exists():
        return {"posts": []}
    return json.loads(POSTS_FILE.read_text(encoding='utf-8'))

def save_posts(posts_data):
    POSTS_FILE.parent.mkdir(exist_ok=True)
    POSTS_FILE.write_text(json.dumps(posts_data, ensure_ascii=False, indent=4), encoding='utf-8')

# 게시물 데이터 로드
posts_data = load_posts_from_api()

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
    st.header('🔍 JSON 데이터 뷰어', divider='gray')
    
    # API 정보 표시
    st.info("""
    다음 API 엔드포인트를 통해 데이터에 접근할 수 있습니다:
    - 전체 게시물: http://localhost:5000/api/posts
    - 날짜별 게시물: http://localhost:5000/api/posts/<날짜>
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
