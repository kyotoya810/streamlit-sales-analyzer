# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# タイトルを表示
st.title("売上データ分析アプリ")

# ファイルアップロード欄を表示
uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded_file:
    # アップロードされたCSVをDataFrameとして読み込む
    df = pd.read_csv(uploaded_file)

    # 日付の列をdatetime型に変換（重要：計算に必要）
    df['チェックイン'] = pd.to_datetime(df['チェックイン'])
    df['予約日'] = pd.to_datetime(df['予約日'])

    # 年月を追加（「2024-05」の形式で月を識別）
    df['年月'] = df['チェックイン'].dt.to_period('M').astype(str)

    # リードタイム列（チェックイン日 - 予約日）
    df['リードタイム（日）'] = (df['チェックイン'] - df['予約日']).dt.days

    # 平均宿泊単価（販売 ÷ 合計日数）
    df['平均宿泊単価'] = df['販売'] / df['合計日数']

    # 稼働率（合計日数 ÷ 30）
    df['稼働率'] = df['合計日数'] / 30

    # 月×施設ごとにグループ化して集計
    summary = df.groupby(['年月', '物件名']).agg({
        '販売': 'sum',
        '平均宿泊単価': 'mean',
        'リードタイム（日）': 'mean',
        '稼働率': 'mean'
    }).reset_index()

    # 集計結果を見やすく縦型表示
    st.subheader("📊 集計結果（施設 × 月）")
    st.dataframe(summary)

    # CSVでダウンロードできるようにする
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv_data = convert_df_to_csv(summary)
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv_data,
        file_name='summary.csv',
        mime='text/csv'
    )

    # グラフで表示したい項目を選択
    graph_option = st.selectbox("📈 グラフで表示する指標を選んでください", 
                                ['販売', '平均宿泊単価', 'リードタイム（日）', '稼働率'])

    st.subheader(f"📈 {graph_option} の推移（施設別）")

    # グラフを描画
    plt.figure(figsize=(10, 5))
    for name, group in summary.groupby('物件名'):
        plt.plot(group['年月'], group[graph_option], label=name)

    plt.xlabel("年月")
    plt.ylabel(graph_option)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)
