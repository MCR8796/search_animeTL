import streamlit as st
import json
from datetime import datetime, timedelta
from collections import defaultdict

# アニメの放送日時を格納したJSONファイルの読み込み
with open('anime_schedule.json', 'r', encoding='utf-8') as f:
    anime_schedule = json.load(f)

# 現在の日時を取得
current_datetime = datetime.now()

# UIの作成
st.title("アニメ検索用プロンプト生成")

# 曜日番号と曜日名のマッピング
week_to_day = {
    1: "月",
    2: "火",
    3: "水",
    4: "木",
    5: "金",
    6: "土",
    7: "日",
    8: "その他"
}

# 放送曜日ごとにアニメをグループ化
anime_by_day = defaultdict(list)

# 曜日情報を基にアニメをグループ化
for anime in anime_schedule:
    day_name = week_to_day.get(anime['week'])
    if day_name:
        anime_by_day[day_name].append(anime['title'])

# 曜日のリスト
days_of_week = ["月", "火", "水", "木", "金", "土", "日", "その他"]

# 曜日ごとにプルダウンメニューを表示
selected_day = st.selectbox('放送曜日を選択', days_of_week)

# 選択した曜日のアニメタイトルをプルダウンで表示
anime_titles_for_day = anime_by_day[selected_day]

if anime_titles_for_day:
    # アニメタイトルを選択
    anime_title = st.selectbox(f'アニメタイトルを選択', anime_titles_for_day)
else:
    st.warning(f"{selected_day}曜日に放送されているアニメはありません。")


# 話数の選択
anime = next(item for item in anime_schedule if item['title'] == anime_title)

broadcast_year = anime['year']
broadcast_month = anime['month']
broadcast_day = anime['day']
broadcast_hour = anime['hour']
broadcast_minute = anime['minute']

# 放送開始日時（1話目の放送開始日時）
first_broadcast_start = datetime(broadcast_year, broadcast_month, broadcast_day, broadcast_hour, broadcast_minute)

# 放送済みの話数（現在日時より前の話数を計算）
episodes = []
broadcast = []
for i, week in enumerate(anime['broadcast']):
    # 放送開始日時から週番号を基に放送日時を計算
    broadcast_start = first_broadcast_start + timedelta(weeks=i)
    if week is not None:
        # 現在日時より前の放送分を計算
        if broadcast_start <= (current_datetime + timedelta(weeks=1)):
            episodes.append(week)
            broadcast.append(broadcast_start)

episode = st.selectbox('話数を選択', episodes)
# 選択肢のインデックスを取得
selected_index = episodes.index(episode)

# 放送時間の設定
start_offset = st.number_input('検索範囲（デフォ：1分前）', min_value=0, value=1)
end_offset = st.number_input('検索範囲（デフォ：3分後）', min_value=0, value=3)
delay_time = st.number_input('放送遅延（分）', value=0)

# 指定された週番号に基づいて放送日を計算
episode_week = broadcast[selected_index]
# 放送開始日時（例: 1話の放送開始）
broadcast_start = episode_week
broadcast_end = broadcast_start + timedelta(minutes=30)  # 仮の放送終了日時（30分後）

# 検索時間の計算
search_start = broadcast_start - timedelta(minutes=start_offset - delay_time)
search_end = broadcast_end + timedelta(minutes=end_offset + delay_time)

# JSTに変換（例として日本時間で表示）
search_start_str = search_start.strftime('%Y-%m-%d_%H:%M:%S') + "_JST"
search_end_str = search_end.strftime('%Y-%m-%d_%H:%M:%S') + "_JST"

# プロンプトの生成
prompt = f"list:1761552900252488071 since:{search_start_str} until:{search_end_str} include:nativeretweets"
st.code(f"{prompt}")
