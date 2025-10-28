# streamlit_app.py
import streamlit as st
import pandas as pd
import altair as alt

# ----------------------------------------------------
# 1. 데이터 로드
# ----------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

df = load_data()

# ----------------------------------------------------
# 2. 기본 UI 구성
# ----------------------------------------------------
st.set_page_config(page_title="MBTI by Country", layout="centered")
st.title("🌍 Countries by MBTI Type (Top 10)")
st.markdown(
    """
    특정 **MBTI 유형**을 선택하면,  
    해당 유형 비율이 가장 높은 **국가 상위 10개**를 시각적으로 보여줍니다.
    """
)

# ----------------------------------------------------
# 3. 유형 선택
# ----------------------------------------------------
mbti_types = [c for c in df.columns if c != "Country"]
selected_type = st.selectbox("MBTI 유형을 선택하세요:", mbti_types, index=0)

# ----------------------------------------------------
# 4. 상위 10개 국가 계산
# ----------------------------------------------------
top10 = df[["Country", selected_type]].sort_values(by=selected_type, ascending=False).head(10)

# 비율(%) 변환
top10["percent"] = top10[selected_type] * 100

# ----------------------------------------------------
# 5. Altair 차트 생성
# ----------------------------------------------------
bar_chart = (
    alt.Chart(top10)
    .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
    .encode(
        x=alt.X("percent:Q", title="비율 (%)", scale=alt.Scale(domain=[0, top10["percent"].max() * 1.1])),
        y=alt.Y("Country:N", sort="-x", title="국가"),
        color=alt.Color("percent:Q", scale=alt.Scale(scheme="tealblues"), legend=None),
        tooltip=[
            alt.Tooltip("Country:N", title="국가"),
            alt.Tooltip("percent:Q", title="비율 (%)", format=".2f"),
        ],
    )
    .properties(width=600, height=400, title=f"{selected_type} 유형이 높은 국가 TOP 10")
    .configure_axis(labelFontSize=12, titleFontSize=13)
    .configure_title(fontSize=18, anchor="middle")
)

# ----------------------------------------------------
# 6. 출력
# ----------------------------------------------------
st.altair_chart(bar_chart, use_container_width=True)

st.markdown("#### 📋 데이터 미리보기")
st.dataframe(top10.reset_index(drop=True), use_container_width=True)

# ----------------------------------------------------
# 7. 간단한 통계 문장
# ----------------------------------------------------
avg_val = df[selected_type].mean() * 100
st.markdown(
    f"**{selected_type}** 유형의 전체 평균 비율은 **{avg_val:.2f}%** 입니다."
)
