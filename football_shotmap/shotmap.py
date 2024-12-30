"""This module generates shotmaps for football matches and players."""

import asyncio

from .scrape import get_player_shots_data, get_match_shots
from .style import OutfitFont, Colors

import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch


def get_season_label(year):
    """
    Generate a season label string in the format "YYYY/YY".

    Args:
        year (int): The starting year of the season.

    Returns:
        str: A string representing the season in the format "YYYY/YY".
    """

    return f"{year}/{int(year) % 100 + 1}"


def get_player_data(player_name, year):
    return asyncio.run(get_player_shots_data(player_name, year))


def get_match_data(home_team, away_team, year):
    return asyncio.run(get_match_shots(home_team, away_team, year))


def prepare_date(data):
    df = pd.DataFrame(data)
    df = df.astype({'xG': float, 'X': float, 'Y': float})

    # Convert x and y for mplsoccer
    df['X'] = df['X'] * 100
    df['Y'] = df['Y'] * 100

    return df


def calculate_stats(df):
    total_shots = df.shape[0]
    total_goals = df[df['result'] == 'Goal'].shape[0]
    total_xG = df['xG'].sum()
    xG_per_shot = total_xG / total_shots
    points_average_distance = df['X'].mean()

    average_pitch_size = 105
    actual_average_distance = average_pitch_size - (df['X'] * average_pitch_size / 100).mean()

    return {
        'total_shots': total_shots,
        'total_goals': total_goals,
        'total_xG': total_xG,
        'xG_per_shot': xG_per_shot,
        'points_average_distance': points_average_distance,
        'actual_average_distance': actual_average_distance
    }


def create_shotmap_fig_form_data(title, subtitle, data):
    df = prepare_date(data)
    stats = calculate_stats(df)

    pitch = VerticalPitch(
        pitch_type='opta',
        half=True,
        corner_arcs=True,
        pitch_color=Colors.BACKGROUND,
        pad_bottom=0.25,
        line_color=Colors.MAIN,
        linewidth=1,
        axis=True,
        label=True
    )

    # Create a subplot with 2 rows and 1 column
    fig = plt.figure(figsize=(8, 12))
    fig.patch.set_facecolor(Colors.BACKGROUND)

    # Top row for the team names and score
    # [left, bottom, width, height]
    ax1 = fig.add_axes([0, 0.7, 1, .2])
    ax1.set_facecolor(Colors.BACKGROUND)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)

    ax1.text(
        x=0.5,
        y=0.8,
        s=title,
        fontsize=24,
        fontproperties=OutfitFont.BLACK,
        color=Colors.MAIN,
        ha='center'
    )
    ax1.text(
        x=0.5,
        y=.65,
        s=subtitle,
        fontsize=14,
        fontproperties=OutfitFont.BOLD,
        color=Colors.MAIN,
        ha='center'
    )

    ax1.text(
        x=0.25,
        y=0.45,
        s=f'Low Quality Chance',
        fontsize=12,
        fontproperties=OutfitFont.BOLD,
        color=Colors.MAIN,
        ha='center'
    )

    # Add a scatter point between the two texts
    points = [
        { "x": 0.37, "y": 0.48, "s": 100 },
        { "x": 0.42, "y": 0.48, "s": 200 },
        { "x": 0.48, "y": 0.48, "s": 300 },
        { "x": 0.54, "y": 0.48, "s": 400 },
        { "x": 0.60, "y": 0.48, "s": 500 }
    ]
    for point in points:
        ax1.scatter(
            x=point["x"],
            y=point["y"],
            s=point["s"],
            color=Colors.BACKGROUND,
            edgecolor=Colors.MAIN,
            linewidth=.8
        )

    ax1.text(
        x=0.75,
        y=0.45,
        s=f'High Quality Chance',
        fontsize=12,
        fontproperties=OutfitFont.BOLD,
        color=Colors.MAIN,
        ha='center'
    )

    ax1.text(
        x=0.45,
        y=0.23,
        s=f'Goal',
        fontsize=10,
        fontproperties=OutfitFont.BOLD,
        color=Colors.MAIN,
        ha='right'
    )
    ax1.scatter(
        x=0.47,
        y=0.26,
        s=100,
        color=Colors.ACCENT,
        edgecolor=Colors.MAIN,
        linewidth=.8,
        alpha=.7
    )

    ax1.scatter(
        x=0.53,
        y=0.26,
        s=100,
        color=Colors.BACKGROUND,
        edgecolor=Colors.MAIN,
        linewidth=.8
    )
    ax1.text(
        x=0.55,
        y=0.23,
        s=f'No Goal',
        fontsize=10,
        fontproperties=OutfitFont.BOLD,
        color=Colors.MAIN,
        ha='left'
    )
    ax1.set_axis_off()

    ax2 = fig.add_axes([.05, 0.25, .9, .5])
    ax2.set_facecolor(Colors.BACKGROUND)
    pitch.draw(ax=ax2)

    # Create a scatter plot at y 100 - average_distance
    ax2.scatter(
        x=90,
        y=stats['points_average_distance'],
        s=100,
        color=Colors.MAIN,
        linewidth=.8
    )

    # Create a line from the bottom of the pitch to the scatter point
    ax2.plot(
        [90, 90],
        [100, stats['points_average_distance']],
        color=Colors.MAIN,
        linewidth=1
    )

    # Add a text label for the average distance
    ax2.text(
        x=90,
        y=stats['points_average_distance'] - 4,
        s=f"Average Distance\n{stats["actual_average_distance"]:.1f} meters",
        fontsize=10,
        fontproperties=OutfitFont.BOLD,
        color=Colors.MAIN,
        ha='center'
    )

    for x in df.to_dict(orient='records'):
        pitch.scatter(
            x['X'],
            x['Y'],
            s=300 * x['xG'],
            color=Colors.ACCENT if x['result'] == 'Goal' else Colors.BACKGROUND,
            ax=ax2,
            alpha=.7,
            linewidth=.8,
            edgecolor=Colors.MAIN
        )

    ax2.set_axis_off()

    # TODO: Fix layout
    # Add another axis for the stats
    ax3 = fig.add_axes([0, .2, 1, .05])
    ax3.set_facecolor(Colors.BACKGROUND)
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)

    ax3.text(
        x=0.2,
        y=.5,
        s='Shots',
        fontsize=20,
        fontproperties=OutfitFont.BOLD,
        color=Colors.MAIN,
        ha='center'
    )

    ax3.text(
        x=0.2,
        y=0,
        s=f'{stats["total_shots"]}',
        fontsize=16,
        fontproperties=OutfitFont.BOLD,
        color=Colors.ACCENT,
        ha='center'
    )

    ax3.text(
        x=0.4,
        y=.5,
        s='Goals',
        fontsize=20,
        fontproperties=OutfitFont.BOLD,
        color=Colors.MAIN,
        ha='center'
    )

    ax3.text(
        x=0.4,
        y=0,
        s=f'{stats["total_goals"]}',
        fontsize=16,
        fontproperties=OutfitFont.BOLD,
        color=Colors.ACCENT,
        ha='center'
    )

    ax3.text(
        x=0.6,
        y=.5,
        s='xG',
        fontsize=20,
        fontproperties=OutfitFont.BOLD,
        color=Colors.MAIN,
        ha='center'
    )

    ax3.text(
        x=0.6,
        y=0,
        s=f'{stats["total_xG"]:.2f}',
        fontsize=16,
        fontproperties=OutfitFont.BOLD,
        color=Colors.ACCENT,
        ha='center'
    )

    ax3.text(
        x=0.8,
        y=.5,
        s='xG/Shot',
        fontsize=20,
        fontproperties=OutfitFont.BOLD,
        color=Colors.MAIN,
        ha='center'
    )

    ax3.text(
        x=0.8,
        y=0,
        s=f'{stats["xG_per_shot"]:.2f}',
        fontsize=16,
        fontproperties=OutfitFont.BOLD,
        color=Colors.ACCENT,
        ha='center'
    )

    ax3.set_axis_off()

    return fig


def create_player_shotmap_fig(player_name, year):
    data = get_player_data(player_name, year)

    title = player_name
    subtitle = f'All shots in the Premier League {get_season_label(year)}'

    return create_shotmap_fig_form_data(title, subtitle, data)


def create_team_shotmap_fig(home_team, away_team, year):
    data = get_match_data(home_team, away_team, year)
    data = data['h']

    title = home_team
    subtitle = f'All shots for {home_team} in the {home_team} vs {away_team} {get_season_label(year)}'

    return create_shotmap_fig_form_data(title, subtitle, data)


def create_player_shotmap(player_name, year):
    file_name = f"./media/{player_name.lower().replace(" ", "_")}_{year}.png"

    fig = create_player_shotmap_fig(player_name, year)
    fig.savefig(file_name, facecolor=Colors.BACKGROUND, bbox_inches="tight")
    return file_name


def create_team_shotmap(home_team, away_team, year):
    normalized_match_name = f"{home_team}_{away_team}".replace(" ", "_").lower()
    file_name = f"./media/{normalized_match_name}_{year}.png"

    fig = create_team_shotmap_fig(home_team, away_team, year)
    fig.savefig(file_name, facecolor=Colors.BACKGROUND, bbox_inches="tight")
    return file_name


if __name__ == "__main__":
    player_name = "Mohamed Salah"
    year = "2023"

    home_team = "Liverpool"
    away_team = "Everton"

    file_name = create_player_shotmap(player_name, year)
    print(f"Shotmap created at: '{file_name}'.")

    file_name = create_team_shotmap(home_team, away_team, year)
    print(f"Shotmap created at: '{file_name}'.")
