# contributter-ranking-bot

[![PyPI](
  https://img.shields.io/pypi/v/contributter-ranking-bot?color=blue
)](
  https://pypi.org/project/contributter-ranking-bot/
) [![Maintainability](
  https://api.codeclimate.com/v1/badges/8e7faa6da2e464a07b4e/maintainability
)](
  https://codeclimate.com/github/eggplants/contributter-ranking-bot/maintainability
)

[![Run Bot](
  https://github.com/eggplants/contributter-ranking-bot/actions/workflows/cron.yml/badge.svg
)](
  https://github.com/eggplants/contributter-ranking-bot/actions/workflows/run.yml
) [![Release Package](
  https://github.com/eggplants/contributter-ranking-bot/actions/workflows/release.yml/badge.svg
)](
  https://github.com/eggplants/contributter-ranking-bot/actions/workflows/release.yml
) [![pages-build-deployment](
  https://github.com/eggplants/contributter-ranking-bot/actions/workflows/pages/pages-build-deployment/badge.svg
)](
  https://github.com/eggplants/contributter-ranking-bot/actions/workflows/pages/pages-build-deployment
) [![pre-commit.ci](
  https://results.pre-commit.ci/badge/github/eggplants/contributter-ranking-bot/main.svg
)](
  https://results.pre-commit.ci/latest/github/eggplants/contributter-ranking-bot/main
)

[contributter](https://contributter.potato4d.me/)を使っているユーザーの1日のcontribute数トップ3をメンション付きで自動ツイートするbotです。

- Original: [![Twitter Follow](https://img.shields.io/twitter/follow/_who_is_king_)](https://twitter.com/_who_is_king_)
  - → Forked: [![Twitter Follow](https://img.shields.io/twitter/follow/satoch_bot)](https://twitter.com/satoch_bot)

## 処理機構

1. 昨日の`#contributter_report`のついたツイート内のcontribution数とユーザーIDを取得
2. contribution数を集計してランキング化
3. ランキング上位3人をメンションしてcontribution数を記載し、自動ツイート
