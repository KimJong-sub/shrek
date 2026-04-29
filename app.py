import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from collections import defaultdict, Counter

# 1. 페이지 설정
st.set_page_config(page_title="부대 기상 브리핑 시스템", layout="centered")

# 2. 설정값
API_KEY = "e7eba533bc9a7b9487df4b77093e4332c42aa5bf0eeb316dac315ab39a1b7315"
FORECAST_URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
REALTIME_URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"

REGION_DATA = {
    "서울특별시": { "종로구": (60, 127, ["서울"]), "강남구": (61, 126, ["서울"]) },
    "경기도": { "수원시": (60, 121, ["경기"]), "파주시": (56, 131, ["경기"]), "평택시": (62, 114, ["경기"]) },
    "강원도": { "춘천시": (73, 134, ["강원"]), "철원군": (65, 139, ["강원"]), "강릉시": (92, 131, ["강원"]) },
    "대전광역시": { "서구": (67, 100, ["대전"]), "유성구": (67, 101, ["대전"]) },
    "충청남도": { "천안시": (63, 110, ["충남"]), "계룡시": (65, 99, ["충남"]) },
    "경상북도": { "포항시": (102, 94, ["경북"]), "안동시": (91, 106, ["경북"]) },
    "경상남도": { "창원시": (91, 77, ["경남"]), "진주시": (81, 75, ["경남"]) },
    "전라북도": { "전주시": (63, 89, ["전북"]), "군산시": (56, 92, ["전북"]) },
    "전라남도": { "목포시": (50, 67, ["전남"]), "여수시": (73, 66, ["전남"]) },
    "제주특별자치도": { "제주시": (52, 38, ["제주"]), "서귀포시": (52, 33, ["제주"]) },
}

# 3. 데이터 처리 함수
def get_base_time():
    now = datetime.now()
    base_times = [2, 5, 8, 11, 14, 17, 20, 23]
    hour = now.hour
    adjusted_hour = hour if now.minute >= 15 else hour - 1
    base_hour = max([t for t in base_times if t <= adjusted_hour], default=23)
    if adjusted_hour < 2:
        base_hour = 23
        now = now - timedelta(days=1)
    return now.strftime("%Y%m%d"), f"{base_hour:02d}00"

def call_api(url, params):
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        return data["response"]["body"]["items"]["item"]
    except: return None

def analyze_fire_wildfire_risk(temp, hum, wind):
    try:
        t, h, w = float(temp), float(hum), float(wind)
        risk_score = 0
        if h <= 35: risk_score += 4
        elif h <= 50: risk_score += 2
        if w >= 7: risk_score += 3
        if t >= 25: risk_score += 1
        
        if risk_score >= 6: return "⚠️ 매우높음(산불위험)", "🚨", "#D93025", "유류고/탄약고 주변 감시 강화, 화기작업 금지"
        if risk_score >= 4: return "높음", "🔥", "#E67E22", "실외 흡연 및 화기 사용 주의"
        return "보통/낮음", "✅", "#27AE60", "일상 수칙 준수"
    except: return "산출불가", "", "#999", "-"

def detailed_commander_briefing(pty, wind, temp, hum):
    m = []
    try: w, t, h = float(wind), float(temp), float(hum)
    except: w, t, h = 0, 15, 50
    if t >= 33: m.append("<b>[온열질환]</b> 실외훈련 조정 검토 요망")
    if t <= -5: m.append("<b>[동상예방]</b> 경계병 교대주기 단축 권장")
    if str(pty) in ["1", "4"]: m.append("<b>[수송안전]</b> 비긴급 배차 제한 검토")
    if w >= 10: m.append("<b>[시설점검]</b> 강풍 대비 천막/구조물 결박")
    if h <= 30: m.append("<b>[산불경계]</b> 산림 인접지 방화선 점검")
    if not m: m = ["특이 기상 위험 없음. 안전수칙 준수"]
    return m

# 4. 메인 UI 구성
st.title("🚀 부대 기상 및 안전 브리핑")
st.write("지역별 실시간 날씨와 지휘관 조치사항을 확인하세요.")

col1, col2 = st.columns(2)
with col1:
    sido = st.selectbox("시/도 선택", list(REGION_DATA.keys()))
with col2:
    sigungu = st.selectbox("시/군/구 선택", list(REGION_DATA[sido].keys()))

if st.button("브리핑 생성", use_container_width=True):
    with st.spinner("기상청 데이터를 분석 중입니다..."):
        nx, ny, _ = REGION_DATA[sido][sigungu]
        today = datetime.now()
        base_date, base_time = get_base_time()

        now_items = call_api(REALTIME_URL, {
            "serviceKey": API_KEY, "numOfRows": 50, "dataType": "JSON",
            "base_date": today.strftime("%Y%m%d"), "base_time": today.strftime("%H")+"00",
            "nx": nx, "ny": ny
        })

        if now_items:
            now_data = {it["category"]: it["obsrValue"] for it in now_items}
            t, h, w, p = now_data.get("T1H", "15"), now_data.get("REH", "50"), now_data.get("WSD", "0"), now_data.get("PTY", "0")
            
            f_level, f_icon, f_color, f_action = analyze_fire_wildfire_risk(t, h, w)
            briefs = detailed_commander_briefing(p, w, t, h)

            # 결과 화면 출력 (HTML 기반)
            html_ui = f"""
            <div style="background:#f1f3f5; padding:15px; border-radius:15px; font-family: sans-serif;">
                <div style="background:#1e3a5f; color:white; padding:15px; border-radius:10px; margin-bottom:15px;">
                    <h3 style="margin:0;">{sido} {sigungu} 기상실황</h3>
                    <p style="font-size:12px; margin:5px 0 0 0;">{today.strftime('%Y-%m-%d %H:%M')} 기준</p>
                </div>
                
                <div style="background:white; padding:15px; border-radius:10px; margin-bottom:10px; border-left:5px solid {f_color};">
                    <h4 style="margin:0 0 10px 0;">[8] 화재 및 산불 위험도</h4>
                    <span style="font-size:24px;">{f_icon}</span> <b style="color:{f_color}; font-size:18px;">{f_level}</b>
                    <p style="font-size:13px; color:#666;">조치: {f_action}</p>
                </div>

                <div style="background:white; padding:15px; border-radius:10px; border:2px solid #e53e3e;">
                    <h4 style="margin:0 0 10px 0; color:#c53030;">[9] 지휘관 사고 예방 조치사항</h4>
                    <ul style="padding-left:20px; font-size:13px; margin:0;">
                        {"".join([f'<li style="margin-bottom:8px;">{b}</li>' for b in briefs])}
                    </ul>
                </div>
            </div>
            """
            st.markdown(html_ui, unsafe_allow_html=True)
        else:
            st.error("기상청 API 정보를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.")

st.divider()
st.caption("군수사령부 5급 김종섭 | 기상청 공공데이터 활용")