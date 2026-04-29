import streamlit as st
import requests
from datetime import datetime

# 페이지 설정 (핸드폰에서 보기 좋게 넓이 조정)
st.set_page_config(page_title="부대 기상 브리핑", layout="centered")

# --- 여기에 기존에 작성하신 REGION_DATA, call_api, analyze_fire_risk 등 함수를 복사해 넣으세요 ---

st.title("🌤️ 부대 안전 기상 브리핑")

# 1. 사이드바 또는 메인 화면에 지역 선택 UI 구성
sido = st.selectbox("지역 선택", list(REGION_DATA.keys()))
sigungu = st.selectbox("시/군/구 선택", list(REGION_DATA[sido].keys()))

if st.button("날씨 조회하기"):
    # 2. 기존 fetch_and_render 함수 로직 실행
    nx, ny, kw = REGION_DATA[sido][sigungu]
    
    # 결과 데이터를 st.markdown()을 사용하여 HTML로 출력
    # (앞서 만든 HTML 코드를 그대로 사용하되 display(HTML(...)) 대신 st.markdown(..., unsafe_allow_html=True) 사용)
    st.markdown(html_code, unsafe_allow_html=True)