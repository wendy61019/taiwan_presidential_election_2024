# 練習專案四：找出章魚里

## 簡介

這個專案「找出章⿂⾥」透過中選會選舉及公投資料庫的 [2024 ー 第16任總統副總統選舉](https://db.cec.gov.tw/ElecTable/Election/ElecTickets?dataType=tickets&typeId=ELC&subjectId=P0&legisId=00&themeId=4d83db17c1707e3defae5dc4d4e9c800&dataLevel=N&prvCode=00&cityCode=000&areaCode=00&deptCode=000&liCode=0000)的資料計算全台灣 7700 餘個村鄰⾥的得票率，並將其與全國得票率相比較，針對兩個報章媒體的不合理論點提出反思。

1. ⼈⼝結構會變動、選舉有不同類型，將⼀個特定村鄰⾥訂為⻑年不變的章⿂⾥是明顯不合理的。
2. 「得票率跟最終結果非常相近」的定義非常模糊。

我們使⽤了 `pandas` 與 `sqlite3` 建立了資料庫，利⽤ `numpy` 進⾏概念驗證，並以 `gradio` 與 `streamlit` 做出成品。
 -  `gradio` 可以點選 [Hugging Face gradio的連結](https://huggingface.co/spaces/namidairo321/taiwan_presidential_election_2024)參考成品。
 - `streamlit`可以點選 [Hugging Face streamlit的連結](https://huggingface.co/spaces/namidairo321/taiwan_presidential_election_2024_streamlit)參考成品。

## 如何重現
 - 安裝 [Miniconda](https://docs.anaconda.com/miniconda)
 - 依據 `environment.yml` 建立環境：

```bash
conda env create -f environment.yml
```

 - 將 `data/` 資料夾中的「總統-A05-4-候選⼈得票數⼀覽表-各投開票所」22 個試算
表檔案放到專案資料夾的 `data/` 資料夾中
 - 啟動環境並執⾏ `python create_taiwan_presidential_election_2024_db.py`
就能在 `data/` 資料夾中建立 `taiwan_presidential_election_2024.db`
 - 啟動環境並執⾏ `python app.py` 並前往 `http://127.0.0.1:7860` 瀏覽成品
 - 啟動環境並執⾏ `streamlit run app_streamlit.py` 並前往 `http://192.168.1.103:8501` 瀏覽成品