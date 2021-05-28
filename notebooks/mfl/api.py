import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime as dt
from urllib.parse import urljoin
from io import BytesIO
from .utils import clean_column_name, convert_weight_to_lbs, convert_height_to_inches


class MFL(object):
    def __init__(self):
        self.base_url = "https://www58.myfantasyleague.com/"
        self.page_html = None


class TopPlayers(MFL):
    def __init__(
        self,
        snapshot_year: int = 2021,
        year: int = 2020,
        count: int = 500,
        start_week: int = 1,
        end_week: int = 16,
        category: str = "overall",
        position: str = "*",
        display: str = "points",
        search_type: str = "BASIC",
        team: str = "*",
        l: int = 46381,
        append_player_paths: bool = True,
    ):
        super().__init__()
        self.param_dict = {
            "L": l,
            "SEARCHTYPE": search_type,
            "COUNT": count,
            "YEAR": year,
            "START_WEEK": start_week,
            "END_WEEK": end_week,
            "CATEGORY": category,
            "POSITION": position,
            "DISPLAY": display,
            "TEAM": team,
        }
        self.append_player_paths = append_player_paths
        self.snapshot_year = snapshot_year if snapshot_year else dt.date.today().year
        self.top_players_url = urljoin(self.base_url, f"{snapshot_year}/top")

        self.top_players = None

    def _get_player_html(self):
        req = requests.get(self.top_players_url, params=self.param_dict)
        resp = req.content
        self.page_html = resp

    def get_stats(self):
        if not self.page_html:
            self._get_player_html()

        stats_df = pd.read_html(BytesIO(self.page_html))[1]
        stats_df.columns = [
            "rank",
            "player_name",
            "total_points",
            "average_points",
            "week_1_pts",
            "week_2_pts",
            "week_3_pts",
            "week_4_pts",
            "week_5_pts",
            "week_6_pts",
            "week_7_pts",
            "week_8_pts",
            "week_9_pts",
            "week_10_pts",
            "week_11_pts",
            "week_12_pts",
            "week_13_pts",
            "week_14_pts",
            "week_15_pts",
            "week_16_pts",
            "week_1_opponent",
            "owner",
            "bye_week",
            "salary",
            "years"
        ]

        stats_df["year"] = self.param_dict["YEAR"]
        stats_df["position"] = stats_df["player_name"].apply(
            lambda x: x.split()[-1].strip()
        )

        if self.append_player_paths:
            soup = BeautifulSoup(self.page_html, "html.parser")
            players_paths_df = pd.DataFrame(
                [
                    (a.text, a.get("href"))
                    for a in soup.find_all("a")
                    if a.get("href", "NULL").startswith("player?L")
                    and a.get("class") is not None
                ],
                columns=["player_name", "player_path"],
            )
            stats_df = stats_df.merge(players_paths_df, on="player_name", how="left")

        cols_to_numeric = ["total_points", "average_points"]
        for c in cols_to_numeric:
            stats_df[c] = stats_df[c].astype(float)

        self.top_players = stats_df
        return self.top_players


class Player(MFL):
    def __init__(self, player_name: str, player_path: str, snapshot_year: int = 2021):
        super().__init__()
        self.player_name = player_name
        self.player_path = player_path
        self.snapshot_year = snapshot_year if snapshot_year else dt.date.today().year
        self.player_url = urljoin(self.base_url, f"{snapshot_year}/{player_path}")

        self.player_bio = None
        self.player_status = None
        self.player_stats = None

    def _get_player_html(self):
        req = requests.get(self.player_url)
        resp = req.content
        self.page_html = resp

    def get_player_bio(self):
        if not self.page_html:
            self._get_player_html()

        bio = pd.read_html(BytesIO(self.page_html))[2]
        bio = (
            bio.set_index(0)
            .transpose()
            .drop(2)
            .rename(columns={"Experience:": "experience"})
        )
        bio["height"], bio["weight"] = (
            bio["Height/Weight:"].apply(lambda x: x.split(" / ")).values[0]
        )
        bio["dob"], bio["age"] = (
            bio["DOB/Age:"].apply(lambda x: x.split(" / ")).values[0]
        )
        bio["player_name"] = self.player_name

        bio = bio[
            ["player_name", "height", "weight", "dob", "age", "experience"]
        ].reset_index(drop=True)

        bio["height_inches"] = bio[f"height"].apply(convert_height_to_inches)
        bio["weight_lbs"] = bio[f"weight"].apply(convert_weight_to_lbs)
        bio["experience_years"] = bio[f"experience"].apply(convert_weight_to_lbs)
        bio["dob"] = pd.to_datetime(bio["dob"])
        bio["age"] = bio["age"].astype(float)

        self.player_bio = bio

        return self.player_bio

    def get_player_status(self):
        if not self.page_html:
            self._get_player_html()

        status = pd.read_html(BytesIO(self.page_html))[3]
        status[0] = status[0].apply(clean_column_name)
        status = status.set_index(0).transpose().reset_index(drop=True)
        status["player_name"] = self.player_name
        self.player_status = status
        return self.player_status

    def get_player_stats(self):
        if not self.page_html:
            self._get_player_html()

        stats = pd.read_html(BytesIO(self.page_html))[5]
        stats = stats.drop(stats.shape[0] - 1)
        stats.columns = [s[1] for s in stats.columns]
        stats = stats.dropna(axis=1, how="all").rename(columns={"Season": "season"})

        stats = pd.melt(
            frame=stats,
            id_vars=["season"],
            value_vars=[c for c in stats.columns if c != "season"],
            var_name="stat_name",
            value_name="value",
            col_level=None,
        )

        stats["value"] = stats["value"].astype(float)

        stats["player_name"] = self.player_name
        self.player_stats = stats
        return self.player_stats
