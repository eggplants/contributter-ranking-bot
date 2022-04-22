"""Tweet n-days-before contributter-report ranking."""

from __future__ import annotations

import collections
import datetime
import json
import os
import re
import time
from typing import Any

import dotenv  # type: ignore[import]
import requests_oauthlib  # type: ignore[import]


class ContributterRanking:
    """Create cnotributter ranking and tweets."""

    def __init__(
        self,
        key_path: str | None = "~/.twitter.key",
        day_before: int = 1,
        top_n: int = 3,
        wait_sec: int = 10,
    ) -> None:
        if key_path is not None and os.path.isfile(key_path):
            dotenv.load_dotenv(key_path)

        self.day_before: int = day_before
        self.day_before_str: str = self.get_n_before(self.day_before)

        self.top_n: int = top_n
        self.wait_sec: int = wait_sec
        self.twitter_oauth: requests_oauthlib.OAuth1Session = self.__get_twitter_oauth()

    def set_day_before(self, day_before: int) -> None:
        """Set day."""
        self.day_before: int = day_before
        self.day_before_str: str = self.get_n_before(self.day_before)

    @staticmethod
    def __get_twitter_oauth() -> requests_oauthlib.OAuth1Session:
        """Create a Twitter OAuth Object."""
        CONSUMER_KEY = os.environ["CONSUMER_KEY"]
        CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
        ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
        ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]
        return requests_oauthlib.OAuth1Session(
            CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
        )

    @staticmethod
    def get_n_before(day_before: int = 1) -> str:
        """Get yeaterday date string. (YYYY/MM/DD)"""
        yesterday = datetime.datetime.today() - datetime.timedelta(days=day_before)
        return yesterday.strftime("%Y/%m/%d")

    def run(self) -> tuple[int, dict[str, Any], Any]:
        """Run Bot."""
        tweets = self.get_contributter_tweets()
        if len(tweets) < self.top_n:
            raise ValueError(
                "Number of Retrieved Tweets must be less than expected top_n"
                f"(got: {len(tweets)} < {self.top_n})"
            )
        rank_data = self.parse_contributter_reports(tweets)
        top_n_contributers = self.get_top_contibutters(rank_data, self.top_n)
        stat = self.get_stat(rank_data)
        tweet_result = self.tweet_top_n(top_n_contributers, stat)
        return (
            int(tweet_result.status_code),
            json.loads(str(tweet_result.text)),
            tweet_result,
        )

    def get_contributter_tweets(self) -> list[Any]:
        """Retrieve yesterday's all contributter reports form twitter."""
        max_id = -1
        params = {
            "count": 100,
            "q": f"#contributter_report {self.day_before_str} exclude:retweets",
            "max_id": max_id,
        }
        tweets, statuses = [], None
        while statuses is None or len(statuses) != 0:
            if max_id != -1:
                params["max_id"] = max_id - 1

            req = self.twitter_oauth.get(
                "https://api.twitter.com/1.1/search/tweets.json", params=params
            )
            if req.status_code == 200:
                res: dict[str, Any] = json.loads(req.text)
                statuses = res.get("statuses", [])
                for status in statuses:
                    tweets.append(status)
                max_id = max_id if len(statuses) == 0 else statuses[-1]["id"]
            time.sleep(self.wait_sec)
        else:
            return tweets

    @staticmethod
    def parse_contributter_reports(tweets: Any) -> dict[str, int]:
        """Create a dictionary of tweets usernames and number of contributions."""
        rank_data: dict[str, int] = {}
        for tweet in tweets:
            content = str(tweet["text"])
            m = re.match(
                r"^([a-z0-9_]{1,15}) さんの \d{4}/\d{2}/\d{2} の contribution 数: (\d+)",
                content,
            )
            if m is not None:
                screen_name, contribution_count, *_ = m.groups()
                if screen_name == str(
                    tweet.get("user", {"screen_name": ""}).get("screen_name", "")
                ):
                    rank_data[screen_name] = int(contribution_count)
        else:
            return rank_data

    @staticmethod
    def get_top_contibutters(
        rank_data: dict[str, int], top: int = 3
    ) -> list[tuple[str, int]]:
        """Rank data and Get top contributors."""
        return collections.Counter(rank_data).most_common(top)

    @staticmethod
    def get_stat(rank_data: dict[str, int]) -> str:
        n = len(rank_data)
        contrib_sum = sum(rank_data.values())
        avg = float(contrib_sum / n)
        return f"ppl: {n}👤, sum: {contrib_sum}🟩, avg: {avg:.2f}🟩"

    def tweet_top_n(self, data: list[tuple[str, int]], stat: str) -> Any:
        contents = [f"✨Contribution Ranking - {self.day_before_str}✨"]
        tr = str.maketrans("1234567890", "１２３４５６７８９０")
        for idx, (name, num) in enumerate(data):
            if idx == 0:
                prefix = "🥇"
            elif idx == 1:
                prefix = "🥈"
            elif idx == 2:
                prefix = "🥉"
            elif idx == 3:
                prefix = "🏅"
            elif idx == 4:
                prefix = "🎖️"
            else:
                prefix = str(idx + 1).translate(tr) + " "
            contents.append(f"{prefix} {num}🟩: @{name}")
        else:
            contents.append(stat)
            contents.append("#contributter_ranking")
        params = {"status": "\n".join(contents)}
        return self.twitter_oauth.post(
            "https://api.twitter.com/1.1/statuses/update.json", params=params
        )
