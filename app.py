# app.py

import streamlit as st
import pandas as pd
import calendar

st.set_page_config(page_title="売上比較アプリ", layout="wide")
st.title("📊 年度別 売上データ比較アプリ")

st.markdown("2つの年度のCSVをアップロードして、同じ月の売上や指標を比較できます。")

# アップロード欄
col1, col2 = st.columns(2)
with col1:
    file1 = st.file_uploader("📂 データ①（前年など）", type="csv", key="file1")
with col2:
    file2 = st.file_uploader("📂 データ②（今年など）", type="csv", key="file2")

# 両方ともアップロードされたら処理開始
if file1 and file2:
    # データ読み込み
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # 日付変換
    for df in [df1, df2]:
        df['チェックイン'] = pd.to_datetime(df['チェックイン'])
        df['予約日'] = pd.to_datetime(df['予約日'])
        df['年月'] = df['チェックイン'].dt.to_period('M').astype(str)
        df['リードタイム（日）'] = (df['チェックイン'] - df['予約日']).dt.days
        df['平均宿泊単価'] = df['販売'] / df['合計日数']

    # ✅ 月選択（例：6月）
    all_months = sorted(set(df1['チェックイン'].dt.month.unique()) | set(df2['チェックイン'].dt.month.unique()))
    target_month = st.selectbox("🗓 比較対象の月を選んでください", all_months)

    # 年ごとにフィルター
    df1_filtered = df1[df1['チェックイン'].dt.month == target_month]
    df2_filtered = df2[df2['チェックイン'].dt.month == target_month]

    # 年を自動判定
    year1 = df1_filtered['チェックイン'].dt.year.min()
    year2 = df2_filtered['チェックイン'].dt.year.min()

    # 月の日数取得（稼働率計算用）
    days_in_month = calendar.monthrange(year2, target_month)[1]  # 最新年を基準に

    # 集計処理
    def summarize(df):
        grouped = df.groupby('物件名').agg({
            '販売': 'sum',
            '平均宿泊単価': 'mean',
            'リードタイム（日）': 'mean',
            '合計日数': 'sum'
        }).reset_index()
        grouped['稼働率'] = (grouped['合計日数'] / days_in_month).clip(upper=1.0)
        return grouped

    summary1 = summarize(df1_filtered)
    summary2 = summarize(df2_filtered)

    # 比較用のマージ
    merged = pd.merge(summary1, summary2, on="物件名", how="outer", suffixes=(f'_{year1}', f'_{year2}'))
    merged.fillna(0, inplace=True)  # データがない物件は0で埋める

    # 差分列の追加（例：販売_差分）
    merged['販売_差分'] = merged[f'販売_{year2}'] - merged[f'販売_{year1}']
    merged['平均宿泊単価_差分'] = merged[f'平均宿泊単価_{year2}'] - merged[f'平均宿泊単価_{year1}']
    merged['リードタイム_差分'] = merged[f'リードタイム（日）_{year2}'] - merged[f'リードタイム（日）_{year1}']

    # 表示
    st.subheader(f"📋 {year1}年 vs {year2}年 - {target_month}月 比較表（施設別）")
    st.dataframe(merged)

    # CSVダウンロード
    download = merged.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 比較結果をCSVでダウンロード",
        data=download,
        file_name=f"comparison_{year1}_vs_{year2}_month{target_month}.csv",
        mime='text/csv'
    )
else:
    st.info("2つのCSVファイルをアップロードしてください。")
