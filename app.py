import calendar

# 年月の選択
unique_months = sorted(df['年月'].unique())
selected_month = st.selectbox("📅 分析する月を選んでください", unique_months)

# 選んだ月に絞り込み
df_month = df[df['年月'] == selected_month]

# 月の日数を取得（稼働率計算に使用）
year, month = map(int, selected_month.split('-'))
days_in_month = calendar.monthrange(year, month)[1]

# 集計処理（施設別）
summary = df_month.groupby('物件名').agg({
    '販売': 'sum',
    '平均宿泊単価': 'mean',
    'リードタイム（日）': 'mean',
    '合計日数': 'sum'
}).reset_index()

# 稼働率（最大100%）
summary['稼働率'] = (summary['合計日数'] / days_in_month).clip(upper=1.0)  # 1.0 = 100%
summary['稼働率'] = (summary['稼働率'] * 100).round(1).astype(str) + '%'

# 合計サマリー（画面上部に表示）
st.subheader(f"📈 {selected_month} の全体サマリー")
st.write(f"✅ 総売上: {df_month['販売'].sum():,.0f} 円")
st.write(f"✅ 平均宿泊単価: {df_month['平均宿泊単価'].mean():,.0f} 円")
st.write(f"✅ 平均リードタイム: {df_month['リードタイム（日）'].mean():.1f} 日")

# 表の表示
st.subheader("🏠 施設別集計（選択月）")
st.dataframe(summary[['物件名', '販売', '平均宿泊単価', 'リードタイム（日）', '稼働率']])

# 選択式でグラフ対象の施設を選ぶ
facility_options = df_month['物件名'].unique().tolist()
selected_facilities = st.multiselect("📊 グラフで表示したい施設を選んでください", facility_options, default=facility_options[:3])

if selected_facilities:
    st.subheader("📉 グラフ表示（選択施設）")
    metric = st.selectbox("表示する指標", ['販売', '平均宿泊単価', 'リードタイム（日）'])

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
else:
    st.info("施設を1つ以上選んでください。")
