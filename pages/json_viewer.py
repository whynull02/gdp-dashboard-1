import streamlit as st
import json
from pathlib import Path

# 페이지 설정
st.set_page_config(page_title='JSON Data', page_icon='📊', layout='wide')

# JSON 파일 경로
POSTS_FILE = Path(__file__).parent.parent / 'data/posts.json'

try:
    # JSON 데이터 로드
    json_data = json.loads(POSTS_FILE.read_text(encoding='utf-8'))
    
    # raw 파라미터 확인
    params = st.query_params
    if "raw" in params and params["raw"] == "true":
        # 순수 JSON 데이터만 반환
        st.write(json_data)
        st.stop()
    
    # 일반 뷰어 페이지 표시
    st.title("📊 JSON 데이터 API")
    st.info("""
    ## 외부에서 데이터 접근하기
    
    ### 1. 배포된 서버 접속 URL
    ```
    https://gdp-dashboard-6l4nu6gox2c.streamlit.app/json_viewer?raw=true
    ```
    
    ### 2. 로컬 개발 환경 URL
    ```
    http://localhost:8501/json_viewer?raw=true
    ```
    
    ### Python 사용 예시:
    ```python
    import requests
    
    # 배포 서버 접속
    url = "https://gdp-dashboard-6l4nu6gox2c.streamlit.app/json_viewer?raw=true"
    response = requests.get(url)
    data = response.json()
    
    # 로컬 서버 접속
    local_url = "http://localhost:8501/json_viewer?raw=true"
    response = requests.get(local_url)
    data = response.json()
    ```
    
    ### curl 사용 예시:
    ```bash
    # 배포 서버 접속
    curl -X GET "https://gdp-dashboard-6l4nu6gox2c.streamlit.app/json_viewer?raw=true"
    
    # 로컬 서버 접속
    curl -X GET "http://localhost:8501/json_viewer?raw=true"
    ```
    """)

    # JSON 데이터 표시 옵션
    st.header("데이터 미리보기", divider="gray")
    view_option = st.radio(
        "보기 방식 선택",
        ["테이블 형식", "JSON 형식"]
    )
    
    if view_option == "테이블 형식":
        st.dataframe(
            json_data['posts'],
            use_container_width=True,
            column_config={
                "title": "제목",
                "content": "내용",
                "date": "작성일"
            }
        )
    else:
        st.json(json_data)
    
    # 데이터 다운로드 버튼
    st.download_button(
        label="JSON 파일 다운로드",
        data=json.dumps(json_data, ensure_ascii=False, indent=2),
        file_name="posts.json",
        mime="application/json"
    )

except FileNotFoundError:
    st.error("데이터 파일을 찾을 수 없습니다.")
except json.JSONDecodeError:
    st.error("JSON 파일 형식이 올바르지 않습니다.")
