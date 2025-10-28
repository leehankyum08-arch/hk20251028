import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="✈️ 항공 네트워크 효율 분석 대시보드", layout="wide")

@st.cache_data
def load_data():
    url_routes = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"
    url_airports = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
    cols_routes = ["Airline","Airline_ID","Source_Airport","Source_ID","Destination_Airport",
                   "Destination_ID","Codeshare","Stops","Equipment"]
    cols_airports = ["Airport_ID","Name","City","Country","IATA","ICAO","Latitude",
                     "Longitude","Altitude","Timezone","DST","Tz_database_time_zone","Type","Source"]
    routes = pd.read_csv(url_routes, names=cols_routes)
    airports = pd.read_csv(url_airports, names=cols_airports)
    return routes, airports

routes, airports = load_data()

st.title("✈️ 항공 네트워크 효율 분석 대시보드")
st.markdown("OpenFlights 데이터를 기반으로 항공사의 네트워크 구조와 효율성을 시각화합니다.")

selected_airline = st.selectbox("항공사 선택:", sorted(routes["Airline"].unique()))
filtered = routes[routes["Airline"] == selected_airline]

tab1, tab2, tab3 = st.tabs(["📍 허브 구조", "📏 거리 효율", "🌐 지역별 연결성"])

# 📍 허브 구조
with tab1:
    hub_counts = (
        filtered.groupby("Source_Airport")["Destination_Airport"]
        .count()
        .reset_index(name="Destinations")
        .sort_values("Destinations", ascending=False)
        .head(10)
    )

    chart = (
        alt.Chart(hub_counts)
        .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(
            x=alt.X("Destinations:Q", title="연결 노선 수"),
            y=alt.Y("Source_Airport:N", sort="-x", title="출발 공항"),
            color=alt.Color("Destinations:Q", scale=alt.Scale(scheme="blues"), legend=None),
            tooltip=["Source_Airport", "Destinations"]
        )
        .properties(title=f"{selected_airline}의 주요 허브공항", width=600, height=400)
    )

    st.altair_chart(chart, use_container_width=True)
    st.dataframe(hub_counts)

# 📏 거리 효율
with tab2:
    merged = filtered.merge(airports[["IATA", "Latitude", "Longitude"]],
                            left_on="Source_Airport", right_on="IATA", how="left") \
                     .merge(airports[["IATA", "Latitude", "Longitude"]],
                            left_on="Destination_Airport", right_on="IATA", how="left",
                            suffixes=("_src", "_dst"))

    merged = merged.dropna(subset=["Latitude_src", "Latitude_dst"])

    # 거리 계산 (단순 구면 근사)
    import numpy as np
    R = 6371  # km
    def haversine(lat1, lon1, lat2, lon2):
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1))*np.cos(np.radians(lat2))*np.sin(dlon/2)**2
        return 2 * R * np.arcsin(np.sqrt(a))

    merged["Distance_km"] = haversine(
        merged["Latitude_src"], merged["Longitude_src"],
        merged["Latitude_dst"], merged["Longitude_dst"]
    )

    chart2 = (
        alt.Chart(merged)
        .mark_bar()
        .encode(
            x=alt.X("Distance_km:Q", bin=alt.Bin(maxbins=30), title="노선 거리 (km)"),
            y=alt.Y("count():Q", title="노선 수"),
            tooltip=[alt.Tooltip("count():Q", title="노선 수")]
        )
        .properties(title=f"{selected_airline} 노선 거리 분포", width=600, height=400)
    )
    st.altair_chart(chart2, use_container_width=True)

    avg_dist = merged["Distance_km"].mean()
    st.metric("평균 노선 거리 (km)", f"{avg_dist:,.0f}")

# 🌐 지역별 연결성 (국가 기반)
with tab3:
    top_countries = (
        filtered.merge(airports[["IATA","Country"]], left_on="Destination_Airport", right_on="IATA")
        .groupby("Country")["Destination_Airport"]
        .count()
        .reset_index(name="Routes")
        .sort_values("Routes", ascending=False)
        .head(10)
    )

    chart3 = (
        alt.Chart(top_countries)
        .mark_circle(size=200)
        .encode(
            x=alt.X("Country:N", sort="-y", title="국가"),
            y=alt.Y("Routes:Q", title="노선 수"),
            color=alt.Color("Routes:Q", scale=alt.Scale(scheme="oranges")),
            tooltip=["Country", "Routes"]
        )
        .properties(title=f"{selected_airline}의 지역별 연결성", width=700, height=400)
    )

    st.altair_chart(chart3, use_container_width=True)
    st.dataframe(top_countries)
