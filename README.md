# contributter-ranking-bot

contributterを使っているユーザーの1日のcontribute数トップ3をメンション付きで自動ツイートするbotです。

実際のbot: <https://twitter.com/_who_is_king_>

詳細記事: <https://zenn.dev/shuntatakemoto/articles/00264c2b366612>

## 処理機構

1. 昨日の#contributter_reportのついたツイート内のcontribution数とユーザーIDを取得
2. contribution数を集計してランキング化
3. ランキング上位3人をメンションしてcontribution数を記載し、自動ツイート
