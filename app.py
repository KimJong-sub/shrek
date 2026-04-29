"""
부대 안전사고 예방을 위한 기상정보 브리핑 프로그램
Streamlit 버전 - 작성자: 군수사령부 5급 김종섭
"""

# =========================================================
# 0. import
# =========================================================
import streamlit as st
import streamlit.components.v1 as components
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from collections import defaultdict, Counter

# =========================================================
# 1. 설정
# =========================================================
API_KEY = "e7eba533bc9a7b9487df4b77093e4332c42aa5bf0eeb316dac315ab39a1b7315"
FORECAST_URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
REALTIME_URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"

REGION_DATA = {
    "서울특별시": {
        "종로구": (60, 127, ["서울", "경기"]),
        "중구": (60, 127, ["서울", "경기"]),
        "용산구": (60, 127, ["서울", "경기"]),
        "강남구": (61, 126, ["서울", "경기"]),
        "송파구": (62, 125, ["서울", "경기"]),
    },
    "부산광역시": {
        "중구": (98, 76, ["부산", "경남"]),
        "해운대구": (99, 75, ["부산", "경남"]),
        "남구": (98, 76, ["부산", "경남"]),
        "사하구": (97, 75, ["부산", "경남"]),
    },
    "대구광역시": {
        "중구": (89, 90, ["대구", "경북"]),
        "동구": (90, 91, ["대구", "경북"]),
        "수성구": (89, 90, ["대구", "경북"]),
        "달서구": (88, 89, ["대구", "경북"]),
    },
    "인천광역시": {
        "중구": (55, 124, ["인천", "경기"]),
        "연수구": (55, 123, ["인천", "경기"]),
        "부평구": (56, 125, ["인천", "경기"]),
        "서구": (56, 126, ["인천", "경기"]),
    },
    "광주광역시": {
        "동구": (58, 74, ["광주", "전남"]),
        "서구": (57, 74, ["광주", "전남"]),
        "북구": (58, 75, ["광주", "전남"]),
        "광산구": (57, 73, ["광주", "전남"]),
    },
    "대전광역시": {
        "동구": (67, 100, ["대전", "충청", "세종"]),
        "중구": (67, 100, ["대전", "충청", "세종"]),
        "서구": (67, 100, ["대전", "충청", "세종"]),
        "유성구": (67, 101, ["대전", "충청", "세종"]),
    },
    "울산광역시": {
        "중구": (102, 84, ["울산", "경남"]),
        "남구": (102, 84, ["울산", "경남"]),
        "동구": (103, 83, ["울산", "경남"]),
        "울주군": (102, 84, ["울산", "경남"]),
    },
    "세종특별자치시": {
        "세종시": (66, 103, ["세종", "충청"]),
        "한솔동": (66, 103, ["세종", "충청"]),
    },
    "경기도": {
        "수원시": (60, 121, ["경기"]),
        "성남시": (62, 123, ["경기"]),
        "고양시": (57, 128, ["경기"]),
        "용인시": (62, 120, ["경기"]),
        "평택시": (62, 114, ["경기"]),
    },
    "강원도": {
        "춘천시": (73, 134, ["강원"]),
        "원주시": (76, 122, ["강원"]),
        "강릉시": (92, 131, ["강원"]),
        "속초시": (87, 141, ["강원"]),
    },
    "충청북도": {
        "청주시": (69, 106, ["충청", "충북"]),
        "충주시": (76, 114, ["충청", "충북"]),
        "제천시": (81, 119, ["충청", "충북"]),
    },
    "충청남도": {
        "천안시": (63, 110, ["충청", "충남"]),
        "공주시": (63, 102, ["충청", "충남"]),
        "홍성군": (55, 103, ["충청", "충남"]),
        "아산시": (60, 110, ["충청", "충남"]),
    },
    "전라북도": {
        "전주시": (63, 89, ["전북", "전라"]),
        "군산시": (56, 92, ["전북", "전라"]),
        "익산시": (60, 91, ["전북", "전라"]),
        "남원시": (68, 80, ["전북", "전라"]),
    },
    "전라남도": {
        "목포시": (50, 67, ["전남", "전라"]),
        "여수시": (73, 66, ["전남", "전라"]),
        "순천시": (70, 70, ["전남", "전라"]),
        "나주시": (56, 71, ["전남", "전라"]),
    },
    "경상북도": {
        "포항시": (102, 94, ["경북", "경상"]),
        "경주시": (100, 91, ["경북", "경상"]),
        "구미시": (84, 96, ["경북", "경상"]),
        "안동시": (91, 106, ["경북", "경상"]),
    },
    "경상남도": {
        "창원시": (91, 77, ["경남", "경상"]),
        "진주시": (81, 75, ["경남", "경상"]),
        "통영시": (87, 68, ["경남", "경상"]),
        "김해시": (95, 77, ["경남", "경상"]),
    },
    "제주특별자치도": {
        "제주시": (52, 38, ["제주"]),
        "서귀포시": (52, 33, ["제주"]),
    },
}


# =========================================================
# 2. 공통 함수 (기존 코드 그대로 유지)
# =========================================================
def get_base_time():
    now = datetime.now()
    base_times = [2, 5, 8, 11, 14, 17, 20, 23]
    hour = now.hour
    adjusted_hour = hour if now.minute >= 10 else hour - 1
    base_hour = max([t for t in base_times if t <= adjusted_hour], default=23)
    if adjusted_hour < 2:
        base_hour = 23
        now = now - timedelta(days=1)
    return now.strftime("%Y%m%d"), f"{base_hour:02d}00"


def call_api(url, params):
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data["response"]["header"]["resultCode"] == "00":
            return data["response"]["body"]["items"]["item"]
        return None
    except Exception:
        return None


def safe_float(v, default=None):
    try:
        return float(v)
    except Exception:
        return default


def sky_label(v):
    return {"1": "맑음", "3": "구름많음", "4": "흐림"}.get(str(v), "-")


def pty_label(v):
    return {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기"}.get(str(v), "-")


def wind_dir_label(deg):
    dirs = ["북","북북동","북동","동북동","동","동남동","남동","남남동","남","남남서","남서","서남서","서","서북서","북서","북북서"]
    try:
        return dirs[round(float(deg) / 22.5) % 16] + "풍"
    except Exception:
        return ""


def fire_risk(temp, humidity, wind):
    try:
        t, h, w = float(temp), float(humidity), float(wind)
        score = 0
        if t > 30: score += 3
        elif t > 25: score += 2
        elif t > 15: score += 1
        if h < 20: score += 3
        elif h < 35: score += 2
        elif h < 50: score += 1
        if w > 9: score += 3
        elif w > 5: score += 2
        elif w > 3: score += 1
        if score >= 7: return "매우높음", "화기 취급 전면 금지, 소방시설 즉시 점검"
        if score >= 5: return "높음", "야외 화기 사용 자제, 소화기 비치 확인"
        if score >= 3: return "보통", "일반적 화기 주의 사항 준수"
        return "낮음", "이상 없음"
    except Exception:
        return "산출불가", "-"


def wildfire_risk(temp, humidity, wind, pty, sky):
    try:
        t = safe_float(temp, 15)
        h = safe_float(humidity, 60)
        w = safe_float(wind, 0)
        score = 0
        if t >= 30: score += 3
        elif t >= 25: score += 2
        elif t >= 20: score += 1
        if h <= 20: score += 3
        elif h <= 35: score += 2
        elif h <= 50: score += 1
        if w >= 9: score += 3
        elif w >= 5: score += 2
        elif w >= 3: score += 1
        if str(pty) in ["1", "4"]: score -= 1
        if str(sky) == "4": score -= 1
        score = max(score, 0)
        if score >= 7: return "매우높음", "🚨"
        if score >= 5: return "높음", "⚠️"
        if score >= 3: return "보통", "🟡"
        return "낮음", "🟢"
    except Exception:
        return "산출불가", "—"


def visibility_from_weather(sky, pty, wind):
    w = safe_float(wind, 0)
    if str(pty) in ["1", "4"]: return "🌧️ 약 1~3 km (우천)"
    if str(pty) in ["2", "3"]: return "🌨️ 약 0.5~2 km (눈)"
    if str(sky) == "4" and w > 5: return "🌫️ 약 3~5 km (흐림+강풍)"
    if str(sky) == "4": return "☁️ 약 5~8 km (흐림)"
    if str(sky) == "3": return "⛅ 약 8~15 km (구름많음)"
    return "☀️ 10 km 이상 (양호)"


def accident_measures(region_name, pty, wind, temp, humidity, sky, visibility, fire_level, wildfire_level):
    measures = []
    w = safe_float(wind, 0)
    t = safe_float(temp, 15)

    summary = (
        f"{region_name} 지역의 현재 기상상황을 종합하면 하늘 상태는 '{sky_label(sky)}', "
        f"강수 형태는 '{pty_label(pty)}'이며, 현재 기온은 약 {temp}°C, "
        f"상대습도는 {humidity}%, 풍속은 {wind}m/s 수준입니다.\n "
        f"가시거리는 {visibility}로 판단되며, 이에 따라 차량 운행, 야외훈련, "
        f"장비 운용 및 화재 예방 활동 전반에 대한 선제적 안전통제가 요구됩니다."
    )
    measures.append(summary)

    if str(pty) in ["1", "4"]:
        measures.append(
            "강수로 인해 도로 미끄럼과 시야 저하가 예상되므로 차량 속도 제한과 보행자 안전통제를 실시하고, "
            "야외 훈련은 실내 대체 여부를 검토해야 합니다."
        )
    if str(pty) in ["2", "3"]:
        measures.append(
            "강설 및 결빙 가능성에 대비하여 제설 장비를 사전 점검하고, 차량 이동 시 월동장비 상태를 확인해야 합니다."
        )
    if w >= 7:
        measures.append(
            "강풍으로 인한 낙하물 및 시설물 파손 위험이 있으므로 천막, 이동식 구조물, 경량 장비의 고정 상태를 즉시 점검해야 합니다."
        )
    if t <= 5:
        measures.append(
            "저온 환경에서는 장시간 야외 활동을 최소화하고 방한장비 착용 상태를 확인하여 저체온증을 예방해야 합니다."
        )
    if t >= 30:
        measures.append(
            "고온 환경에서는 온열질환 예방을 위해 수분 보급과 휴식을 강화하고, 장시간 야외 작업을 조정해야 합니다."
        )
    if fire_level in ["높음", "매우높음"]:
        measures.append(
            "화재 위험이 높은 상태이므로 화기 사용을 최소화하고 소화기, 소화전 등 초기 진화 장비를 재점검해야 합니다."
        )
    if wildfire_level in ["높음", "매우높음"]:
        measures.append(
            "산불 위험이 높아 산림 인접 지역의 훈련 및 불씨 취급을 제한하고, 초동 진화 대응태세를 유지해야 합니다."
        )
    if len(measures) == 1:
        measures.append(
            "현재 기상에 따른 특이 위험요소는 없으나, 기본 안전수칙을 유지하고 기상변화 발생 시 재평가가 필요합니다."
        )
    return measures


def get_weather_warning_rss(keywords):
    warn_url = "https://www.weather.go.kr/w/rss/warning.do"
    try:
        resp = requests.get(warn_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml-xml")
        items = []
        for item in soup.find_all("item"):
            title = item.find("title")
            desc = item.find("description")
            pub_date = item.find("pubDate")
            t = title.get_text(strip=True) if title else ""
            d = desc.get_text(strip=True) if desc else ""
            dt = pub_date.get_text(strip=True) if pub_date else ""
            if any(kw in t + d for kw in keywords):
                items.append({"title": t, "desc": d, "date": dt})
        return items
    except Exception:
        return None


# =========================================================
# 3. 렌더링 함수 (display → return html 문자열로 변경)
# =========================================================
def fetch_and_render(region_name, nx, ny, warn_keywords):
    today = datetime.now()
    today_str = today.strftime("%Y%m%d")
    now_hour = today.strftime("%H") + "00"
    base_date, base_time = get_base_time()

    fcst_items = call_api(FORECAST_URL, {
        "serviceKey": API_KEY, "numOfRows": 1000, "pageNo": 1,
        "dataType": "JSON", "base_date": base_date, "base_time": base_time,
        "nx": nx, "ny": ny
    })

    now_items = call_api(REALTIME_URL, {
        "serviceKey": API_KEY, "numOfRows": 100, "pageNo": 1,
        "dataType": "JSON", "base_date": today_str, "base_time": now_hour,
        "nx": nx, "ny": ny
    })

    warn_items = get_weather_warning_rss(warn_keywords)

    now_data = {}
    if now_items:
        for it in now_items:
            now_data[it["category"]] = it["obsrValue"]

    cur_temp = now_data.get("T1H", "N/A")
    cur_hum  = now_data.get("REH", "N/A")
    cur_wind = now_data.get("WSD", "N/A")
    cur_wdir = now_data.get("VEC", "N/A")
    cur_pty  = now_data.get("PTY", "0")

    fcst_by_dt = defaultdict(dict)
    if fcst_items:
        for it in fcst_items:
            key = f"{it['fcstDate']}_{it['fcstTime']}"
            fcst_by_dt[key][it["category"]] = it["fcstValue"]

    daily = defaultdict(lambda: {"TMX": None, "TMN": None, "SKY": [], "PTY": [], "POP": [], "TMP": {}})
    for key, vals in fcst_by_dt.items():
        d = key[:8]
        t = key[9:]
        if "TMX" in vals: daily[d]["TMX"] = vals["TMX"]
        if "TMN" in vals: daily[d]["TMN"] = vals["TMN"]
        if "SKY" in vals: daily[d]["SKY"].append(vals["SKY"])
        if "PTY" in vals: daily[d]["PTY"].append(vals["PTY"])
        if "POP" in vals: daily[d]["POP"].append(int(vals["POP"]))
        if "TMP" in vals: daily[d]["TMP"][t] = vals["TMP"]

    def get_representative_pty(pty_list):
        if not pty_list: return "0"
        for p in ["3", "2", "1", "4"]:
            if p in [str(x) for x in pty_list]: return p
        return "0"

    def day_summary(ds):
        dd = daily.get(ds, {})
        sky = Counter(dd.get("SKY", [])).most_common(1)[0][0] if dd.get("SKY") else "N/A"
        pty = get_representative_pty(dd.get("PTY", []))
        pop = max(dd.get("POP", [])) if dd.get("POP") else "N/A"
        return sky, pty, pop, dd.get("TMX", "N/A"), dd.get("TMN", "N/A")

    today_sky, today_pty, today_pop, today_tmx, today_tmn = day_summary(today_str)
    tomorrow = (today + timedelta(days=1)).strftime("%Y%m%d")
    tmr_sky, tmr_pty, tmr_pop, tmr_tmx, tmr_tmn = day_summary(tomorrow)
    hour_temps = daily.get(today_str, {}).get("TMP", {})

    try:
        chill = f"{float(cur_temp) - float(cur_wind) * 0.7:.1f}°C"
    except Exception:
        chill = "─"

    fire_level, fire_action = fire_risk(cur_temp, cur_hum, cur_wind)
    wildfire_level, wildfire_icon = wildfire_risk(cur_temp, cur_hum, cur_wind, cur_pty, today_sky)
    vis_str = visibility_from_weather(today_sky, cur_pty, cur_wind)

    m_list = accident_measures(
        region_name, cur_pty, cur_wind, cur_temp, cur_hum,
        today_sky, vis_str, fire_level, wildfire_level
    )

    # ----- HTML 헬퍼 -----
    def card(title, body, danger=False):
        head_style = (
            "display:inline-block;font-size:14px;font-weight:800;letter-spacing:.5px;"
            "margin-bottom:12px;background:#A32D2D;color:#fff;padding:4px 12px;border-radius:6px;"
            if danger else
            "font-size:14px;color:#1a3a5c;letter-spacing:.5px;margin-bottom:10px;font-weight:700;"
        )
        return (
            f'<div style="background:#fff;border-radius:12px;border:0.5px solid #ddd;'
            f'padding:14px 16px;margin-bottom:10px;font-family:sans-serif;">'
            f'<div style="{head_style}">{title}</div>{body}</div>'
        )

    def row(label, value, val_style=""):
        return (
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:5px 0;border-bottom:0.5px solid #eee;">'
            f'<span style="font-size:13px;color:#666;">{label}</span>'
            f'<span style="font-size:13px;font-weight:500;color:#111;text-align:right;{val_style}">{value}</span></div>'
        )

    def stat2(l1, v1, s1, l2, v2, s2):
        def box(l, v, s):
            return (
                f'<div style="background:#f7f7f7;border-radius:8px;padding:10px 12px;flex:1;">'
                f'<div style="font-size:11px;color:#888;margin-bottom:4px;">{l}</div>'
                f'<div style="font-size:20px;font-weight:500;color:#111;">{v}</div>'
                f'<div style="font-size:11px;color:#aaa;margin-top:2px;">{s}</div></div>'
            )
        return f'<div style="display:flex;gap:8px;margin-bottom:8px;">{box(l1,v1,s1)}{box(l2,v2,s2)}</div>'

    def fire_badge(level, icon=""):
        color_map = {
            "매우높음": ("background:#FCEBEB;color:#A32D2D;", "매우높음"),
            "높음":    ("background:#FAECE7;color:#993C1D;", "높음"),
            "보통":    ("background:#FAEEDA;color:#854F0B;", "보통"),
            "낮음":    ("background:#EAF3DE;color:#3B6D11;", "낮음"),
            "산출불가": ("background:#eee;color:#333;", "산출불가"),
        }
        st_str, txt = color_map.get(level, ("background:#eee;color:#333;", level))
        if icon: txt = f"{icon} {txt}"
        return f'<span style="display:inline-block;padding:2px 10px;border-radius:20px;font-size:12px;font-weight:500;{st_str}">{txt}</span>'

    def measure_items_html(m_list):
        rows = ""
        for i, m in enumerate(m_list, 1):
            rows += (
                f'<div style="display:flex;gap:8px;padding:8px;background:#fff8f8;border-radius:4px;'
                f'margin-bottom:3px;align-items:flex-start;">'
                f'<span style="font-size:12px;color:#A32D2D;font-weight:700;width:20px;flex-shrink:0;margin-top:1px;">{i}</span>'
                f'<span style="font-size:13px;color:#333;line-height:1.6;font-weight:500;">{m}</span></div>'
            )
        return rows

    def temp_linechart_html(hour_temps_dict):
        slots = ["0000","0300","0600","0900","1200","1500","1800","2100"]
        lbl_short = ["00시","03시","06시","09시","12시","15시","18시","21시"]
        pairs = [(lbl_short[i], float(hour_temps_dict[sl])) for i, sl in enumerate(slots) if sl in hour_temps_dict]
        if len(pairs) < 2:
            return '<span style="font-size:12px;color:#aaa;">데이터 없음</span>'

        labels = [p[0] for p in pairs]
        values = [p[1] for p in pairs]
        n = len(values)
        W, H = 340, 160
        PAD_L, PAD_R, PAD_TOP, PAD_BOT = 10, 10, 28, 28
        plot_w = W - PAD_L - PAD_R
        plot_h = H - PAD_TOP - PAD_BOT
        t_min = min(values); t_max = max(values)
        t_range = t_max - t_min if t_max != t_min else 1

        def cx(i): return PAD_L + (i / (n - 1)) * plot_w
        def cy(v): return PAD_TOP + plot_h - ((v - t_min) / t_range) * plot_h * 0.80 - plot_h * 0.10

        now_h = datetime.now().hour
        now_lbl = f"{(now_h // 3) * 3:02d}시"
        try: cur_idx = labels.index(now_lbl)
        except ValueError: cur_idx = -1

        area_d = (
            f"M {cx(0):.1f},{cy(values[0]):.1f} "
            + " ".join(f"L {cx(i):.1f},{cy(v):.1f}" for i, v in enumerate(values))
            + f" L {cx(n-1):.1f},{PAD_TOP + plot_h:.1f} L {cx(0):.1f},{PAD_TOP + plot_h:.1f} Z"
        )
        line_d = f"M {cx(0):.1f},{cy(values[0]):.1f} " + " ".join(f"L {cx(i):.1f},{cy(v):.1f}" for i, v in enumerate(values))
        grid_lines = "".join(
            f'<line x1="{PAD_L}" y1="{PAD_TOP + plot_h * k / 4:.1f}" x2="{W-PAD_R}" y2="{PAD_TOP + plot_h * k / 4:.1f}" stroke="#f0f0f0" stroke-width="1"/>'
            for k in range(1, 4)
        )
        circles = temp_lbl_svg = x_lbl_svg = ""
        for i, (lbl, v) in enumerate(zip(labels, values)):
            x, y = cx(i), cy(v)
            is_cur = (i == cur_idx)
            circles    += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{5.5 if is_cur else 3.5}" fill="{"#D85A30" if is_cur else "#378ADD"}" stroke="#fff" stroke-width="2"/>'
            temp_lbl_svg += f'<text x="{x:.1f}" y="{y-9:.1f}" text-anchor="middle" font-size="10" font-weight="{"bold" if is_cur else "500"}" fill="{"#D85A30" if is_cur else "#1a3a5c"}" font-family="sans-serif">{v:.0f}°</text>'
            x_lbl_svg  += f'<text x="{x:.1f}" y="{PAD_TOP+plot_h+18}" text-anchor="middle" font-size="9" fill="{"#D85A30" if is_cur else "#999"}" font-weight="{"bold" if is_cur else "normal"}" font-family="sans-serif">{lbl}</text>'

        cur_vline = (f'<line x1="{cx(cur_idx):.1f}" y1="{PAD_TOP}" x2="{cx(cur_idx):.1f}" y2="{PAD_TOP+plot_h}" stroke="#D85A30" stroke-width="1" stroke-dasharray="3,3" opacity="0.6"/>'
                     if cur_idx >= 0 else "")

        svg = f"""<svg viewBox="0 0 {W} {H}" width="100%" style="display:block;overflow:visible;" xmlns="http://www.w3.org/2000/svg">
  <defs><linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#378ADD" stop-opacity="0.25"/>
    <stop offset="100%" stop-color="#378ADD" stop-opacity="0.02"/>
  </linearGradient></defs>
  {grid_lines}
  <path d="{area_d}" fill="url(#tempGrad)"/>
  {cur_vline}
  <path d="{line_d}" fill="none" stroke="#378ADD" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>
  {temp_lbl_svg}{circles}{x_lbl_svg}
</svg>"""
        hi, lo = max(values), min(values)
        badge = (
            f'<div style="display:flex;justify-content:flex-end;gap:10px;margin-bottom:6px;font-family:sans-serif;">'
            f'<span style="font-size:11px;color:#D85A30;font-weight:600;">▲ 최고 {hi:.0f}°C</span>'
            f'<span style="font-size:11px;color:#185FA5;font-weight:600;">▼ 최저 {lo:.0f}°C</span></div>'
        )
        return badge + svg

    def week_row_html(offset):
        d = today + timedelta(days=offset)
        ds = d.strftime("%Y%m%d")
        dow = ["월","화","수","목","금","토","일"][d.weekday()]
        if offset == 0: day_color = "#185FA5"
        elif d.weekday() == 5: day_color = "#185FA5"
        elif d.weekday() == 6: day_color = "#A32D2D"
        else: day_color = "#222"
        tag = " <span style='font-size:10px;color:#aaa;'>(오늘)</span>" if offset == 0 else \
              " <span style='font-size:10px;color:#aaa;'>(내일)</span>" if offset == 1 else ""

        if ds not in daily:
            return (
                f'<div style="display:flex;align-items:center;padding:6px 0;border-bottom:0.5px solid #eee;">'
                f'<span style="font-size:13px;font-weight:500;width:70px;color:{day_color};">{dow}요일{tag}</span>'
                f'<span style="flex:1;font-size:12px;color:#888;">─</span>'
                f'<span style="font-size:12px;color:#378ADD;width:32px;text-align:center;">─</span>'
                f'<span style="font-size:12px;min-width:70px;text-align:right;">─</span></div>'
            )

        dd = daily[ds]
        sky_rep = sky_label(Counter(dd["SKY"]).most_common(1)[0][0]) if dd["SKY"] else "─"
        pty_rep = pty_label(Counter(dd["PTY"]).most_common(1)[0][0]) if dd["PTY"] else ""
        pop_rep = f"{max(dd['POP'])}%" if dd["POP"] else "─"
        tmx_rep = f"{dd['TMX']}°" if dd["TMX"] else "─"
        tmn_rep = f"{dd['TMN']}°" if dd["TMN"] else "─"
        sky_disp = (sky_rep + (" / " + pty_rep if pty_rep and pty_rep != "없음" else "")).strip()

        return (
            f'<div style="display:flex;align-items:center;padding:6px 0;border-bottom:0.5px solid #eee;">'
            f'<span style="font-size:13px;font-weight:500;width:70px;color:{day_color};">{dow}요일{tag}</span>'
            f'<span style="flex:1;font-size:12px;color:#555;">{sky_disp}</span>'
            f'<span style="font-size:12px;color:#378ADD;width:32px;text-align:center;">{pop_rep}</span>'
            f'<span style="font-size:12px;min-width:70px;text-align:right;">'
            f'<span style="color:#D85A30;font-weight:500;">{tmx_rep}</span>'
            f'<span style="color:#378ADD;margin-left:4px;">{tmn_rep}</span></span></div>'
        )

    bars_html = temp_linechart_html(hour_temps)
    week_html  = "".join(week_row_html(i) for i in range(7))
    wildfire_badge = f'<span style="display:inline-block;padding:2px 10px;border-radius:20px;font-size:12px;font-weight:500;">{wildfire_icon} {wildfire_level}</span>'

    if warn_items is None:
        warn_html = '<div style="font-size:13px;color:#888;">특보 정보를 가져오지 못했습니다.</div>'
    elif len(warn_items) == 0:
        warn_html = (
            '<div style="display:flex;align-items:center;gap:10px;">'
            '<div style="width:28px;height:28px;border-radius:50%;background:#E1F5EE;display:flex;align-items:center;justify-content:center;flex-shrink:0;">'
            '<svg width="14" height="14" viewBox="0 0 14 14" fill="none">'
            '<circle cx="7" cy="7" r="5.5" stroke="#0F6E56" stroke-width="1.2"/>'
            '<path d="M5 7l1.5 1.5L9 5" stroke="#0F6E56" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>'
            '</svg></div>'
            f'<span style="font-size:13px;color:#555;">현재 {region_name} 지역 발효 중인 기상 특보 없음</span></div>'
        )
    else:
        warn_html = ""
        for w in warn_items:
            warn_html += (
                f'<div style="padding:8px 0;border-bottom:0.5px solid #eee;">'
                f'<div style="font-size:13px;font-weight:500;color:#A32D2D;margin-bottom:4px;">⚠ {w["title"]}</div>'
                f'<div style="font-size:11px;color:#888;margin-bottom:4px;">발표: {w["date"]}</div>'
                f'<div style="font-size:12px;color:#555;line-height:1.5;">{w["desc"][:150]}...</div></div>'
            )

    # ★ 핵심 변경: display(HTML(...)) → return html 문자열
    html = f"""
    <div style="max-width:390px;background:#f0f2f5;padding:12px;border-radius:16px;font-family:sans-serif;">
      <div style="background:linear-gradient(135deg,#1a3a5c,#2563a8);border-radius:12px;padding:16px;color:#fff;margin-bottom:10px;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
          <div>
            <div style="font-size:13px;opacity:.75;margin-bottom:2px;">기상현황 브리핑</div>
            <div style="font-size:20px;font-weight:600;">{region_name}</div>
          </div>
          <div style="text-align:right;font-size:11px;opacity:.65;line-height:1.8;">
            {today.strftime('%Y.%m.%d')}<br>{today.strftime('%H:%M')} 현재
          </div>
        </div>
      </div>

      {card('[1] 오늘의 날씨',
        row("하늘 상태", sky_label(today_sky)) +
        row("강수 형태", pty_label(today_pty)) +
        row("강수 확률", f"{today_pop}%") +
        row("최고 / 최저", f'<span style="color:#D85A30;">{today_tmx}°C</span> / <span style="color:#185FA5;">{today_tmn}°C</span>') +
        row("현재 습도", f"{cur_hum}%") +
        row("현재 풍속", f"{cur_wind} m/s &nbsp;{wind_dir_label(cur_wdir)}")
      )}

      {card('[2] 내일 기상 예측',
        row("하늘 상태", sky_label(tmr_sky)) +
        row("강수 형태", pty_label(tmr_pty)) +
        row("강수 확률", f"{tmr_pop}%") +
        row("최고 / 최저", f'<span style="color:#D85A30;">{tmr_tmx}°C</span> / <span style="color:#185FA5;">{tmr_tmn}°C</span>')
      )}

      {card('[3] 현재 기온',
        stat2("현재 기온", f"{cur_temp}°C", "실황", "체감 기온", chill, "풍속 보정") +
        row("일최고 예상", f"{today_tmx}°C", "color:#D85A30;") +
        row("일최저 예상", f"{today_tmn}°C", "color:#185FA5;")
      )}

      {card('[4] 기온 변화 (오늘)', bars_html)}

      {card('[5] 가시거리',
        row("추정 가시거리", vis_str) +
        f'<div style="margin-top:6px;font-size:11px;color:#aaa;">하늘: {sky_label(today_sky)} / 강수: {pty_label(today_pty)} / 풍속: {cur_wind} m/s</div>'
      )}

      {card('[6] 주간 요일별 예상 날씨',
        '<div style="display:flex;margin-bottom:6px;padding-bottom:4px;border-bottom:0.5px solid #eee;">'
        '<span style="font-size:10px;color:#aaa;width:70px;">요일</span>'
        '<span style="font-size:10px;color:#aaa;flex:1;">날씨</span>'
        '<span style="font-size:10px;color:#aaa;width:32px;text-align:center;">강수</span>'
        '<span style="font-size:10px;color:#aaa;min-width:70px;text-align:right;">최고/최저</span>'
        '</div>' + week_html
      )}

      {card('[7] 기상 특보', warn_html)}

      {card('[8] 화재 위험',
        row("일반 화재위험", fire_badge(fire_level)) +
        row("산불 위험도", wildfire_badge) +
        row("판정 근거", f"기온 {cur_temp}°C / 습도 {cur_hum}% / 풍속 {cur_wind} m/s", "font-size:11px;") +
        row("조치 사항", fire_action, "font-size:11px;max-width:55%;")
      )}

      {card('[9] 기상 상황에 따른 사고예방 활동', measure_items_html(m_list), danger=True)}

      <div style="text-align:center;font-size:10px;color:#aaa;padding-bottom:8px;line-height:1.8;">
        ※ 기상청 공공데이터 기반 실시간 자동 데이터 생성. {today.strftime('%Y-%m-%d %H:%M')}<br>
        ※ 출처: 기상청 단기예보 서비스 (data.go.kr)<br>
        ※ 작성자: 군수사령부 5급 김종섭
      </div>
    </div>
    """
    return html   # ★ display() 대신 return


# =========================================================
# 4. Streamlit UI (ipywidgets 완전 대체)
# =========================================================
st.set_page_config(
    page_title="기상정보 브리핑",
    page_icon="🌤️",
    layout="centered",
)

# 페이지 헤더
st.markdown(
    """
    <div style="background:linear-gradient(135deg,#1a3a5c 0%,#2563a8 100%);
    color:#fff;border-radius:12px;padding:16px 20px;margin-bottom:20px;">
      <div style="font-size:20px;font-weight:700;margin-bottom:4px;">
        🌤️ 안전사고 예방을 위한 기상정보 브리핑
      </div>
      <div style="font-size:12px;opacity:.75;">
        지역과 시/군/구를 선택한 뒤, 날씨 조회 버튼을 누르세요.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 지역 선택
sido_list = list(REGION_DATA.keys())
default_sido = "대전광역시"

col1, col2 = st.columns(2)
with col1:
    sido = st.selectbox("시/도", sido_list, index=sido_list.index(default_sido))
with col2:
    sigungu_list = list(REGION_DATA[sido].keys())
    sigungu = st.selectbox("시/군/구", sigungu_list)

# 조회 버튼
if st.button("🔍 날씨 조회", use_container_width=True, type="primary"):
    nx, ny, warn_kw = REGION_DATA[sido][sigungu]
    region_name = f"{sido} {sigungu}"

    with st.spinner(f"⏳ {region_name} 날씨 정보 최신화 중…"):
        html_result = fetch_and_render(region_name, nx, ny, warn_kw)

    # ★ Streamlit에서 HTML 렌더링 (height는 카드 수에 맞게 조정)
    components.html(html_result, height=2200, scrolling=True)
