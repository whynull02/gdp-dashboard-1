import streamlit as st
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title='My Profile',
    page_icon=':smile:', 
)

# 헤더 섹션
st.title('👋 안녕하세요!')
st.subheader('제 개인 웹사이트에 오신 것을 환영합니다')

# 프로필 섹션
col1, col2 = st.columns([1, 2])

with col1:
    st.image('https://via.placeholder.com/200', caption='프로필 사진')

with col2:
    st.markdown("""
    ### 기본 정보
    - 이름: 홍길동
    - 직업: 소프트웨어 엔지니어
    - 위치: 서울, 대한민국
    """)

# 소개 섹션
st.header('자기소개', divider='gray')
st.write("""
저는 웹 개발을 전문으로 하는 소프트웨어 엔지니어입니다.
새로운 기술을 배우고 적용하는 것을 좋아하며, 
특히 사용자 경험을 개선하는 일에 관심이 많습니다.
""")

# 기술 스택
st.header('기술 스택', divider='gray')
cols = st.columns(4)

skills = {
    'Python': 90,
    'JavaScript': 85,
    'HTML/CSS': 80,
    'React': 75
}

for i, (skill, level) in enumerate(skills.items()):
    with cols[i]:
        st.metric(label=skill, value=f'{level}%')

# 연락처
st.header('연락처', divider='gray')
st.markdown("""
- 📧 Email: example@email.com
- 💼 LinkedIn: linkedin.com/in/username
- 📱 GitHub: github.com/username
""")

# 프로젝트 갤러리
st.header('주요 프로젝트', divider='gray')
proj_col1, proj_col2 = st.columns(2)

with proj_col1:
    with st.expander("프로젝트 1", expanded=True):
        st.markdown("""
        웹 애플리케이션 개발 프로젝트입니다.
        - 사용 기술: Python, React
        - 주요 기능: 사용자 인증, 데이터 시각화
        """)

with proj_col2:
    with st.expander("프로젝트 2", expanded=True):
        st.markdown("""
        데이터 분석 프로젝트입니다.
        - 사용 기술: Python, Pandas
        - 주요 기능: 데이터 전처리, 통계 분석
        """)
