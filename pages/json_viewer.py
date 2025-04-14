import streamlit as st
import json
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title='JSON 데이터',
    page_icon='📊',
    layout='wide'
)

# JSON 파일 경로
POSTS_FILE = Path(__file__).parent.parent / 'data/posts.json'

try:
    # JSON 데이터 로드
    json_data = json.loads(POSTS_FILE.read_text(encoding='utf-8'))
    
    # 데이터 표시
    st.json(json_data)
    
except FileNotFoundError:
    st.error("데이터 파일을 찾을 수 없습니다.")
except json.JSONDecodeError:
    st.error("JSON 파일 형식이 올바르지 않습니다.")
