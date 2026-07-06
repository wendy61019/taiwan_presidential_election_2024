import sqlite3
import numpy as np
import pandas as pd
import gradio as gr

def create_gradio_dataframe():
#計算全國得票率 向量a
    connection = sqlite3.connect("data/taiwan_presidential_election_2024.db")
    votes_by_village = pd.read_sql("""SELECT * FROM votes_by_village;""" , con=connection)
    connection.close()
    total_votes = votes_by_village["sum_votes"].sum()
    country_percentage = votes_by_village.groupby("id")["sum_votes"].sum() / total_votes
    vector_a = country_percentage.values

#計算村鄰⾥得票率 向量bi
    groupby_variables = ["county", "town", "village"]
    village_total_votes = votes_by_village.groupby(groupby_variables)["sum_votes"].sum().reset_index()
    merged = pd.merge(votes_by_village, village_total_votes, left_on=groupby_variables, right_on=groupby_variables,
                    how="left")
    merged["village_percentage"] = merged["sum_votes_x"] / merged["sum_votes_y"]
    merged = merged[["county", "town", "village", "id", "village_percentage"]]
    pivot_df = merged.pivot(index=["county", "town", "village"], columns="id",
                            values="village_percentage").reset_index()
    pivot_df = pivot_df.rename_axis(None, axis=1)

#計算餘弦相似度
    cosine_similarities = []
    for row in pivot_df.iterrows():
        vector_bi = np.array([row[1][1], row[1][2], row[1][3]])
        vector_a_dot_vector_bi = np.dot(vector_a, vector_bi)
        length_vector_a = pow((vector_a**2).sum(), 0.5)
        length_vector_bi = pow((vector_bi**2).sum(), 0.5)
        cosine_similarity = vector_a_dot_vector_bi / (length_vector_a*length_vector_bi)
        cosine_similarities.append(cosine_similarity)

#建⽴最後的資料框
    cosine_similarity_df = pivot_df.iloc[:, :]
    cosine_similarity_df["cosine_similarity"] = cosine_similarities
    cosine_similarity_df = cosine_similarity_df.sort_values(["cosine_similarity", "county", "town", "village"],
                                                            ascending=[False, True, True, True])
    cosine_similarity_df = cosine_similarity_df.reset_index(drop=True).reset_index()
    cosine_similarity_df["index"] = cosine_similarity_df["index"] + 1
    column_names_to_revise = {
        "index": "rank",
        1: "candidate_1",
        2: "candidate_2",
        3: "candidate_3"
    }
    cosine_similarity_df = cosine_similarity_df.rename(columns=column_names_to_revise)
    return vector_a, cosine_similarity_df

def filter_county_town_village(df, county_name, town_name, village_name):
    county_condition = df["county"] == county_name
    town_condition = df["town"] == town_name
    village_condition = df["village"] == village_name
    return df[county_condition & town_condition & village_condition]

country_percentage, gradio_dataframe = create_gradio_dataframe()
ko_wu, lai_hsiao, hou_chao = country_percentage

#建立可以篩選指定村鄰⾥的介面
interface = gr.Interface(fn=filter_county_town_village,
                         inputs=[
                                    gr.DataFrame(gradio_dataframe),
                                    "text",
                                    "text",
                                    "text"
                                ],
                         outputs="dataframe",
                         title="找出章魚里",
                         description=f"輸⼊你想篩選的縣市、鄉鎮市區與村鄰⾥。（柯吳配, 賴蕭配, 侯趙配）= ({ko_wu:.6}, {lai_hsiao:.6}, {hou_chao:.6})")
interface.launch()