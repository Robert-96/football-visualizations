"""This module scrapes Understat to fetch and save data related to players, teams, and matches."""

import json
import asyncio

import aiohttp
import pandas as pd
from understat import Understat


class LEAGUES:
    """Leagues names used by Understat."""

    EPL = "EPL"
    PREMIER_LEAGUE = EPL
    BUNDESLIGA = "Bundesliga"
    SERIE_A = "Serie_A"
    LIGUE_1 = "ligue_1"
    RFPL = "RFPL"


async def get_player_id(understat, player_name, year="2024"):
    players = await understat.get_league_players("EPL", season=year)
    for player in players:
        if player["player_name"] == player_name:
            return player["id"]

    raise ValueError(f"Invalid player name: '{player_name}'.")


async def get_math_id(understat, home_team, away_team, year="2024"):
    season = str(year)

    results = await understat.get_league_results("EPL", season=season)
    for result in results:
        if result["h"]["title"] == home_team and result["a"]["title"] == away_team:
            return result["id"]

    fixtures = await understat.get_league_fixtures("EPL", season=season)
    for fixture in fixtures:
        if fixture["h"]["title"] == home_team and fixture["a"]["title"] == away_team:
            return fixture["id"]

    raise ValueError(f"Fixture not found for {home_team} vs {away_team}.")


async def get_teams(league, year="2024"):
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)

        season = str(year)
        return await understat.get_teams(league, season=season)


async def get_league_fixtures(year="2024"):
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)

        season = str(year)
        return await understat.get_league_fixtures("EPL", season=season)


async def get_player_shots_data(player_name, year):
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)

        season = str(year)
        player_id = await get_player_id(understat, player_name, year=season)
        player_shots = await understat.get_player_shots(
            player_id=player_id,
            season=season
        )
        return player_shots


async def get_player_data(player_name, year):
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)

        season = str(year)
        player_id = await get_player_id(understat, player_name, year=season)
        player_shots = await understat.get_player_stats(
            player_id=player_id
        )

        return player_shots


async def get_player_grouped_data(player_name, year):
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)

        season = str(year)
        players = await understat.get_league_players("EPL", season=season)
        player_id = None
        for player in players:
            if player["player_name"] == player_name:
                player_id = player["id"]
                break

        if not player_id:
            raise ValueError(f"Invalid player name: '{player_name}'.")

        player_shots = await understat.get_player_grouped_stats(
            player_id=player_id
        )

        return player_shots


async def get_player_matches(player_name, year):
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)

        season = str(year)
        player_id = await get_player_id(understat, player_name, year=season)
        player_shots = await understat.get_player_matches(
            player_id=player_id
        )

        return player_shots


async def get_match_data(home_team, away_team, year):
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)

        season = str(year)
        fixture_id = await get_math_id(understat, home_team, away_team, year=season)
        fixture_data = await understat.get_match_stats(fixture_id)
        return fixture_data


async def get_match_shots(home_team, away_team, year):
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)

        season = str(year)
        fixture_id = await get_math_id(understat, home_team, away_team, year=season)
        fixture_data = await understat.get_match_shots(fixture_id)
        return fixture_data


async def get_team_stats(team_name, year):
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)

        season = str(year)
        team_stats = await understat.get_team_stats(team_name, season=season)
        return team_stats


async def generate_teams(league=LEAGUES.EPL, year="2024"):
    file_name = f"./data/{league.lower()}_teams_{year}_understat.json"

    data = await get_teams(league, year)
    with open(file_name, 'w') as fp:
        json.dump(data, fp, indent=2)

    return file_name


async def generate_league_fixtures(year):
    file_name = f"./data/{LEAGUES.PREMIER_LEAGUE.lower()}_{year}_fixtures_understat.csv"

    data = await get_league_fixtures(year)
    df = pd.json_normalize(data)
    df.to_csv(file_name, index=False)

    return file_name


async def generate_player_shot_data(player_name, year):
    normalized_player_name = player_name.replace(" ", "_").lower()
    file_name = f"./data/{normalized_player_name}_{year}_shotdata_understat.csv"

    data = await get_player_shots_data(player_name, year)
    df = pd.json_normalize(data)
    df.to_csv(file_name, index=False)

    return file_name


async def generate_player_data(player_name, year):
    normalized_player_name = player_name.replace(" ", "_").lower()
    file_name = f"./data/{normalized_player_name}_{year}_stats_understat.csv"

    data = await get_player_data(player_name, year)
    df = pd.json_normalize(data)
    df.to_csv(file_name, index=False)

    return file_name


async def generate_player_group_data(player_name, year):
    normalized_player_name = player_name.replace(" ", "_").lower()
    file_name = f"./data/{normalized_player_name}_{year}_group_stats_understat.json"

    data = await get_player_grouped_data(player_name, year)
    with open(file_name, 'w') as fp:
        json.dump(data, fp, indent=2)

    return file_name


async def generate_player_matches(player_name, year):
    normalized_player_name = player_name.replace(" ", "_").lower()
    file_name = f"./data/{normalized_player_name}_{year}_matches_understat.csv"

    data = await get_player_matches(player_name, year)
    df = pd.json_normalize(data)
    df.to_csv(file_name, index=False)

    return file_name


async def generate_match_data(home_team, away_team, year):
    normalized_match_name = f"{home_team}_{away_team}".replace(" ", "_").lower()
    file_name = f"./data/{normalized_match_name}_{year}_understat.json"

    data = await get_match_data(home_team, away_team, year)
    with open(file_name, 'w') as fp:
        json.dump(data, fp, indent=2)

    return file_name


async def generate_match_shots(home_team, away_team, year):
    normalized_match_name = f"{home_team}_{away_team}".replace(" ", "_").lower()
    file_name = f"./data/{normalized_match_name}_{year}_shots_understat.json"

    data = await get_match_shots(home_team, away_team, year)
    with open(file_name, 'w') as fp:
        json.dump(data, fp, indent=2)

    return file_name


async def generate_team_stats(team_name, year):
    normalized_team_name = team_name.replace(" ", "_").lower()
    file_name = f"./data/{normalized_team_name}_{year}_stats_understat.json"

    data = await get_team_stats(team_name, year)
    with open(file_name, 'w') as fp:
        json.dump(data, fp, indent=2)

    return file_name


if __name__ == "__main__":
    player_name = "Diogo Jota"
    year = "2023"

    home_team = "Liverpool"
    away_team = "Everton"

    asyncio.run(generate_teams(LEAGUES.EPL, year))
    asyncio.run(generate_player_shot_data(player_name, year))
    asyncio.run(generate_player_data(player_name, year))
    asyncio.run(generate_player_group_data(player_name, year))
    asyncio.run(generate_player_matches(player_name, year))
    asyncio.run(generate_league_fixtures(year))
    asyncio.run(generate_match_data(home_team, away_team, year))
    asyncio.run(generate_match_shots(home_team, away_team, year))
    asyncio.run(generate_team_stats(home_team, year))
