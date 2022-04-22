"""Tweet n-days-before contributter-report ranking."""

from __future__ import annotations

import collections
import datetime
import json
import os
import re
import time
from typing import Any

import dotenv
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
        self.day_before = day_before
        self.day_before_str = self.get_n_before(self.day_before)

    @staticmethod
    def __get_twitter_oauth() -> requests_oauthlib.OAuth1Session:
        """Create a Twitter OAuth Object."""
        consumer_key = os.environ["CONSUMER_KEY"]
        consumer_secret = os.environ["CONSUMER_SECRET"]
        access_token = os.environ["ACCESS_TOKEN"]
        access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]
        return requests_oauthlib.OAuth1Session(
            consumer_key, consumer_secret, access_token, access_token_secret
        )

    @staticmethod
    def is_contributtter_report(tweet: str) -> tuple[bool, str | None, str | None]:
        """Check if tweet is a valid contributter report."""
        match = re.match(
            r"^([a-z0-9_]{1,15}) さんの \d{4}/\d{2}/\d{2} の contribution 数: (\d+)",
            tweet,
        )
        if match is not None:
            screen_name, contribution_count, *_ = match.groups()
            return True, screen_name, contribution_count
        return False, None, None

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
        tweets: list[Any] = []
        statuses: None | list[Any] = None
        while statuses is None or len(statuses) != 0:
            if max_id != -1:
                params["max_id"] = max_id - 1

            req = self.twitter_oauth.get(
                "https://api.twitter.com/1.1/search/tweets.json", params=params
            )
            if req.status_code == 200:
                res: dict[str, Any] = json.loads(req.text)
                statuses_ = list(res.get("statuses", []))
                tweets.extend(statuses_)
                max_id = statuses_[-1]["id"]
            time.sleep(self.wait_sec)
        return tweets

    def parse_contributter_reports(self, tweets: Any) -> dict[str, int]:
        """Create a dictionary of tweets usernames and number of contributions."""
        rank_data: dict[str, int] = {}
        for tweet in tweets:
            is_ok, screen_name, contribution_count = self.is_contributtter_report(tweet)
            contributor_name = str(
                tweet.get("user", {"screen_name": ""}).get("screen_name", "")
            )
            if is_ok and contributor_name != "":
                rank_data[screen_name] = int(contribution_count)
        return rank_data

    @staticmethod
    def get_top_contibutters(
        rank_data: dict[str, int], top: int = 3
    ) -> list[tuple[str, int]]:
        """Rank data and Get top contributors."""
        return collections.Counter(rank_data).most_common(top)

    @staticmethod
    def get_stat(rank_data: dict[str, int]) -> str:
        """Get statistics."""
        contrib_n = len(rank_data)
        contrib_sum = sum(rank_data.values())
        avg = float(contrib_sum / contrib_n)
        return f"ppl: {contrib_n}👤, sum: {contrib_sum}🟩, avg: {avg:.2f}🟩"

    def tweet_top_n(self, data: list[tuple[str, int]], stat: str) -> Any:
        """Tweet top-n with stats."""
        contents = [f"✨Contribution Ranking - {self.day_before_str}✨"]
        tr_table = str.maketrans("1234567890", "１２３４５６７８９０")
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
                prefix = str(idx + 1).translate(tr_table) + " "
            contents.append(f"{prefix} {num}🟩: @{name}")
        contents.append(stat)
        contents.append("#contributter_ranking")
        params = {"status": "\n".join(contents)}
        return self.twitter_oauth.post(
            "https://api.twitter.com/1.1/statuses/update.json", params=params
        )
