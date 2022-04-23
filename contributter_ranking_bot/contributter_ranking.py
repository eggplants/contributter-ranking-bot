"""Tweet n-days-before contributter-report ranking."""

from __future__ import annotations

import collections
import datetime
import json
import os
import re
import sys
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
        wait_sec: int = 10,
    ) -> None:
        if key_path is not None and os.path.isfile(key_path):
            dotenv.load_dotenv(key_path)

        self.__day_before_str: str = self.__get_n_before(day_before)

        self.__wait_sec: int = wait_sec
        self.__twitter_oauth: requests_oauthlib.OAuth1Session = (
            self.__get_twitter_oauth()
        )

    def set_day_before(self, day_before: int) -> None:
        """Set day."""
        self.__day_before_str = self.__get_n_before(day_before)

    def run(
        self, top_n: int = 3, dry_run: bool = False
    ) -> tuple[int, dict[str, Any], Any]:
        """Run Bot."""
        tweets = self.__get_contributter_tweets()
        if len(tweets) < top_n:
            raise ValueError(
                "Number of Retrieved Tweets must be less than expected top_n"
                f"(got: {len(tweets)} < {top_n})"
            )
        rank_data = self.__parse_contributter_reports(tweets)
        top_n_contributers = self.__get_top_contibutters(rank_data, top_n)
        stat = self.__get_stat(rank_data)
        tweet_result = self.__tweet_top_n(top_n_contributers, stat, dry_run=dry_run)
        return (
            int(tweet_result.status_code),
            json.loads(str(tweet_result.text)),
            tweet_result,
        )

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
    def __is_contributtter_report(tweet: str) -> tuple[bool, str | None, int | None]:
        """Check if tweet is a valid contributter report."""
        match = re.match(
            r"^([a-z0-9_]{1,15}) さんの \d{4}/\d{2}/\d{2} の contribution 数: (\d+)",
            tweet,
        )
        if match is not None:
            screen_name, contribution_count, *_ = match.groups()
            return True, screen_name, int(contribution_count)
        return False, None, None

    @staticmethod
    def __get_n_before(day_before: int = 1) -> str:
        """Get yeaterday date string. (YYYY/MM/DD)"""
        yesterday = datetime.datetime.today() - datetime.timedelta(days=day_before)
        return yesterday.strftime("%Y/%m/%d")

    def __get_contributter_tweets(self) -> list[Any]:
        """Retrieve yesterday's all contributter reports form twitter."""
        params = {
            "count": 100,
            "q": f"#contributter_report {self.__day_before_str} exclude:retweets",
            "max_id": -1,
        }
        tweets: list[Any] = []
        statuses: None | list[Any] = None
        while statuses is None or len(statuses) != 0:
            if statuses is not None:
                # pylint: disable=unsubscriptable-object
                params["max_id"] = statuses[-1]["id"] - 1

            req = self.__twitter_oauth.get(
                "https://api.twitter.com/1.1/search/tweets.json", params=params
            )
            if req.status_code == 200:
                res: dict[str, Any] = json.loads(req.text)
                statuses = list(res.get("statuses", []))
                tweets.extend(statuses)
                print(f"{req.status_code}: id={params['max_id']}", file=sys.stderr)
            else:
                statuses = None
                print(f"{req.status_code}: id={params['max_id']}", file=sys.stderr)
            time.sleep(self.__wait_sec)
        return tweets

    def __parse_contributter_reports(self, tweets: Any) -> dict[str, int]:
        """Create a dictionary of tweets usernames and number of contributions."""
        rank_data: dict[str, int] = {}
        for tweet in tweets:
            is_ok, screen_name, contribution_count = self.__is_contributtter_report(
                tweet.get("text", "")
            )
            contributor_name = str(
                tweet.get("user", {"screen_name": ""}).get("screen_name", "")
            )
            if (
                is_ok
                and screen_name is not None
                and contribution_count is not None
                and contributor_name != ""
            ):
                rank_data[screen_name] = int(contribution_count)
        return rank_data

    @staticmethod
    def __get_top_contibutters(
        rank_data: dict[str, int], top: int = 3
    ) -> list[tuple[str, int]]:
        """Rank data and Get top contributors."""
        return collections.Counter(rank_data).most_common(top)

    @staticmethod
    def __get_stat(rank_data: dict[str, int]) -> str:
        """Get statistics."""
        contrib_n = len(rank_data)
        contrib_sum = sum(rank_data.values())
        avg = float(contrib_sum / contrib_n)
        return f"ppl: {contrib_n}👤, sum: {contrib_sum}🟩, avg: {avg:.2f}🟩"

    def __tweet_top_n(
        self, data: list[tuple[str, int]], stat: str, dry_run: bool = False
    ) -> Any:
        """Tweet top-n with stats."""
        mention_interrupt = "." if dry_run else ""
        contents = [f"✨Contribution Ranking - {self.__day_before_str}✨"]
        tr_table = str.maketrans("1234567890", "１２３４５６７８９０")
        for idx, (name, num) in enumerate(data):
            if 0 <= idx <= 4:
                prefix = ("🥇", "🥈", "🥉", "🏅", "🎖️")[idx]
            else:
                prefix = str(idx + 1).translate(tr_table) + " "
            contents.append(f"{prefix} {num}🟩: @{mention_interrupt}{name}")
        contents.append(stat)
        contents.append("#contributter_ranking")
        params = {"status": "\n".join(contents)}
        return self.__twitter_oauth.post(
            "https://api.twitter.com/1.1/statuses/update.json", params=params
        )
