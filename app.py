import streamlit as st
import requests
from datetime import datetime
import xml.etree.ElementTree as ET

# 1. 페이지 설정 (모바일 최적화)
st.set_page_config(page_title="안전사고 예방 기상 브리핑", layout="centered")

# 2. 지역 데이터 (기존 데이터 유지)
REGION_DATA = {
    "서울특별시": {"강남구": (61, 126, "1168000000"), "서초구": (61, 125, "1165000000"), "종로구": (60, 127, "1111000000")},
    "대전광역시": {"서구": (67, 100, "3017000000"), "유성구": (67, 101, "3020000000")},
    # ... 필요한 지역 데이터를 여기에 추가하세요 ...
}

# 3. 도움말 함수들 (기존 로직 유지)
def get_weather_data(nx, ny):
    # 여기에 기존의 기상청 API 호출 로직을 넣으세요
    # (ServiceKey, URL 등을 포함한 원래의 call_api 함수 내용)
    return {"temp": "25", "sky": "맑음", "rain": "0"} # 예시 데이터

def analyze_fire_risk(temp, humidity):
    # 기존 화재 위험도 분석 로직
    if float(temp) > 20: return "높음", "🔥", "#E67E22"
    return "보통", "✅", "#27AE60"

# 4. UI 구성
st.markdown("""
<div style="font-family:sans-serif;background:linear-gradient(135deg,#1a3a5c 0%,#2563a8 100%);color:#fff;border-radius:12px;padding:14px 18px;margin-bottom:12px;">
    <div style="font-size:19px;font-weight:700;margin-bottom:3px;">🌤️ 안전사고 예방을 위한 기상정보 브리핑</div>
    <div style="font-size:12px;opacity:.75;">지역을 선택하고 브리핑 생성 버튼을 누르세요.</div>
</div>
""", unsafe_allow_html=True)

# 지역 선택 UI
col1, col2 = st.columns(2)
with col1:
    sido = st.selectbox("지역(시/도)", list(REGION_DATA.keys()))
with col2:
    sigungu = st.selectbox("시/군/구", list(REGION_DATA[sido].keys()))

# 브리핑 생성 버튼
if st.button("🚀 브리핑 생성 및 조회", use_container_width=True):
    with st.spinner('기상 데이터를 분석 중입니다...'):
        # 실제 데이터 가져오기
        nx, ny, code = REGION_DATA[sido][sigungu]
        # data = get_weather_data(nx, ny) # 실제 함수 호출 시 주석 해제
        
        # 분석 결과 예시 (기존 로직 결과물들을 여기에 통합)
        fire_risk, fire_icon, fire_color = analyze_fire_risk(25, 30)
        
        # --- HTML 브리핑 화면 구성 (수정된 포인트) ---
        briefing_html = f"""
        <div style="background:#f8f9fa; padding:15px; border-radius:15px; border:1px solid #dee2e6;">
            <h3 style="margin-top:0; color:#1a3a5c;">📍 {sido} {sigungu} 기상 브리핑</h3>
            
            <div style="background:white; padding:15px; border-radius:10px; margin-bottom:10px; border-left:5px solid {fire_color}; shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <h4 style="margin:0 0 10px 0; color:#333;">[8] 화재 및 산불 위험도</h4>
                <span style="font-size:24px;">{fire_icon}</span> 
                <b style="color:{fire_color}; font-size:18px;">{fire_risk}</b>
                <p style="font-size:13px; color:#666; margin: 5px 0 0 0;">조치: 실외 흡연 및 화기 사용 시 지정된 장소 이용 엄수</p>
            </div>

            <div style="background:white; padding:15px; border-radius:10px; border:2px solid #e53e3e;">
                <h4 style="margin:0 0 10px 0; color:#c53030;">[9] 지휘관 사고 예방 조치사항</h4>
                <ul style="padding-left:20px; font-size:13px; margin:0; color:#444;">
                    <li style="margin-bottom:8px;">유동병력 온열질환 예방활동 강화 및 수분 섭취 권장</li>
                    <li style="margin-bottom:8px;">야외 교육훈련 시 휴식시간 정기적 부여 (15분 이상)</li>
                    <li style="margin-bottom:8px;">특이 기상 발생 시 즉시 보고 체계 유지</li>
                </ul>
            </div>
            
            <p style="text-align:right; font-size:11px; color:#999; margin-top:10px;">
                생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            </p>
        </div>
        """
        
        # HTML 렌더링 실행
        st.markdown(briefing_html, unsafe_allow_html=True)