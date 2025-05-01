import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import AMD_Tools4 as amd
import matplotlib.pyplot as plt

# --- 気象要素の一覧（日本語名 + 記号） ---
ELEMENT_OPTIONS = {
    "日平均気温 (TMP_mea)": "TMP_mea",
    "日最高気温 (TMP_max)": "TMP_max",
    "日最低気温 (TMP_min)": "TMP_min",
    "降水量 (APCP)": "APCP",
    "降水量高精度 (APCPRA)": "APCPRA",
    "降水の有無 (OPR)": "OPR",
    "日照時間 (SSD)": "SSD",
    "全天日射量 (GSR)": "GSR",
    "下向き長波放射量 (DLR)": "DLR",
    "相対湿度 (RH)": "RH",
    "風速 (WIND)": "WIND",
    "積雪深 (SD)": "SD",
    "積雪水量 (SWE)": "SWE",
    "降雪水量 (SFW)": "SFW",
    "予報気温の確からしさ (PTMP)": "PTMP"
}

# --- タイトル ---
st.title("気象データ取得＋可視化アプリ")
st.write("地図で地点を選び、気象要素を可視化します。")

# --- 地図で座標選択 ---
st.subheader("1. 地図で圃場地点をクリックして選択")
m = folium.Map(location=[35.0, 135.0], zoom_start=6)
m.add_child(folium.LatLngPopup())
st_map = st_folium(m, height=400, width=700)

lat = lon = None
if st_map and st_map.get("last_clicked"):
    lat = st_map["last_clicked"]["lat"]
    lon = st_map["last_clicked"]["lng"]
    st.success(f"選択された座標：緯度 {lat:.4f}, 経度 {lon:.4f}")
else:
    st.warning("地図をクリックして地点を選択してください。")

# --- 入力フォーム ---
st.subheader("2. 取得期間と気象要素の指定")
start_date = st.date_input("開始日")
end_date = st.date_input("終了日")
selected_labels = st.multiselect("取得する気象要素（記号付き）", list(ELEMENT_OPTIONS.keys()), default=["日平均気温 (TMP_mea)"])

# --- 実行処理 ---
if st.button("データを取得して表示"):
    if not lat or not lon:
        st.error("地図から地点を選択してください。")
    elif start_date >= end_date:
        st.error("終了日は開始日より後の日付にしてください。")
    elif not selected_labels:
        st.error("1つ以上の気象要素を選択してください。")
    else:
        try:
            itsu = [str(start_date), str(end_date)]
            doko = [lat, lat, lon, lon]
            records = {}

            for label in selected_labels:
                code = ELEMENT_OPTIONS[label]
                data, tim, _, _ = amd.GetMetData(code, itsu, doko)
                records[label] = data[:, 0, 0]

            df = pd.DataFrame(records)
            df.insert(0, "日付", [str(t) for t in tim])

            st.subheader("3. データ表示")
            st.dataframe(df)

            st.subheader("4. 折れ線グラフ（要素ごと）")
            for label in selected_labels:
                st.write(f"### {label} の推移")
                fig, ax = plt.subplots()
                ax.plot(df["日付"], df[label], marker='o')
                ax.set_xlabel("日付")
                ax.set_ylabel(label)
                ax.tick_params(axis='x', labelrotation=45)
                st.pyplot(fig)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")