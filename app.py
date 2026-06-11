import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.title("ADC資料散佈圖描繪器")

# 1. 檔案上傳
uploaded_file = st.file_uploader("請上傳單行資料的 CSV 檔", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file,header=None, names=["ADC/Voltage"])
    total_rows = len(df)
    df["TimeUnit"] = df.index

    # 初始化 Session State 來同步卷軸與輸入框
    if 'start_idx' not in st.session_state:
        st.session_state.start_idx = 0
        st.session_state.end_idx = min(5000, total_rows)

    # 2. 控制介面 (兩個輸入框 + 卷軸操作)
    col1, col2 = st.columns(2)
    start = col1.number_input("起始索引", 0, total_rows-1, st.session_state.start_idx)
    end = col2.number_input("結束索引", 0, total_rows, st.session_state.end_idx)

    page_slider = st.slider("瀏覽區間", 0, total_rows, (start, end))
    #full_render = st.checkbox("允許逐筆繪圖，最多100,000 (可能變慢)",value=False)

# 建議在檔案最上方設定一個常數，方便管理
    MAX_POINTS_WITHOUT_SAMPLING = 200000 

    # 3. 邏輯處理：縮放與分頁
    display_df = df.iloc[start:end]

    if len(display_df) > MAX_POINTS_WITHOUT_SAMPLING:
        # 當資料量大於設定的閾值時，才進行抽樣
        target = MAX_POINTS_WITHOUT_SAMPLING
        n = len(display_df)
        step = int(np.ceil(n / target))
        # 限制 step 不要太大，避免跳太兇導致訊號失真
        step = min(step, 10)
        display_df = display_df.iloc[::step]
        st.warning(f"資料量大於 {MAX_POINTS_WITHOUT_SAMPLING:,} 筆，已啟用自動抽樣以維持流暢度")
    #else:
        # 安全保護
    #    if len(display_df) > 100000:
    #        st.error(f"目前區間共有 {len(display_df):,} 筆資料，超過安全上限 100,000 筆，請縮小範圍。")
    #        st.stop()

    # 4. 繪圖 (散佈圖)
    df = display_df.reset_index()
    fig = px.scatter(display_df, x="TimeUnit", y="ADC/Voltage",title="時間序列散佈圖",render_mode="webgl")


    # 顯示圖表
    st.plotly_chart(fig, use_container_width=True)

    # 5. 卷軸控制 (使用 slider 模擬分頁)
    if page_slider != (start, end):
        st.session_state.start_idx, st.session_state.end_idx = page_slider
        st.rerun() # 自動重繪
