import streamlit as st
import requests
from datetime import datetime
import xml.etree.ElementTree as ET

# 1. 페이지 설정 (모바일 접속 시 최적화)
st.set_page_config(page_title="부대 기상 브리핑", layout="centered")

# 2. 지역 데이터 (예시 데이터 - 필요시 추가하세요)
REGION_DATA = {
    "서울특별시": {"강남구": (61, 126, "1168000000"), "서초구": (61, 125, "1165000000")},
    "대전광역시": {"서구": (67, 100, "3017000000"), "유성구": (67, 101, "3020000000")},
}

# 3. 디자인 스타일 (CSS) - 모바일에서 더 깔끔하게 보이도록 추가
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #2563a8; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 4. 상단 헤더
st.markdown("""
<div style="background:linear-gradient(135deg,#1a3a5c 0%,#2563a8 100%); color:white; border-radius:12px; padding:20px; margin-bottom:20px; text-align:center;">
    <h2 style="margin:0;">🌤️ 안전사고 예방 기상 브리핑</h2>
    <p style="margin:5px 0 0 0; opacity:0.8; font-size:14px;">지휘관 및 당직사관용 실시간 분석 시스템</p>
</div>
""", unsafe_allow_html=True)

# 5. 사용자 입력부
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        sido = st.selectbox("지역(시/도)", list(REGION_DATA.keys()))
    with col2:
        sigungu = st.selectbox("시/군/구", list(REGION_DATA[sido].keys()))

# 6. 브리핑 생성 로직
if st.button("🚀 브리핑 생성"):
    with st.spinner('데이터를 분석 중입니다...'):
        # 실제 API 데이터 기반 변수 설정 (여기에 김종섭님의 기존 분석 로직을 넣으세요)
        # 현재는 예시 데이터로 구성합니다.
        fire_risk = "높음"
        fire_icon = "🔥"
        fire_color = "#E67E22"
        now_time = datetime.now().strftime('%Y-%m-%d %H:%M')

        # --- 핵심: HTML 문자열을 변수에 담기 ---
        briefing_result = f"""
        <div style="background:white; padding:20px; border-radius:15px; border:1px solid #e1e4e8; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="margin-top:0; color:#1a3a5c; border-bottom:2px solid #2563a8; padding-bottom:10px;">📍 {sido} {sigungu} 기상 브리핑</h3>
            
            <div style="background:#fffcf5; padding:15px; border-radius:10px; margin-bottom:15px; border-left:5px solid {fire_color};">
                <h4 style="margin:0 0 8px 0; color:#333;">[8] 화재 및 산불 위험도</h4>
                <div style="display:flex; align-items:center;">
                    <span style="font-size:30px; margin-right:10px;">{fire_icon}</span>
                    <b style="color:{fire_color}; font-size:20px;">{fire_risk}</b>
                </div>
                <p style="font-size:14px; color:#555; margin:8px 0 0 0;"><b>조치:</b> 실외 흡연 및 화기 사용 시 지정된 장소 이용 엄수 및 잔불 점검 철저</p>
            </div>

            <div style="background:#fff5f5; padding:15px; border-radius:10px; border:1px solid #feb2b2;">
                <h4 style="margin:0 0 10px 0; color:#c53030;">[9] 지휘관 사고 예방 조치사항</h4>
                <ul style="padding-left:20px; font-size:14px; margin:0; color:#2d3748; line-height:1.6;">
                    <li>유동병력 온열질환 예방활동 강화 및 수분 섭취 권장</li>
                    <li>야외 교육훈련 시 휴식시간 정기적 부여 (15분 이상)</li>
                    <li>특이 기상 발생 시 즉시 보고 및 전 부대 상황 전파</li>
                </ul>
            </div>
            
            <p style="text-align:right; font-size:12px; color:#a0aec0; margin-top:15px;">
                생성일시: {now_time}
            </p>
        </div>
        """

        # --- 7. 화면에 출력 (이 부분이 가장 중요합니다) ---
        st.markdown(briefing_result, unsafe_allow_html=True)