
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==================================================
# 1. 기본 설정
# ==================================================

st.set_page_config(
    page_title="영화 관객 데이터 분석실",
    page_icon="🎬",
    layout="wide"
)

# ==================================================
# 2. 전체 디자인 CSS
# ==================================================

st.markdown("""
<style>

/* 전체 배경 */
.stApp {
    background-color: #F3F7FC;
}

/* 기본 글씨 */
.stApp {
    color: #263B55;
}

/* 메인 제목 */
.main-title {
    font-size: 34px;
    font-weight: 800;
    color: #183B65 !important;
}

/* 부제목 */
.sub-title {
    color: #526D8A !important;
    font-size: 16px;
}

/* 섹션 제목 */
.section-title {
    font-size: 23px;
    font-weight: 750;
    color: #244B78 !important;
    padding-top: 12px;
}

/* 분석 질문 */
.question {
    background-color: #E2EDFA;
    padding: 13px 17px;
    border-radius: 10px;
    color: #244B78 !important;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 15px;
}

.question * {
    color: #244B78 !important;
}

/* 일반 설명 */
.stMarkdown p {
    color: #344B65;
}

/* 캡션 */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
    color: #52647A !important;
}

/* 입력 항목 제목 */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p {
    color: #263B55 !important;
    font-weight: 600 !important;
}

/* 입력 상자 */
.stSelectbox div,
.stDateInput div {
    color: #263B55;
}

/* 메트릭 카드 */
div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border-radius: 12px;
    padding: 15px;
    border: 1px solid #DCE7F3;
}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #244B78 !important;
}

/* 알림 메시지 */
[data-testid="stAlert"] p {
    color: #263B55 !important;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background-color: #E8F0FA;
}

section[data-testid="stSidebar"] * {
    color: #263B55;
}

/* 슬라이더 */
[data-testid="stSlider"] p {
    color: #263B55 !important;
}

/* 구분선 */
hr {
    border-color: #CFDCEC;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# 3. 데이터 불러오기
# ==================================================

DATA_URL = (
    "https://raw.githubusercontent.com/"
    "greatsong/my-data-log/refs/heads/main/"
    "data/kobis_daily_log.csv"
)


@st.cache_data
def load_data():

    df = pd.read_csv(
        DATA_URL,
        encoding="utf-8-sig"
    )

    # 날짜 변환
    date_text = df["날짜"].astype(str).str.strip()

    df["날짜"] = pd.to_datetime(
        date_text,
        format="%Y%m%d",
        errors="coerce"
    )

    # 날짜 형식이 YYYY-MM-DD인 경우도 처리
    missing_date = df["날짜"].isna()

    df.loc[missing_date, "날짜"] = pd.to_datetime(
        date_text[missing_date],
        errors="coerce"
    )

    # 숫자형 변수 변환
    numeric_cols = [
        "순위",
        "일관객",
        "누적관객",
        "스크린수",
        "상영횟수"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col], errors="coerce"
            )

    df = df.dropna(
        subset=["날짜", "영화명", "일관객"]
    )

    df["영화명"] = df["영화명"].astype(str)

    df["요일"] = df["날짜"].dt.day_name()
    df["월"] = df["날짜"].dt.month

    return df


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()


# 필수 열 확인
required_columns = [
    "날짜", "영화명", "일관객",
    "누적관객", "스크린수", "순위"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(
        "CSV에 필요한 열이 없습니다: "
        + ", ".join(missing_columns)
    )
    st.stop()


# ==================================================
# 4. 제목
# ==================================================

st.markdown(
    '<div class="main-title">🎬 영화 관객 데이터 분석실</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'KOBIS 일별 박스오피스 데이터를 활용한 영화 흥행 분석'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ==================================================
# 5. 전체 데이터 요약
# ==================================================

st.subheader("📊 데이터 한눈에 보기")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "전체 기록 수",
        f"{len(df):,}개"
    )

with col2:
    st.metric(
        "분석 영화 수",
        f"{df['영화명'].nunique():,}편"
    )

with col3:
    st.metric(
        "전체 기록 관객 수 합계",
        f"{df['일관객'].sum():,.0f}명"
    )

with col4:
    st.metric(
        "데이터 기간",
        f"{df['날짜'].min():%Y.%m.%d} ~ "
        f"{df['날짜'].max():%Y.%m.%d}"
    )

st.divider()


# ==================================================
# 6. 분석 기간 설정
# ==================================================

st.subheader("🗓️ 분석 기간 설정")

date_range = st.date_input(
    "분석할 날짜를 선택하세요.",
    value=(
        df["날짜"].min().date(),
        df["날짜"].max().date()
    ),
    min_value=df["날짜"].min().date(),
    max_value=df["날짜"].max().date()
)

if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
    st.warning("시작 날짜와 종료 날짜를 모두 선택하세요.")
    st.stop()

start_date, end_date = date_range

if start_date > end_date:
    st.error("시작 날짜가 종료 날짜보다 늦을 수 없습니다.")
    st.stop()

filtered = df[
    (df["날짜"].dt.date >= start_date) &
    (df["날짜"].dt.date <= end_date)
].copy()

if filtered.empty:
    st.warning("선택한 기간에 데이터가 없습니다.")
    st.stop()

st.caption(
    f"현재 분석 기간: {start_date} ~ {end_date}"
)

st.divider()


# ==================================================
# 7. 사이드바 메뉴
# ==================================================

st.sidebar.title("🎬 분석 메뉴")

menu = st.sidebar.radio(
    "원하는 분석을 선택하세요.",
    [
        "전체 그래프",
        "1. 선 그래프",
        "2. 다중 선 그래프",
        "3. 영역 그래프",
        "4. 가로 막대 그래프",
        "5. 히트맵",
        "6. 도넛 그래프",
        "7. 트리맵",
        "8. 히스토그램",
        "9. 산점도",
        "10. 박스플롯",
        "11. 버블 그래프",
        "12. 선버스트"
    ]
)


# ==================================================
# 8. 그래프 공통 함수
# ==================================================

def show_question(question):

    st.markdown(
        f'<div class="question">'
        f'🔍 분석 질문: {question}'
        f'</div>',
        unsafe_allow_html=True
    )


def show_chart(fig):

    fig.update_layout(
        template="plotly_white",

        # 그래프 배경
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",

        # 전체 글씨
        font=dict(
            family="Malgun Gothic, sans-serif",
            color="#263B55",
            size=13
        ),

        # 제목
        title_font=dict(
            color="#183B65",
            size=19
        ),

        # 축
        xaxis=dict(
            title_font=dict(color="#263B55"),
            tickfont=dict(color="#52647A"),
            gridcolor="#E5EBF2",
            zerolinecolor="#CBD5E1"
        ),

        yaxis=dict(
            title_font=dict(color="#263B55"),
            tickfont=dict(color="#52647A"),
            gridcolor="#E5EBF2",
            zerolinecolor="#CBD5E1"
        ),

        # 범례
        legend=dict(
            font=dict(color="#263B55"),
            bgcolor="rgba(255,255,255,0.8)"
        ),

        # 마우스 올렸을 때
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font=dict(
                color="#263B55",
                size=13
            ),
            bordercolor="#CBD5E1"
        ),

        margin=dict(
            l=30,
            r=30,
            t=60,
            b=30
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        theme=None
    )


def genre_unavailable():

    st.info(
        "현재 CSV에는 영화 장르 정보가 없습니다. "
        "장르 정보가 추가되면 이 그래프를 사용할 수 있습니다."
    )


# ==================================================
# 9. 1. 선 그래프
# ==================================================

def line_chart():

    st.markdown(
        '<div class="section-title">📈 1. 선 그래프</div>',
        unsafe_allow_html=True
    )

    show_question(
        "한 영화의 관객은 개봉 후 어떻게 변하나?"
    )

    movies = sorted(filtered["영화명"].unique())

    selected = st.selectbox(
        "분석할 영화를 선택하세요.",
        movies,
        key="single_movie"
    )

    data = filtered[
        filtered["영화명"] == selected
    ].sort_values("날짜").copy()

    first_date = data["날짜"].min()

    data["경과일"] = (
        data["날짜"] - first_date
    ).dt.days

    fig = px.line(
        data,
        x="경과일",
        y="일관객",
        markers=True,
        title=f"{selected}의 관객 수 변화",
        hover_data=["날짜", "누적관객"],
        labels={
            "경과일": "첫 관측일 이후 경과일",
            "일관객": "일일 관객 수 (명)"
        }
    )

    show_chart(fig)

    st.caption(
        "※ 실제 개봉일이 아니라 선택한 분석 기간에서 "
        "해당 영화가 처음 관측된 날을 기준으로 합니다."
    )


# ==================================================
# 10. 2. 다중 선 그래프
# ==================================================

def multi_line_chart():

    st.markdown(
        '<div class="section-title">📈 2. 다중 선 그래프</div>',
        unsafe_allow_html=True
    )

    show_question(
        "흥행 대작들의 곡선은 서로 닮았나?"
    )

    top_n = st.slider(
        "비교할 영화 수",
        2, 10, 5,
        key="multi_n"
    )

    top_movies = (
        filtered.groupby("영화명")["누적관객"]
        .max()
        .nlargest(top_n)
        .index.tolist()
    )

    data = filtered[
        filtered["영화명"].isin(top_movies)
    ].copy()

    data = data.sort_values("날짜")

    first_dates = (
        data.groupby("영화명")["날짜"]
        .transform("min")
    )

    data["경과일"] = (
        data["날짜"] - first_dates
    ).dt.days

    data["기준 관객"] = (
        data.groupby("영화명")["일관객"]
        .transform("first")
    )

    data["관객 지수"] = np.where(
        data["기준 관객"] > 0,
        data["일관객"] / data["기준 관객"] * 100,
        np.nan
    )

    fig = px.line(
        data,
        x="경과일",
        y="관객 지수",
        color="영화명",
        title="흥행 영화별 관객 변화 패턴 비교",
        labels={
            "경과일": "첫 관측일 이후 경과일",
            "관객 지수": "관객 변화 지수 (첫 관측일=100)"
        }
    )

    show_chart(fig)

    st.caption(
        "영화마다 첫 관측일의 관객 수를 100으로 설정하여 "
        "관객 변화 형태를 비교합니다."
    )


# ==================================================
# 11. 3. 영역 그래프
# ==================================================

def area_chart():

    st.markdown(
        '<div class="section-title">📊 3. 영역 그래프</div>',
        unsafe_allow_html=True
    )

    show_question(
        "1년 중 극장이 가장 붐빈 날은 언제인가?"
    )

    daily = (
        filtered.groupby("날짜", as_index=False)
        ["일관객"].sum()
    )

    fig = px.area(
        daily,
        x="날짜",
        y="일관객",
        title="날짜별 전체 기록 관객 수",
        labels={
            "날짜": "날짜",
            "일관객": "일일 관객 수 합계 (명)"
        }
    )

    show_chart(fig)

    peak = daily.loc[
        daily["일관객"].idxmax()
    ]

    st.success(
        f"가장 관객이 많았던 기록일: "
        f"{peak['날짜']:%Y년 %m월 %d일} "
        f"({peak['일관객']:,.0f}명)"
    )

    st.caption(
        "※ 일별 박스오피스 10위권에 기록된 영화의 합계입니다. "
        "극장 전체 관객 수와는 다를 수 있습니다."
    )


# ==================================================
# 12. 4. 가로 막대 그래프
# ==================================================

def bar_chart():

    st.markdown(
        '<div class="section-title">📊 4. 가로 막대 그래프</div>',
        unsafe_allow_html=True
    )

    show_question(
        "이 기간에 관객이 가장 많았던 영화는 무엇인가?"
    )

    top_n = st.slider(
        "표시할 영화 수",
        5, 20, 10,
        key="bar_n"
    )

    ranking = (
        filtered.groupby("영화명", as_index=False)
        ["일관객"].sum()
        .sort_values("일관객", ascending=False)
        .head(top_n)
    )

    fig = px.bar(
        ranking.sort_values("일관객"),
        x="일관객",
        y="영화명",
        orientation="h",
        text="일관객",
        title="기간 내 영화별 관객 수 합계",
        labels={
            "일관객": "기간 내 관객 수 합계 (명)",
            "영화명": "영화명"
        }
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}명",
        textposition="outside"
    )

    show_chart(fig)

    st.caption(
        "※ 선택 기간의 일일 관객 수를 합산한 결과입니다. "
        "10위권 밖의 날짜는 누락될 수 있습니다."
    )


# ==================================================
# 13. 5. 히트맵
# ==================================================

def heatmap_chart():

    st.markdown(
        '<div class="section-title">🔥 5. 히트맵</div>',
        unsafe_allow_html=True
    )

    show_question(
        "월 × 요일로 보면 언제 관객이 몰리나?"
    )

    data = filtered.copy()

    weekday_order = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    weekday_korean = {
        "Monday": "월요일",
        "Tuesday": "화요일",
        "Wednesday": "수요일",
        "Thursday": "목요일",
        "Friday": "금요일",
        "Saturday": "토요일",
        "Sunday": "일요일"
    }

    pivot = data.pivot_table(
        index="월",
        columns="요일",
        values="일관객",
        aggfunc="sum",
        fill_value=0
    )

    pivot = pivot.reindex(
        index=range(1, 13),
        columns=weekday_order,
        fill_value=0
    )

    pivot.columns = [
        weekday_korean[c] for c in pivot.columns
    ]

    fig = px.imshow(
        pivot,
        text_auto=".2s",
        aspect="auto",
        color_continuous_scale="Blues",
        title="월별 · 요일별 관객 수"
    )

    fig.update_layout(
        xaxis_title="요일",
        yaxis_title="월"
    )

    show_chart(fig)


# ==================================================
# 14. 6. 도넛 그래프
# ==================================================

def donut_chart():

    st.markdown(
        '<div class="section-title">🍩 6. 도넛 그래프</div>',
        unsafe_allow_html=True
    )

    show_question(
        "10위권에 든 영화의 장르 구성은?"
    )

    genre_unavailable()


# ==================================================
# 15. 7. 트리맵
# ==================================================

def treemap_chart():

    st.markdown(
        '<div class="section-title">🌳 7. 트리맵</div>',
        unsafe_allow_html=True
    )

    show_question(
        "장르 안에서 어떤 영화가 컸나?"
    )

    genre_unavailable()


# ==================================================
# 16. 8. 히스토그램
# ==================================================

def histogram_chart():

    st.markdown(
        '<div class="section-title">📊 8. 히스토그램</div>',
        unsafe_allow_html=True
    )

    show_question(
        "영화 대부분은 관객이 몇 명쯤인가?"
    )

    fig = px.histogram(
        filtered,
        x="일관객",
        nbins=40,
        title="일일 관객 수 분포",
        labels={
            "일관객": "일일 관객 수 (명)",
            "count": "기록 수"
        }
    )

    show_chart(fig)

    st.caption(
        "각 영화의 날짜별 관객 수가 어느 구간에 "
        "많이 분포하는지 확인합니다."
    )


# ==================================================
# 17. 9. 산점도
# ==================================================

def scatter_chart():

    st.markdown(
        '<div class="section-title">🔵 9. 산점도</div>',
        unsafe_allow_html=True
    )

    show_question(
        "스크린을 많이 받은 영화가 관객도 많나?"
    )

    fig = px.scatter(
        filtered,
        x="스크린수",
        y="일관객",
        color="순위",
        hover_name="영화명",
        hover_data=["날짜", "상영횟수"],
        title="스크린 수와 일일 관객 수의 관계",
        labels={
            "스크린수": "스크린 수",
            "일관객": "일일 관객 수 (명)",
            "순위": "박스오피스 순위"
        }
    )

    show_chart(fig)

    corr = filtered[
        ["스크린수", "일관객"]
    ].corr().iloc[0, 1]

    st.metric(
        "스크린 수와 관객 수의 상관계수",
        f"{corr:.3f}" if pd.notna(corr) else "계산 불가"
    )

    st.caption(
        "상관관계가 나타나더라도 스크린 수가 관객 수 증가의 "
        "직접적인 원인이라고 단정할 수는 없습니다."
    )


# ==================================================
# 18. 10. 박스플롯
# ==================================================

def boxplot_chart():

    st.markdown(
        '<div class="section-title">📦 10. 박스플롯</div>',
        unsafe_allow_html=True
    )

    show_question(
        "장르별 관객 분포는 어떻게 다른가?"
    )

    genre_unavailable()


# ==================================================
# 19. 11. 버블 그래프
# ==================================================

def bubble_chart():

    st.markdown(
        '<div class="section-title">🫧 11. 버블 그래프</div>',
        unsafe_allow_html=True
    )

    show_question(
        "첫 주 관객까지 넣으면 무엇이 더 보이나?"
    )

    data = filtered.sort_values("날짜").copy()

    # 영화코드가 있으면 영화별 구분에 사용
    group_col = (
        "영화코드"
        if "영화코드" in data.columns
        else "영화명"
    )

    first_dates = (
        data.groupby(group_col)["날짜"]
        .transform("min")
    )

    data["경과일"] = (
        data["날짜"] - first_dates
    ).dt.days

    first_week = data[
        data["경과일"] < 7
    ]

    summary = (
        first_week.groupby(
            [group_col, "영화명"],
            as_index=False
        )
        .agg(
            첫주관객=("일관객", "sum"),
            최대스크린수=("스크린수", "max"),
            최대누적관객=("누적관객", "max")
        )
    )

    summary = summary[
        summary["첫주관객"] > 0
    ]

    if summary.empty:
        st.warning("분석할 데이터가 없습니다.")
        return

    fig = px.scatter(
        summary,
        x="첫주관객",
        y="최대누적관객",
        size="최대스크린수",
        color="최대스크린수",
        hover_name="영화명",
        title="영화별 첫 7일 관객 수와 누적 관객 수",
        labels={
            "첫주관객": "첫 7일 관객 수 (명)",
            "최대누적관객": "최대 기록 누적 관객 수 (명)",
            "최대스크린수": "최대 스크린 수"
        },
        size_max=55,
        color_continuous_scale="Blues"
    )

    show_chart(fig)

    st.caption(
        "※ 첫 7일은 실제 개봉일이 아니라 "
        "데이터에서 처음 관측된 날부터 계산합니다."
    )


# ==================================================
# 20. 12. 선버스트
# ==================================================

def sunburst_chart():

    st.markdown(
        '<div class="section-title">☀️ 12. 선버스트</div>',
        unsafe_allow_html=True
    )

    show_question(
        "국가에서 장르로 내려가면 무엇이 보일까?"
    )

    st.info(
        "현재 CSV에는 국가와 장르 정보가 없습니다. "
        "영화별 국가 및 장르 데이터가 추가되면 "
        "계층형 선버스트 그래프를 구현할 수 있습니다."
    )


# ==================================================
# 21. 전체 그래프
# ==================================================

def all_charts():

    line_chart()
    st.divider()

    multi_line_chart()
    st.divider()

    area_chart()
    st.divider()

    bar_chart()
    st.divider()

    heatmap_chart()
    st.divider()

    histogram_chart()
    st.divider()

    scatter_chart()
    st.divider()

    bubble_chart()
    st.divider()

    st.subheader("추가 분석: 장르 및 국가 데이터 필요")

    donut_chart()
    st.divider()

    treemap_chart()
    st.divider()

    boxplot_chart()
    st.divider()

    sunburst_chart()


# ==================================================
# 22. 메뉴 실행
# ==================================================

if menu == "전체 그래프":
    all_charts()

elif menu == "1. 선 그래프":
    line_chart()

elif menu == "2. 다중 선 그래프":
    multi_line_chart()

elif menu == "3. 영역 그래프":
    area_chart()

elif menu == "4. 가로 막대 그래프":
    bar_chart()

elif menu == "5. 히트맵":
    heatmap_chart()

elif menu == "6. 도넛 그래프":
    donut_chart()

elif menu == "7. 트리맵":
    treemap_chart()

elif menu == "8. 히스토그램":
    histogram_chart()

elif menu == "9. 산점도":
    scatter_chart()

elif menu == "10. 박스플롯":
    boxplot_chart()

elif menu == "11. 버블 그래프":
    bubble_chart()

elif menu == "12. 선버스트":
    sunburst_chart()


# ==================================================
# 23. 하단 안내
# ==================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        color:#526D8A;
        padding:15px;
        font-size:13px;
    ">
        🎬 영화 관객 데이터 분석실<br>
        KOBIS 일별 박스오피스 데이터 활용
    </div>
    """,
    unsafe_allow_html=True
)
