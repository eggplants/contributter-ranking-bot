"""Tweet n-days-before contributter-report ranking."""

from __future__ import annotations

import collections
import datetime
import json
import os
import re
import textwrap
import time
from typing import Any

import dotenv  # type: ignore[import]
import requests_oauthlib  # type: ignore[import]


class ContributterRanking:
    def __init__(self, key_path: str | None = "~/.twitter.key") -> None:
        if key_path is not None and os.path.isfile(key_path):
            dotenv.load_dotenv(key_path)
        self.day_before: int = 1
        self.top_n: int = 3
        self.wait_sec: int = 10
        self.twitter_oauth: requests_oauthlib.OAuth1Session = self.__get_twitter_oauth()
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
        tweets = self.get_contributter_tweets()
        if len(tweets) < self.top_n:
            raise ValueError(
                "Number of Retrieved Tweets must be less than expected top_n"
                f"(got: {len(tweets)}< {self.top_n})"
            )
        rank_data = self.parse_contributter_reports(tweets)
        top_n_contributers = self.get_top_contibutters(rank_data, self.top_n)
        tweet_result = self.tweet_top3(top_n_contributers)
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

    def tweet_top3(self, data: list[tuple[str, int]]) -> Any:
        (
            (first_name, first_num),
            (second_name, second_num),
            (third_name, third_num),
            *_,
        ) = data
        content = textwrap.dedent(
            f"""
            ✨{self.day_before_str} の Contribution 数 Ranking✨
            🥇 @{first_name}さん　contribution 数: {first_num}
            🥈 @{second_name}さん　contribution 数: {second_num}
            🥉 @{third_name}さん　contribution 数: {third_num}
            #contributter_ranking
            """
        )
        params = {"status": content}
        return self.twitter_oauth.post(
            "https://api.twitter.com/1.1/statuses/update.json", params=params
        )
