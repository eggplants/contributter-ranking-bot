# contributter-ranking-bot

[![MIT](
  https://img.shields.io/badge/license-MIT-blue.svg?style=flat
)](
  https://github.com/eggplants/contributter-ranking-bot/blob/main/LICENSE
) [![PyPI](
  https://img.shields.io/pypi/v/contributter-ranking-bot?color=blue
)](
  https://pypi.org/project/contributter-ranking-bot/
) [![Maintainability](
  https://api.codeclimate.com/v1/badges/8e7faa6da2e464a07b4e/maintainability
)](
  https://codeclimate.com/github/eggplants/contributter-ranking-bot/maintainability
)

[![pages-build-deployment](
  https://github.com/eggplants/contributter-ranking-bot/actions/workflows/pages/pages-build-deployment/badge.svg
)](
  https://github.com/eggplants/contributter-ranking-bot/actions/workflows/pages/pages-build-deployment
) [![pre-commit.ci](
  https://results.pre-commit.ci/badge/github/eggplants/contributter-ranking-bot/main.svg
)](
  https://results.pre-commit.ci/latest/github/eggplants/contributter-ranking-bot/main
)

[![Run Bot for test](
  https://github.com/eggplants/contributter-ranking-bot/actions/workflows/cron_test.yml/badge.svg
)](
  https://github.com/eggplants/contributter-ranking-bot/actions/workflows/cron_test.yml
) [![Run Bot](
  https://github.com/eggplants/contributter-ranking-bot/actions/workflows/cron.yml/badge.svg
)](
  https://github.com/eggplants/contributter-ranking-bot/actions/workflows/cron.yml
) [![Release Package](
  https://github.com/eggplants/contributter-ranking-bot/actions/workflows/release.yml/badge.svg
)](
  https://github.com/eggplants/contributter-ranking-bot/actions/workflows/release.yml
)

- [Contributter](https://contributter.potato4d.me/) Ranking Bot for Twitter
- Forked from [shuntatakemoto/contributter-ranking-bot](https://github.com/shuntatakemoto/contributter-ranking-bot)

## Deployment on Twitter

- Original: [![Twitter Follow @who_is_king](https://img.shields.io/twitter/follow/_who_is_king_)](https://twitter.com/_who_is_king_)
  - → Forked: [![Twitter Follow @ContribRankBot](https://img.shields.io/twitter/follow/ContribRankBot)](https://twitter.com/ContribRankBot)

## Installation

```sh
pip install contributter-ranking-bot
# or:
pip install git+https://github.com/eggplants/contributter-ranking-bot
```

## Tweet Format

```txt
✨Contribution Ranking - {YYYY/MM/DD}✨
{prefix} {num}🟩: @{mention_interrupt}{name}
...
{prefix} {num}🟩: @{mention_interrupt}{name}
📊<[ppl: {contrib_n}👤, sum: {contrib_sum}🟩, avg: {avg:.2f}🟩]
#contributter_ranking
```

## CLI Usage

```shellsession
$ crb -h
usage: crb [-h] [-k PATH] [-d DAY] [-w SEC] [-n N] [-q] [-D] [-V]

This command makes Contributter Ranking Bot easier to run.

optional arguments:
  -h, --help                show this help message and exit
  -k PATH, --key PATH       key file (default: None)
  -d DAY, --day-before DAY  n days before (default: 1)
  -w SEC, --wait-sec SEC    interval of retrieving tweets (default: 10)
  -n N, --top-n N           top n to tweet (default: 3)
  -q, --quiet               suppress log print (default: False)
  -D, --dry-run             tweet without mentions (default: False)
  -V, --version             show program's version number and exit

$ cat .twitter.key
CONSUMER_KEY="***"
CONSUMER_SECRET="***"
ACCESS_TOKEN="***"
ACCESS_TOKEN_SECRET="***"

$ crb -k .twitter.key
# Running Bot was successful!
# See at: https://twitter.com/satoch_bot/status/1517223447868448768
{
    "created_at": "Thu Apr 21 19:27:13 +0000 2022",
...
}

# 5 days before, tweet top-five ranking
$ crb -d 5 -n 5 -k .twitter.key
```

## License

MIT
