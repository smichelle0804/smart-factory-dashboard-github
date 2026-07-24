from pathlib import Path
import json
import math

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# 0. Page configuration
# =========================================================
st.set_page_config(
    page_title="스마트팩토리 전력 비효율 구간 탐지를 위한  다변량 AI 관리 모델",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "dashboard_data_report"
MAX_PLOT_POINTS = 45_000

COLORS = {
    "bg": "#07101F",
    "panel": "#111A34",
    "panel2": "#152344",
    "panel3": "#1B315A",
    "border": "#27385E",
    "text": "#EDF4FF",
    "muted": "#91A4C3",
    "teal": "#25C4C0",
    "cyan": "#59C4FF",
    "blue": "#4D7CFE",
    "yellow": "#F7B844",
    "orange": "#FF9955",
    "red": "#FF6677",
    "purple": "#9C87FF",
    "green": "#5DD8A6",
    "grid": "#263658",
}

REQUIRED_FILES = [
    "equipment_summary.csv",
    "screening_feature_contribution.csv",
    "monitoring_1min.parquet",
    "anomaly_points.parquet",
    "hourly_summary.csv",
    "event_log.csv",
    "detection_summary.csv",
    "overlap_summary.csv",
    "prediction_validation.csv",
    "report_summary.json",
]


# =========================================================
# 1. CSS — dense dark cockpit inspired by the supplied examples
# =========================================================
st.markdown(
    f"""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

    header[data-testid="stHeader"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    #MainMenu,
    footer {{
        display: none !important;
        height: 0 !important;
        visibility: hidden !important;
    }}

    html, body, .stApp,
    h1, h2, h3, h4, h5, h6, p, label, div, span,
    button, input, textarea, select, option,
    [class*="st-"], [data-testid] {{
        font-family: "Pretendard Variable", Pretendard, -apple-system,
        BlinkMacSystemFont, "Apple SD Gothic Neo", "Noto Sans KR",
        "Segoe UI", sans-serif !important;
    }}

    .stApp {{
        background:
          radial-gradient(circle at 52% -10%, rgba(77,124,254,0.15), transparent 27%),
          {COLORS['bg']};
        color: {COLORS['text']};
    }}

    [data-testid="stMainBlockContainer"], .block-container {{
        max-width: 1680px;
        padding: 0.35rem 1.15rem 2.2rem 1.15rem !important;
    }}

    .hero {{
        display:flex;
        justify-content:space-between;
        align-items:flex-start;
        background: linear-gradient(90deg, #0E1730 0%, #142A50 56%, #0E1730 100%);
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 13px 18px 12px 18px;
        margin-bottom: 8px;
        box-shadow: 0 9px 28px rgba(0,0,0,.22);
    }}
    .hero-title {{font-size:1.62rem;font-weight:850;letter-spacing:-.02em;color:{COLORS['text']};}}
    .hero-sub {{font-size:.84rem;font-weight:650;color:{COLORS['teal']};margin-top:4px;}}
    .hero-date {{font-size:.75rem;color:{COLORS['muted']};margin-top:4px;text-align:right;}}

    .kpi {{
        background: linear-gradient(145deg, #1B315D, #264F8B);
        border: 1px solid #365E9B;
        border-radius: 6px;
        padding: 10px 11px 9px 11px;
        min-height: 91px;
        box-shadow: 0 7px 18px rgba(0,0,0,.18);
    }}
    .kpi.teal {{background:linear-gradient(145deg,#113A48,#176A70);border-color:#268B8E;}}
    .kpi.gold {{background:linear-gradient(145deg,#493516,#7B5C23);border-color:#A77A2D;}}
    .kpi.red {{background:linear-gradient(145deg,#4C2132,#87344A);border-color:#B84B67;}}
    .kpi-label {{font-size:.72rem;color:#CAD7EB;font-weight:700;}}
    .kpi-value {{font-size:1.35rem;color:#FFF;font-weight:850;line-height:1.1;margin-top:8px;}}
    .kpi-note {{font-size:.66rem;color:#CBD7E9;margin-top:7px;line-height:1.3;}}

    .section-title {{
        font-size:.89rem;
        font-weight:800;
        color:{COLORS['text']};
        margin:2px 0 6px 1px;
    }}
    .mini-title {{font-size:.78rem;font-weight:800;color:{COLORS['text']};margin-bottom:5px;}}

    .panel-note {{
        background:rgba(37,196,192,.08);
        border:1px solid rgba(37,196,192,.22);
        border-left:4px solid {COLORS['teal']};
        border-radius:6px;
        padding:9px 11px;
        font-size:.75rem;
        color:#C9D7EB;
        line-height:1.48;
    }}

    .status-line {{
        display:flex;justify-content:space-between;align-items:center;
        background:#121E3A;border:1px solid {COLORS['border']};
        border-radius:6px;padding:8px 9px;margin-bottom:6px;
    }}
    .status-name {{font-size:.75rem;font-weight:750;color:#D2DDF0;}}
    .pill {{font-size:.67rem;font-weight:850;border-radius:999px;padding:3px 8px;}}
    .pill.ok {{color:#B9F7DF;background:rgba(93,216,166,.14);border:1px solid rgba(93,216,166,.42);}}
    .pill.alert {{color:#FFE0E5;background:rgba(255,102,119,.14);border:1px solid rgba(255,102,119,.42);}}

    div[data-testid="stDataFrame"] {{
        border:1px solid {COLORS['border']};
        border-radius:6px;
        overflow:hidden;
    }}
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    input {{background:#111B35 !important;color:{COLORS['text']} !important;border-color:{COLORS['border']} !important;}}

    [data-testid="stRadio"] > div {{gap:.35rem;}}
    [data-testid="stRadio"] label {{
        background:#111B35;border:1px solid {COLORS['border']};border-radius:5px;
        padding:5px 10px;margin:0;color:#DCE7F8;
    }}
    [data-testid="stRadio"] label:has(input:checked) {{
        background:#21487F;border-color:#3C6EB0;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 2. Data loading
# =========================================================
missing = [f for f in REQUIRED_FILES if not (DATA_DIR / f).exists()]
if missing:
    st.error("dashboard_data_report 폴더에 필요한 파일이 없습니다.")
    st.code("\n".join(missing))
    st.info("먼저 01_report_aligned_dashboard_data.ipynb를 위에서부터 모두 실행하세요.")
    st.stop()


@st.cache_data(show_spinner=False)
def load_csv(name: str, parse_dates=None) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / name, parse_dates=parse_dates)


@st.cache_data(show_spinner=False)
def load_parquet(name: str) -> pd.DataFrame:
    df = pd.read_parquet(DATA_DIR / name)
    for col in ["datetime", "datetime_hour", "start_datetime", "end_datetime"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df


@st.cache_data(show_spinner=False)
def load_json(name: str) -> dict:
    with open(DATA_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


equipment = load_csv("equipment_summary.csv")
contribution = load_csv("screening_feature_contribution.csv")
monitoring = load_parquet("monitoring_1min.parquet")
anomaly_points = load_parquet("anomaly_points.parquet")
hourly = load_csv("hourly_summary.csv", parse_dates=["datetime_hour"])
events = load_csv("event_log.csv", parse_dates=["start_datetime", "end_datetime"])
detection = load_csv("detection_summary.csv")
overlap = load_csv("overlap_summary.csv")
prediction = load_csv("prediction_validation.csv")
summary = load_json("report_summary.json")


# =========================================================
# 3. Helpers
# =========================================================
def kpi(label: str, value: str, note: str = "", tone: str = ""):
    st.markdown(
        f"""
        <div class="kpi {tone}">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_line(name: str, is_alert: bool):
    cls = "alert" if is_alert else "ok"
    text = "이상" if is_alert else "정상"
    st.markdown(
        f'<div class="status-line"><span class="status-name">{name}</span>'
        f'<span class="pill {cls}">{text}</span></div>',
        unsafe_allow_html=True,
    )


def style_fig(fig: go.Figure, height=300, legend=True):
    fig.update_layout(
        height=height,
        margin=dict(l=14, r=12, t=28, b=20),
        paper_bgcolor=COLORS["panel"],
        plot_bgcolor=COLORS["panel"],
        font=dict(
            family='"Pretendard Variable", Pretendard, "Noto Sans KR", sans-serif',
            color=COLORS["text"],
            size=10,
        ),
        showlegend=legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=9),
        ),
        hoverlabel=dict(bgcolor="#0D1730", font_color=COLORS["text"]),
    )
    fig.update_xaxes(gridcolor=COLORS["grid"], linecolor=COLORS["border"])
    fig.update_yaxes(gridcolor=COLORS["grid"], linecolor=COLORS["border"])
    return fig


def filter_range(df, col, start_date, end_date):
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date) + pd.Timedelta(days=1)
    return df[(df[col] >= start) & (df[col] < end)].copy()


def pct(v, digits=2):
    return f"{v * 100:.{digits}f}%"


# =========================================================
# 4. Header and navigation
# =========================================================
st.markdown(
    f"""
    <div class="hero">
      <div>
        <div class="hero-title">스마트팩토리 전력 비효율 통합 관제 대시보드 </div>
        <div class="hero-sub"> 예비건조기 IQR / EWMA / Isolation Forest 통합 탐지</div>
      </div>
      <div class="hero-date">{summary['period_start']} — {summary['period_end']}<br>5초 RTU 전력 데이터</div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.radio(
    "메뉴",
    ["통합 관제", "설비 스크리닝", "탐지 방법론", "예측 검증", "데이터 품질", "이벤트 로그"],
    horizontal=True,
    label_visibility="collapsed",
)


# =========================================================
# 5. Integrated cockpit
# =========================================================
if page == "통합 관제":
    min_date = monitoring["datetime"].min().date()
    max_date = monitoring["datetime"].max().date()
    default_start = max(min_date, max_date - pd.Timedelta(days=6))

    f1, f2, f3 = st.columns([1.45, 1, 1])
    with f1:
        date_value = st.date_input(
            "분석 기간",
            value=(default_start, max_date),
            min_value=min_date,
            max_value=max_date,
        )
    if isinstance(date_value, tuple) and len(date_value) == 2:
        start_date, end_date = date_value
    else:
        start_date = end_date = date_value
    with f2:
        display_mode = st.selectbox("표시 대상", ["전체", "두 방법 이상 공통 탐지", "고빈도 시간"])
    with f3:
        st.text_input("집중 관리 설비", summary["target_module"], disabled=True)

    view = filter_range(monitoring, "datetime", start_date, end_date)
    points = filter_range(anomaly_points, "datetime", start_date, end_date)
    hourly_view = filter_range(hourly, "datetime_hour", start_date, end_date)
    event_view = filter_range(events, "start_datetime", start_date, end_date)

    if display_mode == "두 방법 이상 공통 탐지":
        points = points[points["model_agreement_count"] >= 2]
    elif display_mode == "고빈도 시간":
        high_hours = set(hourly_view.loc[hourly_view["is_high_frequency"] == 1, "datetime_hour"])
        points = points[points["datetime_hour"].isin(high_hours)]

    latest = view.iloc[-1]
    latest_points = points[points["datetime"] <= latest["datetime"]]
    latest_event_count = int(latest.get("event_count", 0))

    cards = st.columns(6)
    with cards[0]:
        kpi("집중 관리 설비", "15번", "예비건조기", "red")
    with cards[1]:
        kpi("전체 설비 IF 이상률", "1.62%", "702 / 43,201구간 · 전체 1위", "teal")
    with cards[2]:
        kpi("IQR 탐지", "20,317건", "예비건조기 0.78%", "")
    with cards[3]:
        kpi("EWMA 탐지", "26,244건", "1.01% · 25,991 이벤트", "teal")
    with cards[4]:
        kpi("정밀 IF 탐지", "20,736건", "예비건조기 0.80%", "")
    with cards[5]:
        kpi("고빈도 구간", "369개", "시간당 10.93건 초과", "gold")

    st.write("")
    left, center, right = st.columns([1.02, 2.25, 1.03])

    with left:
        st.markdown('<div class="section-title">설비별 비효율 탐지 순위</div>', unsafe_allow_html=True)
        rank_df = equipment.sort_values("if_anomaly_rate_pct", ascending=True).copy()
        rank_df["group"] = np.where(rank_df["module(equipment)"] == summary["target_module"], "예비건조기", "기타 설비")
        fig = px.bar(
            rank_df,
            x="if_anomaly_rate_pct",
            y="module(equipment)",
            orientation="h",
            color="group",
            color_discrete_map={"예비건조기": COLORS["red"], "기타 설비": COLORS["teal"]},
            labels={"if_anomaly_rate_pct": "이상률 (%)", "module(equipment)": "", "group": ""},
            hover_data=["if_anomaly_count", "screening_rank"],
        )
        fig.update_layout(showlegend=False)
        style_fig(fig, 390, False)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-title">선택 기간 상태 구성</div>', unsafe_allow_html=True)
        agreement = view["model_agreement_count"].value_counts().reindex([0,1,2,3], fill_value=0).reset_index()
        agreement.columns = ["count_models", "count"]
        agreement["label"] = agreement["count_models"].map({0:"정상",1:"1개 탐지",2:"2개 탐지",3:"3개 탐지"})
        fig = px.pie(
            agreement,
            values="count",
            names="label",
            hole=.64,
            color="label",
            color_discrete_map={"정상":COLORS["green"],"1개 탐지":COLORS["yellow"],"2개 탐지":COLORS["orange"],"3개 탐지":COLORS["red"]},
        )
        fig.update_traces(textinfo="percent", hovertemplate="%{label}<br>%{value:,}개<extra></extra>")
        fig.add_annotation(text=f"{len(view):,}<br><span style='font-size:9px'>1분 구간</span>", x=.5, y=.5, showarrow=False, font=dict(color=COLORS["text"], size=14))
        style_fig(fig, 260, True)
        st.plotly_chart(fig, use_container_width=True)

    with center:
        st.markdown('<div class="section-title">예비건조기 역률 · EWMA 관리도</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=view["datetime"], y=view["powerfactor_avg"], name="평균 역률", mode="lines", line=dict(color=COLORS["cyan"], width=1.4)))
        fig.add_trace(go.Scatter(x=view["datetime"], y=view["ewma"], name="EWMA", mode="lines", line=dict(color=COLORS["yellow"], width=1.35)))
        fig.add_trace(go.Scatter(x=view["datetime"], y=view["ewma_ucl"], name="EWMA 상한", mode="lines", line=dict(color=COLORS["muted"], dash="dot", width=.8)))
        fig.add_trace(go.Scatter(x=view["datetime"], y=view["ewma_lcl"], name="EWMA 하한", mode="lines", line=dict(color=COLORS["muted"], dash="dot", width=.8)))
        ewma_pts = points[points["ewma_flag"] == 1]
        common_pts = points[points["model_agreement_count"] >= 2]
        fig.add_trace(go.Scatter(x=ewma_pts["datetime"], y=ewma_pts["powerfactor_avg"], name="EWMA 이상", mode="markers", marker=dict(color=COLORS["red"], size=5, symbol="diamond")))
        fig.add_trace(go.Scatter(x=common_pts["datetime"], y=common_pts["powerfactor_avg"], name="2개 이상 일치", mode="markers", marker=dict(color=COLORS["purple"], size=6, symbol="x")))
        fig.update_yaxes(title="Power Factor")
        style_fig(fig, 450, True)
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="mini-title">3상 불평형률</div>', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=view["datetime"], y=view["voltage_unbalance_pct"], name="전압 불평형률", mode="lines", line=dict(color=COLORS["teal"], width=1.1)))
            fig.add_trace(go.Scatter(x=view["datetime"], y=view["current_unbalance_pct"], name="전류 불평형률", mode="lines", line=dict(color=COLORS["purple"], width=1.1)))
            fig.update_yaxes(title="%")
            style_fig(fig, 255, True)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown('<div class="mini-title">시간당 EWMA 이벤트</div>', unsafe_allow_html=True)
            fig = go.Figure(go.Bar(x=hourly_view["datetime_hour"], y=hourly_view["event_count"], marker_color=COLORS["cyan"], name="이벤트"))
            fig.add_hline(y=summary["high_frequency_threshold"], line_dash="dash", line_color=COLORS["red"], annotation_text="10.93건")
            fig.update_yaxes(title="건")
            style_fig(fig, 255, False)
            st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown('<div class="section-title">선택 시점 통합 상태</div>', unsafe_allow_html=True)
        status_line("IQR", bool(latest["iqr_flag"]))
        status_line("EWMA", bool(latest["ewma_flag"]))
        status_line("Isolation Forest", bool(latest["if_flag"]))

        st.markdown('<div class="section-title">IF 이상 판정 기여도</div>', unsafe_allow_html=True)
        fig = px.pie(
            contribution,
            names="feature_label",
            values="contribution",
            hole=.62,
            color_discrete_sequence=[COLORS["teal"], COLORS["cyan"], COLORS["yellow"], COLORS["blue"], COLORS["purple"], COLORS["red"]],
        )
        fig.update_traces(textinfo="percent", hovertemplate="%{label}<br>%{value:.6f}<extra></extra>")
        style_fig(fig, 260, True)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-title">최근 이상 이벤트</div>', unsafe_allow_html=True)
        recent = event_view.sort_values("start_datetime", ascending=False).head(7).copy()
        if recent.empty:
            st.info("선택 기간에 이벤트가 없습니다.")
        else:
            recent = recent[["start_datetime", "duration_seconds", "minimum_powerfactor", "max_model_agreement"]]
            recent.columns = ["발생 시각", "지속(초)", "최저 역률", "일치"]
            recent["발생 시각"] = recent["발생 시각"].dt.strftime("%m-%d %H:%M:%S")
            st.dataframe(recent, hide_index=True, use_container_width=True, height=245)

    st.write("")
    b1, b2, b3 = st.columns([1.1, 1.2, 1.0])
    with b1:
        st.markdown('<div class="section-title">날짜 × 시간 이벤트 히트맵</div>', unsafe_allow_html=True)
        h = hourly_view.copy()
        h["date"] = h["datetime_hour"].dt.strftime("%m-%d")
        h["hour"] = h["datetime_hour"].dt.hour
        p = h.pivot_table(index="date", columns="hour", values="event_count", aggfunc="sum", fill_value=0)
        fig = px.imshow(p, aspect="auto", color_continuous_scale=[[0,"#14213D"],[.35,"#1D7186"],[.72,"#F7B844"],[1,"#FF6677"]], labels=dict(x="시간", y="날짜", color="건"))
        fig.update_layout(coloraxis_showscale=False)
        style_fig(fig, 310, False)
        st.plotly_chart(fig, use_container_width=True)
    with b2:
        st.markdown('<div class="section-title">탐지 방법별 비율</div>', unsafe_allow_html=True)
        d = detection.copy()
        d["anomaly_rate_pct"] = d["anomaly_rate"] * 100
        fig = px.bar(d, x="method", y="anomaly_rate_pct", color="method", text=d["anomaly_count"].map(lambda x:f"{int(x):,}"), color_discrete_map={"IQR":COLORS["teal"],"EWMA":COLORS["yellow"],"Isolation Forest":COLORS["purple"]}, labels={"method":"", "anomaly_rate_pct":"이상률 (%)"})
        fig.update_layout(showlegend=False)
        style_fig(fig, 310, False)
        st.plotly_chart(fig, use_container_width=True)
    with b3:
        st.markdown('<div class="section-title">운영 결론</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="panel-note">
            예비건조기는 유효전력 소비량은 다른 설비와 유사하지만 역률 채널만 불안정하다.<br><br>
            역률 변수를 제거하면 미래 예측 AUC가 약 0.5로 하락하므로, 본 시스템은 조기 예측이 아니라 현재 상태 탐지를 중심으로 설계한다.<br><br>
            IQR·EWMA·Isolation Forest의 탐지 비율이 0.78~1.01%로 수렴하며 서로 다른 이상을 추가 포착한다.
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# 6. Screening page
# =========================================================
elif page == "설비 스크리닝":
    cols = st.columns(5)
    with cols[0]: kpi("분석 구간", "561,613", "5분 리샘플 구간")
    with cols[1]: kpi("사용 지표", "6개", "전력·무효전력·역률·불평형")
    with cols[2]: kpi("전체 IF 이상", "5,617건", "contamination=1.00%", "teal")
    with cols[3]: kpi("예비건조기 이상", "702건", "설비 내 1.62%", "red")
    with cols[4]: kpi("예비건조기 순위", "1위", "13개 설비 중", "gold")

    st.write("")
    c1, c2 = st.columns([1.65, 1])
    with c1:
        d = equipment.sort_values("if_anomaly_rate_pct", ascending=True).copy()
        d["group"] = np.where(d["module(equipment)"] == summary["target_module"], "예비건조기", "기타")
        fig = px.bar(d, x="if_anomaly_rate_pct", y="module(equipment)", orientation="h", color="group", text=d["if_anomaly_rate_pct"].map(lambda x:f"{x:.2f}%"), color_discrete_map={"예비건조기":COLORS["red"],"기타":COLORS["teal"]}, labels={"if_anomaly_rate_pct":"이상률 (%)","module(equipment)":"","group":""}, hover_data=["if_anomaly_count","observation_count","avg_powerfactor","avg_active_power"])
        fig.update_layout(showlegend=False)
        style_fig(fig, 600, False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(contribution.sort_values("contribution"), x="contribution", y="feature_label", orientation="h", color="contribution", color_continuous_scale=[COLORS["blue"], COLORS["teal"]], labels={"contribution":"점수 변화량","feature_label":""})
        fig.update_layout(coloraxis_showscale=False)
        style_fig(fig, 330, False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            """
            <div class="panel-note">
            6개 지표를 StandardScaler로 표준화하고 Isolation Forest(n_estimators=200, contamination=0.01)를 적용했다.<br><br>
            기여도는 각 변수를 표준화 평균(0)으로 고정했을 때 이상점수 평균이 얼마나 변하는지로 근사했다. 전류·전압 불평형률이 가장 높다.
            </div>
            """, unsafe_allow_html=True)
    st.dataframe(equipment.sort_values("screening_rank"), hide_index=True, use_container_width=True)


# =========================================================
# 7. Detection-method page
# =========================================================
elif page == "탐지 방법론":
    c = st.columns(4)
    with c[0]: kpi("IQR", "20,317건", "0.78% · 단일 지표 규칙", "teal")
    with c[1]: kpi("EWMA", "26,244건", "1.01% · 3σ 관리도", "gold")
    with c[2]: kpi("정밀 IF", "20,736건", "0.80% · 다변량 비지도")
    with c[3]: kpi("EWMA 이벤트", "25,991개", "평균 지속 5초", "red")

    st.write("")
    a, b = st.columns([1.1, 1.4])
    with a:
        d = detection.copy(); d["rate_pct"] = d["anomaly_rate"]*100
        fig = px.bar(d, x="method", y="rate_pct", color="method", text="rate_pct", color_discrete_map={"IQR":COLORS["teal"],"EWMA":COLORS["yellow"],"Isolation Forest":COLORS["purple"]}, labels={"method":"","rate_pct":"탐지 비율 (%)"})
        fig.update_traces(texttemplate="%{text:.2f}%")
        fig.update_layout(showlegend=False)
        style_fig(fig, 380, False)
        st.plotly_chart(fig, use_container_width=True)
    with b:
        long = overlap.melt(id_vars=["pair","jaccard"], value_vars=["a_only","both","b_only"], var_name="type", value_name="count")
        long["type"] = long["type"].map({"a_only":"A만 탐지","both":"공통 탐지","b_only":"B만 탐지"})
        fig = px.bar(long, x="pair", y="count", color="type", barmode="stack", color_discrete_map={"A만 탐지":COLORS["teal"],"공통 탐지":COLORS["purple"],"B만 탐지":COLORS["yellow"]}, labels={"pair":"","count":"포인트 수","type":""})
        style_fig(fig, 380, True)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns([1.4, 1])
    with c1:
        fig = go.Figure(go.Bar(x=hourly["datetime_hour"], y=hourly["event_count"], marker_color=COLORS["cyan"]))
        fig.add_hline(y=summary["high_frequency_threshold"], line_dash="dash", line_color=COLORS["red"], annotation_text="고빈도 기준 10.93")
        style_fig(fig, 360, False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.dataframe(overlap, hide_index=True, use_container_width=True, height=240)
        st.markdown(
            f"""
            <div class="panel-note">
            IQR 이상 20,317건 중 EWMA가 놓친 건은 0건이며, EWMA는 5,927건을 추가 탐지했다.<br><br>
            EWMA와 정밀 IF는 16,179건을 공통 탐지하고, IF는 EWMA가 놓친 4,557건을 추가 포착했다.<br><br>
            시간당 평균 이벤트는 {summary['mean_hourly_events']:.2f}건이며, 10.93건 초과 시간을 고빈도 구간으로 정의했다.
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# 8. Prediction validation
# =========================================================
elif page == "예측 검증":
    st.markdown('<div class="section-title">역률 변수 포함·제외 ROC-AUC</div>', unsafe_allow_html=True)
    model = st.selectbox("모델", prediction["model"].unique())
    p = prediction[prediction["model"] == model].copy()
    long = p.melt(id_vars=["prediction_window","model"], value_vars=["with_powerfactor_auc","without_powerfactor_auc"], var_name="condition", value_name="auc")
    long["condition"] = long["condition"].map({"with_powerfactor_auc":"역률 포함","without_powerfactor_auc":"역률 제외"})
    fig = px.bar(long, x="prediction_window", y="auc", color="condition", barmode="group", color_discrete_map={"역률 포함":COLORS["cyan"],"역률 제외":COLORS["red"]}, range_y=[.45,.70], labels={"prediction_window":"예측 범위","auc":"ROC-AUC","condition":""})
    fig.add_hline(y=.5, line_dash="dash", line_color=COLORS["yellow"], annotation_text="무작위 수준 AUC=0.5")
    style_fig(fig, 480, True)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    with c1: kpi("역률 포함 범위", "0.63~0.66", "세 모델·네 예측 조건")
    with c2: kpi("역률 제외 범위", "0.49~0.51", "무작위 예측 수준", "red")
    with c3: kpi("최종 방향", "탐지형", "예측형 조기경보 기각", "teal")
    st.markdown(
        """
        <div class="panel-note">
        불평형 피처를 포함한 초기 모델은 일정 수준의 AUC를 보였지만, 과거 역률 변수(powerfactor_lag)를 제거하면 모든 모델과 모든 예측 범위에서 AUC가 약 0.5로 붕괴했다. 따라서 예측 성능은 불평형 지표의 선행 신호가 아니라 역률 자체의 단기 자기상관에서 기인한다. 대시보드의 주 기능은 미래 위험 확률이 아니라 현재 이상 상태와 고빈도 구간의 탐지다.
        </div>
        """, unsafe_allow_html=True)
    st.dataframe(prediction, hide_index=True, use_container_width=True)


# =========================================================
# 9. Data quality / EDA
# =========================================================
elif page == "데이터 품질":
    c = st.columns(6)
    with c[0]: kpi("원본 행 수", "33,696,013", "5초 간격")
    with c[1]: kpi("설비", "13종", "RTU 수집")
    with c[2]: kpi("수집 공백", "0건", "150일 무중단", "teal")
    with c[3]: kpi("값 결측", "0건", "보간 전 기준", "teal")
    with c[4]: kpi("계량기 롤오버", "0건", "누적값 감소 없음", "teal")
    with c[5]: kpi("전압 범위 이탈", "0건", "물리 기준", "teal")

    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("통계적 IQR 이상", "20,317건", "전체 0.0603% · 대부분 15번", "red")
        st.markdown('<div class="panel-note">설비별 Q1−3×IQR ~ Q3+3×IQR 기준. 유효전력과 전류 이상은 0건이며, 3상 역률 채널에서만 유사한 비율로 발생했다.</div>', unsafe_allow_html=True)
    with c2:
        kpi("시간대 효과", "η²=0.00002", "최대−최소 변동폭 0.061%", "")
        st.markdown('<div class="panel-note">최고 4시 3,010.7W, 최저 14시 3,008.9W. 가정 피크 시간과 그 외 시간의 평균도 3,009.88W와 3,009.97W로 사실상 동일하다.</div>', unsafe_allow_html=True)
    with c3:
        kpi("설비 간 차이", "η²<0.0001", "평균 3,008.7~3,010.7W", "")
        st.markdown('<div class="panel-note">예비건조기의 평균 유효전력은 약 3,010.4W로 다른 설비와 유사하지만 역률 채널만 상대적으로 불안정하다.</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown(
        """
        <div class="panel-note">
        timestamp와 localtime 사이에 8시간의 고정 차이가 확인되어 분석 기준 시각은 localtime으로 통일했다. 수치형 변수는 float32로 다운캐스팅하고, 전압·전류 불평형률, 평균 역률, 무효/유효 전력비, 누적전력 증분을 생성한 뒤 1분·5분 데이터로 리샘플링했다.
        </div>
        """, unsafe_allow_html=True)


# =========================================================
# 10. Event log
# =========================================================
elif page == "이벤트 로그":
    min_date = events["start_datetime"].min().date()
    max_date = events["start_datetime"].max().date()
    d = st.date_input("기간", value=(max(min_date, max_date-pd.Timedelta(days=6)), max_date), min_value=min_date, max_value=max_date)
    if isinstance(d, tuple) and len(d) == 2:
        s, e = d
    else:
        s = e = d
    min_agree = st.selectbox("최소 모델 일치 수", [1,2,3], index=0)
    ev = filter_range(events, "start_datetime", s, e)
    ev = ev[ev["max_model_agreement"] >= min_agree].sort_values("start_datetime", ascending=False)

    c = st.columns(4)
    with c[0]: kpi("이벤트 수", f"{len(ev):,}", "선택 기간")
    with c[1]: kpi("최저 역률", f"{ev['minimum_powerfactor'].min():.2f}" if len(ev) else "-", "선택 이벤트", "red")
    with c[2]: kpi("평균 지속", f"{ev['duration_seconds'].mean():.1f}초" if len(ev) else "-", "순간 스파이크", "gold")
    with c[3]: kpi("2개 이상 일치", f"{(ev['max_model_agreement']>=2).sum():,}", "우선 점검 후보", "teal")
    st.dataframe(ev, hide_index=True, use_container_width=True, height=580)
    st.download_button("선택 이벤트 CSV 다운로드", ev.to_csv(index=False).encode("utf-8-sig"), "selected_events.csv", "text/csv")
    
