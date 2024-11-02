"""Scrape understat to get shot data for a given player."""

import asyncio

import aiohttp
import pandas as pd
from understat import Understat


async def get_shots_data(player_name, year):
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)

        season = str(year)
        players = await understat.get_league_players("EPL", season=season)
        player_id = None
        for player in players:
            if player["player_name"] == player_name:
                player_id = player["id"]

        if not player_id:
            raise ValueError(f"Invalid player name: '{player_name}'.")

        player_shots = await understat.get_player_shots(
            player_id=player_id,
            season=season
        )

        return player_shots


async def generate_shot_data(player_name, year):
    normalized_player_name = player_name.replace(" ", "_").lower()
    file_name = f"./data/{normalized_player_name}_{year}_understat.csv"

    data = await get_shots_data(player_name, year)
    df = pd.json_normalize(data)
    df.to_csv(file_name, index=False)

    return file_name


if __name__ == "__main__":
    player_name = "Diogo Jota"
    year = "2024"

    asyncio.run(generate_shot_data(player_name, year))
