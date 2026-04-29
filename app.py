import streamlit as st
from datetime import datetime

# 1. 페이지 설정 (최상단에 위치)
st.set_page_config(page_title="부대 기상 브리핑", layout="centered")

# 2. 스타일 정의 (CSS)
st.markdown("""
    <style>
    .main { background-color: #f0f2f5; }
    .stButton>button { 
        width: 100%; 
        border-radius: 50px; 
        background: linear-gradient(135deg, #1a3a5c 0%, #2563a8 100%); 
        color: white; 
        font-weight: 600;
        height: 3em;
        border: none;
        box-shadow: 0 4px 14px rgba(37,99,168,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 상단 헤더 (HTML 카드 형태)
st.markdown("""
<div style="background:linear-gradient(135deg,#1a3a5c 0%,#2563a8 100%); color:white; border-radius:12px; padding:20px; margin-bottom:20px; text-align:center;">
    <h2 style="margin:0;">🌤️ 안전사고 예방 기상 브리핑</h2>
    <p style="margin:5px 0 0 0; opacity:0.8; font-size:14px;">실시간 기상 분석 및 사고 예방 조치사항</p>
</div>
""", unsafe_allow_html=True)

# 4. 지역 선택 데이터
REGION_DATA = {
    "서울특별시": ["강남구", "서초구", "송파구"],
    "대전광역시": ["유성구", "서구", "중구", "동구"]
}

col1, col2 = st.columns(2)
with col1:
    sido = st.selectbox("지역(시/도)", list(REGION_DATA.keys()))
with col2:
    sigungu = st.selectbox("시/군/구", REGION_DATA[sido])

# 5. 브리핑 생성 버튼 및 출력 로직
if st.button("🚀 브리핑 생성"):
    # 현재 날짜 및 시간
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 출력할 HTML 브리핑 내용 (변수로 저장)
    # 반드시 unsafe_allow_html=True를 사용해 렌더링해야 함
    briefing_html = f"""
    <div style="font-family:sans-serif;">
        <h3 style="color:#1a3a5c; margin-bottom:15px;">📍 {sido} {sigungu} 기상 브리핑</h3>
        
        <div style="background:white; padding:15px; border-radius:10px; margin-bottom:12px; border-left:5px solid #E67E22; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <h4 style="margin:0 0 10px 0; color:#333;">[8] 화재 및 산불 위험도</h4>
            <div style="display:flex; align-items:center;">
                <span style="font-size:24px; margin-right:10px;">🔥</span> 
                <b style="color:#E67E22; font-size:18px;">높음</b>
            </div>
            <p style="font-size:13px; color:#666; margin: 8px 0 0 0;"><b>조치:</b> 실외 흡연 및 화기 사용 시 지정된 장소 이용 엄수</p>
        </div>

        <div style="background:white; padding:15px; border-radius:10px; border:2px solid #e53e3e; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <h4 style="margin:0 0 10px 0; color:#c53030;">[9] 지휘관 사고 예방 조치사항</h4>
            <ul style="padding-left:20px; font-size:13px; margin:0; color:#444; line-height:1.6;">
                <li style="margin-bottom:8px;">유동병력 온열질환 예방활동 강화 및 수분 섭취 권장</li>
                <li style="margin-bottom:8px;">야외 교육훈련 시 휴식시간 정기적 부여 (15분 이상)</li>
                <li style="margin-bottom:8px;">특이 기상 발생 시 즉시 보고 체계 유지 및 상황 전파</li>
            </ul>
        </div>

        <p style="text-align:right; font-size:11px; color:#999; margin-top:15px;">
            생성일시: {now_str}
        </p>
    </div>
    """
    
    # 핵심 수정 사항: HTML 렌더링 허용
    st.markdown(briefing_html, unsafe_allow_html=True)