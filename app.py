import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import calendar

st.title("売上データ分析アプリ")

uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded_file:
    # CSV読み込み
    df = pd.read_csv(uploaded_file)
    df['チェックイン'] = pd.to_datetime(df['チェックイン'])
    df['予約日'] = pd.to_datetime(df['予約日'])

    # 年月列を追加
    df['年月'] = df['チェックイン'].dt.to_period('M').astype(str)
    df['リードタイム（日）'] = (df['チェックイン'] - df['予約日']).dt.days
    df['平均宿泊単価'] = df['販売'] / df['合計日数']

    # 対象月の選択
    unique_months = sorted(df['年月'].unique())
    selected_month = st.selectbox("📅 分析する月を選んでください", unique_months)

    # 対象月でフィルター
    df_month = df[df['年月'] == selected_month]
    year, month = map(int, selected_month.split('-'))
    days_in_month = calendar.monthrange(year, month)[1]

    # 施設別集計
    summary = df_month.groupby('物件名').agg({
        '販売': 'sum',
        '平均宿泊単価': 'mean',
        'リードタイム（日）': 'mean',
        '合計日数': 'sum'
    }).reset_index()

    # 稼働率の計算と整形
    summary['稼働率'] = (summary['合計日数'] / days_in_month).clip(upper=1.0)
    summary['稼働率'] = (summary['稼働率'] * 100).round(1).astype(str) + '%'

    # 月間の合計を表示
    st.subheader(f"📈 {selected_month} の全体サマリー")
    st.write(f"✅ 総売上: {df_month['販売'].sum():,.0f} 円")
    st.write(f"✅ 平均宿泊単価: {df_month['平均宿泊単価'].mean():,.0f} 円")
    st.write(f"✅ 平均リードタイム: {df_month['リードタイム（日）'].mean():.1f} 日")

    # 表表示
    st.subheader("🏠 施設別集計（選択月）")
    st.dataframe(summary[['物件名', '販売', '平均宿泊単価', 'リードタイム（日）', '稼働率']])

    # グラフ対象施設選択
    facility_options = df_month['物件名'].unique().tolist()
    selected_facilities = st.multiselect("📊 グラフで表示する施設を選んでください", facility_options, default=facility_options[:3])

    if selected_facilities:
        metric = st.selectbox("📈 表示指標を選んでください", ['販売', '平均宿泊単価', 'リードタイム（日）'])

        plt.figure(figsize=(10, 5))
        for name in selected_facilities:
            facility_data = df_month[df_month['物件名'] == name]
            plt.plot(facility_data['チェックイン'], facility_data[metric], marker='o', label=name)

        plt.xlabel("チェックイン日")
        plt.ylabel(metric)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt)
