import math
import random
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ------------------------------------------------------------
# 이벤트 온 | AI 기반 행사 자동 설계 대시보드
# 실행: streamlit run app.py
# ------------------------------------------------------------
st.set_page_config(
    page_title="이벤트 온 | AI 행사 설계",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Theme ----------
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
      html, body, [class*="css"] { font-family: 'DM Sans', 'Noto Sans KR', sans-serif; }
      .stApp { background: #f5f7fb; }
      [data-testid="stSidebar"] { background: #101a35; }
      [data-testid="stSidebar"] * { color: #f2f5ff !important; }
      .hero {
        background: linear-gradient(120deg, #17264d 0%, #284a88 60%, #4169b5 100%);
        padding: 28px 32px; border-radius: 22px; color: white; margin-bottom: 20px;
      }
      .hero h1 { font-size: 34px; line-height: 1.2; margin: 0 0 8px 0; color: white; }
      .hero p { color: #dce7ff; margin: 0; font-size: 15px; }
      .eyebrow { color: #91b6ff; font-size: 12px; font-weight: 800; letter-spacing: 1.5px; }
      .metric-card {
        background: white; border: 1px solid #e5eaf4; border-radius: 16px;
        padding: 17px 18px; min-height: 105px;
      }
      .metric-label { color: #69758f; font-size: 12px; margin-bottom: 8px; }
      .metric-value { color: #17264d; font-size: 26px; font-weight: 800; }
      .metric-note { color: #79859d; font-size: 11px; margin-top: 4px; }
      .section-title { font-size: 20px; font-weight: 800; color: #17264d; margin: 6px 0 3px 0; }
      .section-sub { color: #75819a; font-size: 13px; margin-bottom: 14px; }
      .info-box {
        background: #eef4ff; border: 1px solid #d9e6ff; border-radius: 12px;
        padding: 13px 15px; color: #284a88; font-size: 13px;
      }
      .workflow-step {
        background: white; border: 1px solid #e5eaf4; border-radius: 13px;
        padding: 13px 14px; height: 100%;
      }
      .step-num { color: #4f75d6; font-size: 11px; font-weight: 800; }
      .step-name { color: #17264d; font-weight: 800; margin: 4px 0; }
      .step-desc { color: #74809a; font-size: 12px; }
      div.stButton > button { border-radius: 10px; font-weight: 700; min-height: 42px; }
      h2, h3 { color: #17264d; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar inputs ----------
with st.sidebar:
    st.markdown("## 🎪 이벤트 온")
    st.caption("AI EVENT DESIGN STUDIO")
    st.markdown("---")
    st.markdown("### 행사 기본 정보")
    event_name = st.text_input("행사명", "청춘 페스티벌 2026")
    event_purpose = st.selectbox(
        "행사 목적", ["축제·페스티벌", "기업 행사", "학교 행사", "전시·박람회", "지역 커뮤니티", "기타"]
    )
    budget = st.select_slider(
        "예상 예산", options=["500만 원", "1,000만 원", "3,000만 원", "5,000만 원", "1억 원", "3억 원"],
        value="5,000만 원"
    )
    visitors = st.number_input("예상 방문객 수", min_value=50, max_value=100000, value=3000, step=100)
    venue = st.selectbox("행사 장소", ["야외 공원", "실내 전시장", "학교 운동장", "컨벤션 센터", "복합 공간"])
    mood = st.multiselect(
        "원하는 분위기", ["활기찬", "감성적인", "가족 친화적", "미래적인", "고급스러운", "자연 친화적"],
        default=["활기찬", "감성적인"]
    )
    age_group = st.selectbox("주요 예상 연령대", ["10대", "20대", "전 연령", "가족 단위", "30~40대", "50대 이상"])
    duration = st.selectbox("행사 진행 시간", ["2시간", "4시간", "6시간", "하루 종일", "2일 이상"])
    st.markdown("---")
    st.markdown("### 원하는 부스 추가")
    booth_input = st.text_input("부스 이름", placeholder="예: 포토존, 굿즈 판매")
    booth_kind = st.selectbox("부스 유형", ["체험", "식음료", "판매", "전시", "휴식", "기타"])
    add_booth = st.button("＋ 부스 목록에 추가", use_container_width=True)
    if "custom_booths" not in st.session_state:
        st.session_state.custom_booths = []
    if add_booth and booth_input.strip():
        item = {"name": booth_input.strip(), "kind": booth_kind}
        if item not in st.session_state.custom_booths:
            st.session_state.custom_booths.append(item)
        st.rerun()
    if st.session_state.custom_booths:
        st.caption("추가한 부스")
        for i, booth in enumerate(st.session_state.custom_booths):
            c1, c2 = st.columns([4, 1])
            c1.write(f"• {booth['name']} · {booth['kind']}")
            if c2.button("삭제", key=f"del_{i}"):
                st.session_state.custom_booths.pop(i)
                st.rerun()
    generate = st.button("✨ AI 행사 설계 시작", type="primary", use_container_width=True)

# ---------- Helpers ----------
def parse_budget(label):
    return {
        "500만 원": 5_000_000,
        "1,000만 원": 10_000_000,
        "3,000만 원": 30_000_000,
        "5,000만 원": 50_000_000,
        "1억 원": 100_000_000,
        "3억 원": 300_000_000,
    }.get(label, 50_000_000)


def create_layout(venue_name, visitors, custom_booths):
    # Schematic coordinates on a 100 x 70 canvas. This is a generated concept,
    # not a surveyed or safety-certified venue plan.
    nodes = [
        {"name": "메인 공연장", "x": 50, "y": 53, "w": 28, "h": 16, "color": "#dce7ff", "line": "#5276d8", "kind": "공연"},
        {"name": "푸드존", "x": 80, "y": 43, "w": 15, "h": 13, "color": "#ffead9", "line": "#e68b45", "kind": "식음료"},
        {"name": "체험부스 A", "x": 18, "y": 43, "w": 23, "h": 10, "color": "#e0f5ec", "line": "#36a77c", "kind": "체험"},
        {"name": "체험부스 B", "x": 18, "y": 29, "w": 23, "h": 10, "color": "#e0f5ec", "line": "#36a77c", "kind": "체험"},
        {"name": "휴게공간", "x": 80, "y": 25, "w": 15, "h": 12, "color": "#f0e7ff", "line": "#9365ce", "kind": "휴식"},
        {"name": "안내센터", "x": 50, "y": 14, "w": 15, "h": 8, "color": "#fff4c9", "line": "#c59a22", "kind": "안내"},
        {"name": "응급의료센터", "x": 8, "y": 14, "w": 16, "h": 8, "color": "#ffe0e3", "line": "#d85b6b", "kind": "의료"},
        {"name": "입장 / 퇴장", "x": 92, "y": 8, "w": 12, "h": 7, "color": "#e6edf5", "line": "#77869d", "kind": "출입"},
    ]
    for i, booth in enumerate(custom_booths):
        col = i % 3
        row = i // 3
        nodes.append({
            "name": booth["name"][:16],
            "x": 31 + col * 19,
            "y": 7 + row * 12,
            "w": 15,
            "h": 7,
            "color": "#e6f3ff",
            "line": "#4d9bd6",
            "kind": booth["kind"],
        })
    return nodes


def make_map(nodes, visitors, crowd_level):
    fig = go.Figure()
    # Venue boundary
    fig.add_shape(type="rect", x0=1, y0=1, x1=99, y1=68, line=dict(color="#aab6cc", width=2), fillcolor="#fbfcff", layer="below")
    # Main paths
    paths = [
        ([10, 50, 50, 90], [9, 9, 33, 33]),
        ([50, 50], [33, 53]),
        ([50, 20], [33, 33]),
        ([50, 83], [33, 33]),
        ([20, 20], [33, 43]),
    ]
    for xs, ys in paths:
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color="#c6d2e8", width=9), hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color="#ffffff", width=3, dash="dot"), hoverinfo="skip", showlegend=False))
    for n in nodes:
        x0, x1 = n["x"] - n["w"] / 2, n["x"] + n["w"] / 2
        y0, y1 = n["y"] - n["h"] / 2, n["y"] + n["h"] / 2
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
                      line=dict(color=n["line"], width=2), fillcolor=n["color"], opacity=0.97)
        fig.add_annotation(x=n["x"], y=n["y"], text=f"<b>{n['name']}</b>", showarrow=False,
                           font=dict(size=10, color="#253452"), align="center")
    # Crowd markers: deterministic positions so reruns remain stable.
    rng = random.Random(int(visitors) + int(crowd_level))
    crowd_x, crowd_y, crowd_color = [], [], []
    for _ in range(min(95, max(20, int(visitors / 40)))):
        x = rng.uniform(8, 93)
        y = rng.uniform(7, 61)
        crowd_x.append(x)
        crowd_y.append(y)
        crowd_color.append("#e36d5c" if crowd_level >= 70 and rng.random() < 0.38 else "#4e82df")
    fig.add_trace(go.Scatter(
        x=crowd_x, y=crowd_y, mode="markers",
        marker=dict(size=6, color=crowd_color, opacity=0.75, line=dict(width=0.5, color="white")),
        name="군중 위치(시뮬레이션)",
        hovertemplate="시뮬레이션 관측점<extra></extra>",
    ))
    fig.update_layout(
        height=500, margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(range=[0, 100], visible=False, fixedrange=True),
        yaxis=dict(range=[0, 70], visible=False, fixedrange=True, scaleanchor="x", scaleratio=1),
        showlegend=False,
    )
    return fig


def metric_card(label, value, note):
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


# ---------- Header ----------
st.markdown(
    f"""
    <div class="hero">
      <div class="eyebrow">AI-POWERED EVENT PLANNING PLATFORM</div>
      <h1>이벤트 온 <span style="font-size:18px;font-weight:500;color:#cbdcff;">EVENT ON</span></h1>
      <p>아이디어부터 공간 배치까지, 데이터 기반으로 더 안전하고 효율적인 행사를 설계하세요.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "design_generated" not in st.session_state:
    st.session_state.design_generated = False
if generate:
    st.session_state.design_generated = True

# Dynamic indicators
budget_num = parse_budget(budget)
crowd_score = min(96, max(24, int(visitors / 75) + (15 if venue in ["실내 전시장", "컨벤션 센터"] else 5)))
crowd_score = min(96, crowd_score)
safety_score = max(68, 98 - int(visitors / 600) - (8 if venue == "실내 전시장" else 0))
efficiency_score = min(97, 75 + len(st.session_state.custom_booths) * 2 + (8 if budget_num >= 50_000_000 else 0))
layout_nodes = create_layout(venue, visitors, st.session_state.custom_booths)

# Metrics
m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("예상 방문객", f"{visitors:,}명", "입력한 예상 인원 기준")
with m2:
    metric_card("예산 규모", budget, "입력한 총예산")
with m3:
    metric_card("예상 혼잡 지수", f"{crowd_score}/100", "높을수록 혼잡 가능성 큼")
with m4:
    metric_card("설계 안전 체크", f"{safety_score}/100", "개념 설계용 참고 지표")

st.markdown("")

# Main map + insights
left, right = st.columns([1.7, 1], gap="large")
with left:
    st.markdown('<div class="section-title">디지털 트윈 행사장 배치도</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">공간 구역과 이동 통로를 한눈에 확인하세요.</div>', unsafe_allow_html=True)
    crowd_level = st.slider("군중 이동 시뮬레이션 강도", 20, 100, crowd_score, 5, help="데모용 시뮬레이션 강도입니다. 실제 센서 데이터가 연결된 것은 아닙니다.")
    st.plotly_chart(make_map(layout_nodes, visitors, crowd_level), use_container_width=True, config={"displayModeBar": False})
    st.caption("※ 배치도와 군중 점은 화면 시연을 위한 개념 시뮬레이션이며, 실제 측량·실시간 센서·안전 인증 데이터가 아닙니다.")

with right:
    st.markdown('<div class="section-title">AI 설계 인사이트</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">입력한 조건을 바탕으로 한 예시 분석</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="info-box"><b>추천 운영 전략</b><br>
        {venue} 환경을 기준으로 출입구와 주요 구역 사이에 중앙 이동 통로를 확보하는 배치를 제안합니다.</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("")
    if crowd_level >= 70:
        st.warning("혼잡 주의: 공연장·푸드존 주변에 대기열 공간과 일방통행 동선을 추가 검토하세요.")
    else:
        st.success("혼잡 예측: 현재 설정에서는 주요 구역 사이에 이동 통로를 분산하는 방안을 권장합니다.")
    st.markdown("**추천 배치 원칙**")
    st.write("• 입구에서 안내센터가 잘 보이도록 배치")
    st.write("• 응급의료센터는 주요 동선에서 접근하기 쉬운 위치에 배치")
    st.write("• 푸드존과 휴게공간을 분리해 체류 인원 분산")
    st.write("• 공연 종료 시 출구 방향으로 흐름이 모이지 않도록 퇴장 동선 검토")
    st.progress(efficiency_score / 100, text=f"공간 활용 참고 점수 {efficiency_score}/100")

st.markdown("---")

# Workflow
st.markdown('<div class="section-title">AI 행사 설계 프로세스</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">행사 정보 입력부터 설계안과 분석 리포트 생성까지</div>', unsafe_allow_html=True)
steps = [
    ("01", "정보 입력", "행사 목적·예산·방문객·장소 조건 정리"),
    ("02", "디지털 트윈 생성", "행사 공간과 구역별 제약 조건 구성"),
    ("03", "배치안 탐색", "여러 배치 후보를 만들고 조건에 맞게 평가"),
    ("04", "군중 흐름 분석", "혼잡 가능 구역과 이동 동선 검토"),
    ("05", "다목적 최적화", "안전·접근성·공간 활용·예산을 함께 고려"),
    ("06", "설계안 리포트", "추천 배치와 추천 이유를 요약"),
]
cols = st.columns(6, gap="small")
for col, (num, name, desc) in zip(cols, steps):
    with col:
        st.markdown(
            f'<div class="workflow-step"><div class="step-num">STEP {num}</div>'
            f'<div class="step-name">{name}</div><div class="step-desc">{desc}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown("---")

# Report
st.markdown('<div class="section-title">행사 설계안 요약</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">현재 입력값에 맞춘 초안입니다. 실제 운영 전 현장 확인과 전문가 검토가 필요합니다.</div>', unsafe_allow_html=True)
r1, r2 = st.columns([1.1, 1], gap="large")
with r1:
    st.markdown("#### 행사 개요")
    report = pd.DataFrame([
        ["행사명", event_name or "미입력"],
        ["행사 목적", event_purpose],
        ["예상 예산", budget],
        ["예상 방문객", f"{visitors:,}명"],
        ["장소 유형", venue],
        ["예상 연령대", age_group],
        ["진행 시간", duration],
        ["원하는 분위기", ", ".join(mood) if mood else "미선택"],
        ["추가 부스", ", ".join(b["name"] for b in st.session_state.custom_booths) or "없음"],
    ], columns=["항목", "설계 조건"])
    st.dataframe(report, hide_index=True, use_container_width=True)
with r2:
    st.markdown("#### 추천 설계 이유")
    reasons = [
        f"예상 방문객 {visitors:,}명을 기준으로 주요 시설을 여러 구역에 나누어 배치했습니다.",
        "안내센터와 응급의료센터를 눈에 띄고 접근하기 쉬운 위치에 두는 구성을 제안합니다.",
        "푸드존과 휴게공간을 분리해 한 지점에 인원이 오래 머무르는 현상을 줄이는 방향입니다.",
        f"행사 분위기({', '.join(mood) if mood else '미선택'})와 연령대({age_group})를 운영 동선과 안내 방식에 반영할 수 있습니다.",
    ]
    for reason in reasons:
        st.markdown(f"- {reason}")
    st.markdown("")
    st.info("현재 버전은 규칙 기반 데모입니다. 실제 AI 모델, 수천 개 배치안 탐색, 실시간 군중 데이터 연결은 별도 개발이 필요합니다.")

# Downloadable report
csv_data = report.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "⬇ 행사 설계 요약 CSV 다운로드",
    data=csv_data,
    file_name="event_on_design_report.csv",
    mime="text/csv",
)

st.markdown(
    """
    <div style="text-align:center;color:#8a95aa;font-size:11px;padding:24px 0 8px 0;">
      EVENT ON · AI Event Design Dashboard · Concept prototype
    </div>
    """,
    unsafe_allow_html=True,
)
