# streamlit_app.py
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="MBTI by Country", layout="centered")
st.title("🌍 Countries by MBTI Type (Top 10)")

uploaded_file = st.file_uploader("📤 countriesMBTI_16types.csv 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    mbti_types = [c for c in df.columns if c != "Country"]
    selected_type = st.selectbox("MBTI 유형 선택:", mbti_types)

    top10 = df[["Country", selected_type]].sort_values(by=selected_type, ascending=False).head(10)
    top10["percent"] = top10[selected_type] * 100

    chart = (
        alt.Chart(top10)
        .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(
            x=alt.X("percent:Q", title="비율 (%)"),
            y=alt.Y("Country:N", sort="-x", title="국가"),
            color=alt.Color("percent:Q", scale=alt.Scale(scheme="tealblues"), legend=None),
            tooltip=["Country", alt.Tooltip("percent:Q", format=".2f", title="비율 (%)")],
        )
        .properties(width=600, height=400, title=f"{selected_type} 유형이 높은 국가 TOP 10")
    )

    st.altair_chart(chart, use_container_width=True)
    st.dataframe(top10, use_container_width=True)
else:
    st.info("CSV 파일을 업로드하면 시각화를 시작할 수 있습니다.")
