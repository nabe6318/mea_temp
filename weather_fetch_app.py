import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import AMD_Tools4 as amd
import matplotlib.pyplot as plt

# --- タイトル ---
st.title("気象データ取得＋可視化アプリ")
st.write("地図で地点を選び、複数の気象要素を一括取得・グラフ表示・CSV保存できます。")

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
elements = st.multiselect("取得する気象要素", [
    'TMP_mea',  # 日平均気温
    'TMP_max',  # 日最高気温
    'TMP_min',  # 日最低気温
    'PRE',      # 降水量
    'RAD',      # 日射量
    'SUN'       # 日照時間
], default=['TMP_mea'])

filename = st.text_input("保存するCSVファイル名（例：weather_data.csv）", value="weather_data.csv")

# --- 実行処理 ---
if st.button("データを取得して表示"):
    if not lat or not lon:
        st.error("地図から地点を選択してください。")
    elif start_date >= end_date:
        st.error("終了日は開始日より後の日付にしてください。")
    elif not elements:
        st.error("1つ以上の気象要素を選択してください。")
    elif not filename.endswith(".csv"):
        st.error("ファイル名は .csv で終わってください。")
    else:
        try:
            itsu = [str(start_date), str(end_date)]
            doko = [lat, lat, lon, lon]
            records = {}

            # 各気象要素について取得＆格納
            for el in elements:
                data, tim, _, _ = amd.GetMetData(el, itsu, doko)
                records[el] = data[:, 0, 0]

            # DataFrame化
            df = pd.DataFrame(records)
            df.insert(0, "date", [str(t) for t in tim])

            # 表示
            st.subheader("3. データ表示")
            st.dataframe(df)

            # グラフ表示
            st.subheader("4. 折れ線グラフ（要素ごと）")
            for el in elements:
                st.write(f"### {el} の推移")
                fig, ax = plt.subplots()
                ax.plot(df["date"], df[el], marker='o')
                ax.set_xlabel("日付")
                ax.set_ylabel(el)
                ax.tick_params(axis='x', labelrotation=45)
                st.pyplot(fig)

            # 保存
            df.to_csv(filename, index=False)
            st.success(f"CSVファイルとして「{filename}」を保存しました。")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")