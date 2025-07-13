from datetime import datetime, timedelta, timezone

import folium
import pandas as pd
import plotly.express as px
import requests
import reverse_geocoder as rg
import streamlit as st
from folium.plugins import MarkerCluster, TimestampedGeoJson
from streamlit_folium import st_folium

# JST設定
JST = timezone(timedelta(hours=9))


# 地震データ取得（USGS API）
def fetch_earthquake_data(start_date, end_date):
    url = (
        f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson"
        f"&starttime={start_date}&endtime={end_date}"
        f"&minlatitude=24&maxlatitude=46&minlongitude=122&maxlongitude=146"
    )
    res = requests.get(url)
    data = res.json()
    recs = []
    for f in data["features"]:
        lon, lat, depth = f["geometry"]["coordinates"]
        props = f["properties"]
        recs.append(
            {
                "発生時刻": datetime.utcfromtimestamp(props["time"] / 1000).astimezone(
                    JST
                ),
                "マグニチュード": props["mag"],
                "深さ（km）": depth,
                "緯度": lat,
                "経度": lon,
            }
        )
    return pd.DataFrame(recs)


# 緯度経度から都道府県・市区町村
def reverse_geo(df):
    results = rg.search(list(zip(df["緯度"], df["経度"])), mode=1)
    df["都道府県"] = [r["admin1"] for r in results]
    df["市区町村"] = [r["name"] for r in results]
    df["地域"] = df["都道府県"] + " - " + df["市区町村"]
    return df


# 色設定
def get_marker_color(mag):
    if mag is None:
        return "gray"
    if mag >= 6:
        return "red"
    if mag >= 4:
        return "orange"
    return "yellow"


# Streamlit 設定
st.set_page_config(layout="wide")
st.title("地震データ可視化アプリ")

if "df" not in st.session_state:
    st.session_state.df = None

col1, col2 = st.columns(2)
with col1:
    start_dt = st.date_input("開始日", datetime(2025, 6, 1))
with col2:
    end_dt = st.date_input("終了日", datetime(2025, 7, 12))

if start_dt > end_dt:
    st.warning("開始日は終了日より前にしてください。")
elif st.button("地震データ取得"):
    with st.spinner("地震データ取得中..."):
        df = fetch_earthquake_data(
            start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")
        )
        if df.empty:
            st.error("該当する地震データがありません。")
        else:
            df = reverse_geo(df)
            st.session_state.df = df
            st.success(f"{len(df)}件の地震データを取得しました。")

df = st.session_state.df
if df is not None:
    tab = st.radio(
        "表示形式を選択",
        [
            "地図",
            "クラスタリング地図",
            "タイムスライダー地図",
            "マグニチュード別棒グラフ",
            "市区町村別件数",
            "地域別深度推移",
            "データ表",
        ],
    )

    if tab == "地図":
        m = folium.Map([36, 138], zoom_start=5)
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row["緯度"], row["経度"]],
                radius=(row["マグニチュード"] or 1) * 1.5,
                color=get_marker_color(row["マグニチュード"]),
                fill=True,
                fill_color=get_marker_color(row["マグニチュード"]),
                fill_opacity=0.6,
                popup=f"{row['地域']}<br>M{row['マグニチュード']:.1f}, 深さ: {row['深さ（km）']}km<br>{row['発生時刻']}",
            ).add_to(m)
        st_folium(m, width=800, height=600)

    elif tab == "クラスタリング地図":
        m = folium.Map([36, 138], zoom_start=5)
        cluster = MarkerCluster().add_to(m)
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row["緯度"], row["経度"]],
                radius=3,
                color=get_marker_color(row["マグニチュード"]),
                fill=True,
                fill_color=get_marker_color(row["マグニチュード"]),
                fill_opacity=0.6,
                popup=f"M{row['マグニチュード']:.1f}, 深さ: {row['深さ（km）']}km",
            ).add_to(cluster)
        st_folium(m, width=800, height=600)

    elif tab == "タイムスライダー地図":
        features = []
        for _, r in df.iterrows():
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [r["経度"], r["緯度"]],
                    },
                    "properties": {
                        "time": r["発生時刻"].isoformat(),
                        "style": {
                            "color": get_marker_color(r["マグニチュード"]),
                            "radius": r["マグニチュード"] * 1.5,
                        },
                        "popup": f"M{r['マグニチュード']:.1f}, 深さ{r['深さ（km）']}km",
                    },
                }
            )
        m = folium.Map([36, 138], zoom_start=5)
        TimestampedGeoJson(
            {"type": "FeatureCollection", "features": features},
            period="PT1H",
            add_last_point=True,
            auto_play=False,
            loop=False,
        ).add_to(m)
        st_folium(m, width=800, height=600)

    elif tab == "マグニチュード別棒グラフ":
        bins = pd.cut(
            df["マグニチュード"], [0, 3.9, 5.9, 10], labels=["M<4", "M4-6", "M6+"]
        )
        count = bins.value_counts().sort_index()
        fig = px.bar(
            x=count.index,
            y=count.values,
            labels={"x": "マグニチュード帯", "y": "件数"},
            title="マグニチュード別 地震件数",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif tab == "市区町村別件数":
        top = df["地域"].value_counts().nlargest(20)
        fig = px.bar(
            x=top.index,
            y=top.values,
            labels={"x": "地域", "y": "件数"},
            title="市区町村別 地震件数 上位20",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif tab == "地域別深度推移":
        region = st.selectbox("地域を選択", df["地域"].unique())
        mag_filter = st.selectbox(
            "マグニチュードで絞り込み", ["すべて", "M<4", "M4-6", "M6+"]
        )
        sub = df[df["地域"] == region]
        if mag_filter == "M<4":
            sub = sub[sub["マグニチュード"] < 4]
        elif mag_filter == "M4-6":
            sub = sub[(sub["マグニチュード"] >= 4) & (sub["マグニチュード"] < 6)]
        elif mag_filter == "M6+":
            sub = sub[sub["マグニチュード"] >= 6]
        sub = sub.sort_values("発生時刻")
        if not sub.empty:
            fig = px.line(
                sub,
                x="発生時刻",
                y="深さ（km）",
                title=f"{region} 地域の地震深度推移",
                labels={"発生時刻": "発生時刻", "深さ（km）": "深さ（km）"},
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("該当するデータがありません。")

    elif tab == "データ表":
        st.dataframe(df)

    # CSV ダウンロード
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 CSVダウンロード", data=csv, file_name="earthquake_data.csv", mime="text/csv"
    )
