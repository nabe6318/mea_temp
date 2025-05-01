import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import AMD_Tools4 as amd
import matplotlib.pyplot as plt

# --- 気象要素の記号一覧のみ ---
ELEMENT_OPTIONS = [
    "TMP_mea", "TMP_max", "TMP_min", "APCP", "APCPRA", "OPR", "SSD",
    "GSR", "DLR", "RH", "WIND", "SD", "SWE", "SFW", "PTMP"
]

# --- タイトル ---
st.title("気象データ取得＋可視化アプリ")
st.write("地図で地点を選び、気象要素を可視化します.地図の下が表示されないときは再読込")

# --- 地図で座標選択 ---
st.subheader("1. 地図で地点をクリック")

# foliumマップの作成
m = folium.Map(location=[35.0, 135.0], zoom_start=6, control_scale=True)
m.add_child(folium.LatLngPopup())  # クリック座標表示

# マップを表示し、クリック情報を取得
st_data = st_folium(m, height=500, width=700)

lat = lon = None
if st_data and st_data.get("last_clicked"):
    lat = st_data["last_clicked"]["lat"]
    lon = st_data["last_clicked"]["lng"]
    st.success(f"選択された座標：緯度 {lat:.4f}, 経度 {lon:.4f}")
else:
    st.info("地図をクリックして緯度・経度を選んでください。")

# --- 入力フォーム ---
st.subheader("2. 取得期間と気象要素の指定(26日先まで指定可能)")
start_date = st.date_input("開始日")
end_date = st.date_input("終了日")
selected_codes = st.multiselect("取得する気象要素（記号）", ELEMENT_OPTIONS, default=["TMP_mea", "TMP_max", "TMP_min"])

# -# --- 実行処理 ---
if st.button("データを取得"):
    if not lat or not lon:
        st.error("地図から地点を選択してください。")
    elif start_date >= end_date:
        st.error("終了日は開始日より後の日付にしてください。")
    elif not selected_codes:
        st.error("1つ以上の気象要素を選択してください。")
    else:
        try:
            itsu = [str(start_date), str(end_date)]
            doko = [lat, lat, lon, lon]
            records = {}
            normals = {}
            tim_ref = None

            for code in selected_codes:
                # 実測値取得
                data, tim, _, _ = amd.GetMetData(code, itsu, doko, cli=False)
                records[code + "_AMD"] = data[:, 0, 0]

                # 平年値取得
                norm_data, norm_tim, _, _ = amd.GetMetData(code, itsu, doko, cli=True)
                normals[code + "_NORM"] = norm_data[:, 0, 0]

                if tim_ref is None:
                    tim_ref = tim

            df = pd.DataFrame({**records, **normals})
            # 日付列（月日形式）
            df.insert(0, "Date", [t.strftime("%m/%d") for t in pd.to_datetime(tim_ref)])

            st.subheader("3. データ表示（AMDと平年値）")
            st.dataframe(df)

            st.subheader("4. 折れ線グラフ（AMD vs 平年値）")
            for code in selected_codes:
                actual = code + "_AMD"
                normal = code + "_NORM"
                st.write(f"### {code} の推移")
                fig, ax = plt.subplots()
                ax.plot(df["Date"], df[actual], marker='o', label='AMD')
                ax.plot(df["Date"], df[normal], marker='x', linestyle='--', label='Normal')
                ax.set_xlabel("Date (MM/DD)")
                ax.set_ylabel(code)
                ax.tick_params(axis='x', labelrotation=45)
                ax.legend()
                st.pyplot(fig)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")