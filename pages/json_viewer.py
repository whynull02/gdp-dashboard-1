import streamlit as st
import json
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title='JSON 데이터 뷰어',
    page_icon='📊',
    layout='wide'
)

# JSON 파일 경로
POSTS_FILE = Path(__file__).parent.parent / 'data/posts.json'

try:
    # JSON 데이터 로드
    json_data = json.loads(POSTS_FILE.read_text(encoding='utf-8'))

    # API 접근 방법 안내
    st.title("📊 JSON 데이터 API")
    st.info("""
    ## 외부에서 JSON 데이터 접근하기

    ### 1. 웹 브라우저에서 직접 접근
    아래 URL을 브라우저에 입력하세요:
    ```
    https://gdp-dashboard-6l4nu6gox2c.streamlit.app/json_viewer?raw=true
    ```

    ### 2. Python으로 데이터 가져오기
    ```python
    import requests
    
    # JSON 데이터 가져오기
    url = 'https://gdp-dashboard-6l4nu6gox2c.streamlit.app/json_viewer?raw=true'
    response = requests.get(url)
    data = response.json()
    
    # 데이터 사용 예시
    for post in data['posts']:
        print(f"제목: {post['title']}")
        print(f"내용: {post['content']}")
        print(f"작성일: {post['date']}")
        print("-" * 50)
    ```
    
    ### JavaScript 사용 예시:
    ```javascript
    fetch('https://gdp-dashboard-6l4nu6gox2c.streamlit.app/json_viewer?raw=true')
        .then(response => response.json())
        .then(data => {
            data.posts.forEach(post => {
                console.log(`제목: ${post.title}`);
                console.log(`내용: ${post.content}`);
                console.log(`작성일: ${post.date}`);
                console.log("-".repeat(50));
            });
        });
    ```
    """)

    # raw=true 파라미터가 있으면 JSON 데이터만 반환
    params = st.query_params
    if params.get("raw") == "true":
        st.json(json_data)
    else:
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
