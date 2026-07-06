import sqlite3
import numpy as np
import pandas as pd
import streamlit as st

# =====================================================================
# 1. CORE FUNCTIONS (Functional Programming & Vectorized Computations)
# =====================================================================

@st.cache_data
def prepare_data(db_path: str):
    with sqlite3.connect(db_path) as connection:
        votes_by_village = pd.read_sql("SELECT * FROM votes_by_village;", con=connection)

# 計算全國得票率 向量 a
    total_votes = votes_by_village["sum_votes"].sum()
    vector_a = (votes_by_village.groupby("id")["sum_votes"].sum() / total_votes).values

# 計算村鄰里得票率 矩陣 b
    groupby_variables = ["county", "town", "village"]
    village_total_votes = votes_by_village.groupby(groupby_variables)["sum_votes"].transform("sum")
    pivot_df = (
        votes_by_village.assign(village_percentage = votes_by_village["sum_votes"] / village_total_votes)
        .pivot(index=groupby_variables, columns="id", values="village_percentage")
        .reset_index()
        .rename_axis(None, axis=1)
    )
# 矩陣化計算餘弦相似度 (Vectorized Implementation)
    matrix_b = pivot_df.iloc[:, 3:].values
    dot_products = np.dot(matrix_b, vector_a)
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(matrix_b, axis=1)
    cosine_similarities = dot_products / (norm_a * norm_b)

# 建立最後的資料框與排名
    column_names_to_revise = {
        "index": "rank",
        1: "candidate_1",
        2: "candidate_2",
        3: "candidate_3"
    }
    
    cosine_similarity_df = (
        pivot_df.assign(cosine_similarity = cosine_similarities)
        .sort_values(
            ["cosine_similarity", "county", "town", "village"],
            ascending=[False, True, True, True]
            )
            .reset_index(drop=True)
            .reset_index()
            .assign(index=lambda df: df["index"] + 1)
            .rename(columns=column_names_to_revise)
    )
    return vector_a, cosine_similarity_df

# =====================================================================
# 2. STREAMLIT USER INTERFACE
# =====================================================================

#載入資料
country_percentage, main_dataframe = prepare_data("data/taiwan_presidential_election_2024.db")
ko_wu, lai_hsiao, hou_chao = country_percentage

#設置網頁標題與介紹
st.title("🐙找出章魚里")
st.markdown(f"""
輸⼊你想篩選的縣市、鄉鎮市區與村鄰⾥。
<br>
<br>
**全國得票率基準：**
* **柯吳配：** `{ko_wu:.6f}`
* **賴蕭配：** `{lai_hsiao:.6f}`
* **侯趙配：** `{hou_chao:.6f}`
""", unsafe_allow_html=True)

#設置分隔線
st.divider()

#設置下拉選單
st.subheader("🔍 條件篩選")
col1, col2, col3 = st.columns(3)

with col1:
#縣市選單，加入"全部"選項
    county_list = ["全部"] + list(main_dataframe["county"].unique())
    selected_county = st.selectbox("請選擇縣市", county_list)

with col2:
#根據選定的縣市，選擇鄉鎮市區
    if selected_county != "全部":
        filtered_towns = main_dataframe[main_dataframe["county"] ==selected_county]
        unique_towns = list(filtered_towns["town"].unique())
        town_list = ["全部"] + unique_towns
    else:
        town_list = ["全部"]
    selected_town = st.selectbox("請選擇鄉鎮市區", town_list)

with col3:
#根據選定的鄉鎮市區，選擇村里
    if selected_county != "全部" and selected_town != "全部":
        filtered_villages = main_dataframe[
            (main_dataframe["county"] == selected_county) & 
            (main_dataframe["town"] == selected_town)
        ]["village"].unique()
        village_list = ["全部"] + list(filtered_villages)
    else:
        village_list = ["全部"]
    selected_village = st.selectbox("請選擇村鄰⾥", village_list)

# =====================================================================
# 3. DATA FILTERING & DISPLAY
# =====================================================================
    
output_df = main_dataframe.copy()

if selected_county != "全部":
    output_df = output_df[output_df["county"] == selected_county]
if selected_town != "全部":
    output_df = output_df[output_df["town"] == selected_town]
if selected_village != "全部":
    output_df = output_df[output_df["village"] == selected_village]

#呈現結果
st.subheader(f"📊 篩選結果 (共 {len(output_df)} 筆資料)")
st.dataframe(output_df, width="stretch", hide_index=True)