import streamlit as st
import json
from pathlib import Path

# 페이지 설정 (반드시 첫 번째 Streamlit 명령어여야 함)
st.set_page_config(
    page_title='JSON 데이터 뷰어',
    page_icon='🔍'
)

# JSON 파일 경로
POSTS_FILE = Path(__file__).parent.parent / 'data/posts.json'

# 헤더
st.title('🔍 JSON 데이터 뷰어')

# 돌아가기 버튼 추가
if st.sidebar.button('게시판으로 돌아가기'):
    st.switch_page("streamlit_app.py")

# URL 파라미터 처리 수정
params = st.query_params

# JSON 데이터 로드
try:
    json_data = json.loads(POSTS_FILE.read_text(encoding='utf-8'))
    
    # JSON 데이터 표시 옵션
    view_option = st.radio(
        "데이터 표시 방식",
        ["데이터 테이블", "Raw JSON"]
    )
    
    if view_option == "데이터 테이블":
        st.dataframe(json_data['posts'])
    else:
        st.json(json_data)
    
    # JSON 다운로드 버튼
    st.download_button(
        label="JSON 파일 다운로드",
        data=json.dumps(json_data, ensure_ascii=False, indent=4),
        file_name="posts.json",
        mime="application/json"
    )

    # 데이터 공유 섹션 추가
    st.header('데이터 공유', divider='gray')
    st.markdown("""
    ### API 형식으로 데이터 접근하기
    다음 URL을 통해 JSON 데이터에 접근할 수 있습니다:
    ```
    http://localhost:8501/view_json?format=json
    ```
    """)

    # URL 파라미터에 따른 응답 수정
    if 'format' in params and params['format'] == 'json':
        st.write(json_data)
        st.download_button(
            "다운로드",
            json.dumps(json_data, ensure_ascii=False, indent=2),
            "data.json",
            "application/json"
        )

    # 데이터 필터링 옵션
    st.sidebar.header('필터 옵션')
    if st.sidebar.checkbox('날짜별 필터링'):
        dates = [post['date'] for post in json_data['posts']]
        selected_date = st.sidebar.selectbox('날짜 선택', sorted(set(dates)))
        filtered_data = {
            'posts': [post for post in json_data['posts'] if post['date'] == selected_date]
        }
        if view_option == "데이터 테이블":
            st.dataframe(filtered_data['posts'])
        else:
            st.json(filtered_data)

except FileNotFoundError:
    st.error("JSON 파일을 찾을 수 없습니다.")
except json.JSONDecodeError:
    st.error("JSON 파일 형식이 올바르지 않습니다.")
