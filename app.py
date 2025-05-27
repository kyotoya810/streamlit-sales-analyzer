# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import calendar

st.set_page_config(page_title="売上データ分析", layout="wide")
st.title("📊 売上データ分析アプリ（施設別・月別）")

uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded_file:
    # データ読み込み
    df = pd.read_csv(uploaded_file)
    df['チェックイン'] = pd.to_datetime(df['チェックイン'])
    df['予約日'] = pd.to_datetime(df['予約日'])

    # 日付情報追加
    df['年月'] = df['チェックイン'].dt.to_period('M').astype(str)
    df['リードタイム（日）'] = (df['チェックイン'] - df['予約日']).dt.days
    df['平均宿泊単価'] = df['販売'] / df['合計日数']

    # 月選択
    unique_months = sorted(df['年月'].unique())
    selected_month = st.selectbox("📅 分析する月を選んでください", unique_months)

    # 該当月にフィルタ
    df_month = df[df['年月'] == selected_month]
    year, month = map(int, selected_month.split('-'))
    days_in_month = calendar.monthrange(year, month)[1]

    # 集計（施設別）
    summary = df_month.groupby('物件名').agg({
        '販売': 'sum',
        '平均宿泊単価': 'mean',
        'リードタイム（日）': 'mean',
        '合計日数': 'sum'
    }).reset_index()

    # 稼働率（最大100%）
    summary['稼働率'] = (summary['合計日数'] / days_in_month).clip(upper=1.0)
    summary['稼働率'] = (summary['稼働率'] * 100).round(1).astype(str) + '%'

    # 全体サマリー
    st.subheader(f"📈 {selected_month} の全体サマリー")
    col1, col2, col3 = st.columns(3)
    col1.metric("総売上", f"{df_month['販売'].sum():,} 円")
    col2.metric("平均宿泊単価", f"{df_month['平均宿泊単価'].mean():,.0f} 円")
    col3.metric("平均リードタイム", f"{df_month['リードタイム（日）'].mean():.1f} 日")

    # 表表示
    st.subheader("🏠 施設別サマリー（選択月）")
    st.dataframe(summary[['物件名', '販売', '平均宿泊単価', 'リードタイム（日）', '稼働率']])

    # ダウンロード
    csv = summary.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 CSVでダウンロード",
        data=csv,
        file_name=f'{selected_month}_summary.csv',
        mime='text/csv'
    )

    # グラフ対象施設選択
    st.subheader("📊 指標別の棒グラフ（日別 × 施設別）")
    facility_options = df_month['物件名'].unique().tolist()
    selected_facilities = st.multiselect("表示する施設を選んでください", facility_options, default=facility_options[:3])

    # 指標選択
    metric = st.selectbox("表示する指標を選んでください", ['販売', '平均宿泊単価', 'リードタイム（日）'])

    if selected_facilities:
        graph_df = df_month[df_month['物件名'].isin(selected_facilities)]
        grouped = graph_df.groupby(['チェックイン', '物件名'])[metric].sum().reset_index()

        # グラフ描画
        plt.figure(figsize=(12, 6))
        for name in selected_facilities:
            subset = grouped[grouped['物件名'] == name]
            x = subset['チェックイン'].dt.strftime('%m-%d')
            y = subset[metric]
            plt.bar(x, y, label=name)

        plt.xlabel("チェックイン日")
        plt.ylabel(metric)
        plt.title(f"{selected_month} の {metric} の日別棒グラフ")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        st.pyplot(plt)
    else:
        st.info("施設を1つ以上選択してください。")
