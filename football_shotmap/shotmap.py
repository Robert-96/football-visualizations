"""Generate shotmap."""

import asyncio

from .scrape import get_player_shots_data
from .fonts import OutfitFont

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


def create_shotmap_fig_form_data(player_name, year, data):
    df = prepare_date(data)
    stats = calculate_stats(df)

    pitch = VerticalPitch(
        pitch_type='opta',
        half=True,
        corner_arcs=True,
        pitch_color=BACKGROUND_COLOR,
        pad_bottom=0.25,
        line_color=MAIN_COLOR,
        linewidth=1,
        axis=True,
        label=True
    )

    # Create a subplot with 2 rows and 1 column
    fig = plt.figure(figsize=(8, 12))
    fig.patch.set_facecolor(BACKGROUND_COLOR)

    # Top row for the team names and score
    # [left, bottom, width, height]
    ax1 = fig.add_axes([0, 0.7, 1, .2])
    ax1.set_facecolor(BACKGROUND_COLOR)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)

    ax1.text(
        x=0.5,
        y=0.8,
        s=player_name,
        fontsize=24,
        fontproperties=OutfitFont.BLACK,
        color=MAIN_COLOR,
        ha='center'
    )
    ax1.text(
        x=0.5,
        y=.65,
        s=f'All shots in the Premier League {get_season_label(year)}',
        fontsize=14,
        fontproperties=OutfitFont.BOLD,
        color=MAIN_COLOR,
        ha='center'
    )

    ax1.text(
        x=0.25,
        y=0.45,
        s=f'Low Quality Chance',
        fontsize=12,
        fontproperties=OutfitFont.BOLD,
        color=MAIN_COLOR,
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
            color=BACKGROUND_COLOR,
            edgecolor=MAIN_COLOR,
            linewidth=.8
        )

    ax1.text(
        x=0.75,
        y=0.45,
        s=f'High Quality Chance',
        fontsize=12,
        fontproperties=OutfitFont.BOLD,
        color=MAIN_COLOR,
        ha='center'
    )

    ax1.text(
        x=0.45,
        y=0.23,
        s=f'Goal',
        fontsize=10,
        fontproperties=OutfitFont.BOLD,
        color=MAIN_COLOR,
        ha='right'
    )
    ax1.scatter(
        x=0.47,
        y=0.26,
        s=100,
        color=ACCENT_COLOR,
        edgecolor=MAIN_COLOR,
        linewidth=.8,
        alpha=.7
    )

    ax1.scatter(
        x=0.53,
        y=0.26,
        s=100,
        color=BACKGROUND_COLOR,
        edgecolor=MAIN_COLOR,
        linewidth=.8
    )
    ax1.text(
        x=0.55,
        y=0.23,
        s=f'No Goal',
        fontsize=10,
        fontproperties=OutfitFont.BOLD,
        color=MAIN_COLOR,
        ha='left'
    )
    ax1.set_axis_off()

    ax2 = fig.add_axes([.05, 0.25, .9, .5])
    ax2.set_facecolor(BACKGROUND_COLOR)
    pitch.draw(ax=ax2)

    # Create a scatter plot at y 100 - average_distance
    ax2.scatter(
        x=90,
        y=stats['points_average_distance'],
        s=100,
        color=MAIN_COLOR,
        linewidth=.8
    )

    # Create a line from the bottom of the pitch to the scatter point
    ax2.plot(
        [90, 90],
        [100, stats['points_average_distance']],
        color=MAIN_COLOR,
        linewidth=1
    )

    # Add a text label for the average distance
    ax2.text(
        x=90,
        y=stats['points_average_distance'] - 4,
        s=f"Average Distance\n{stats["actual_average_distance"]:.1f} meters",
        fontsize=10,
        fontproperties=OutfitFont.BOLD,
        color=MAIN_COLOR,
        ha='center'
    )

    for x in df.to_dict(orient='records'):
        pitch.scatter(
            x['X'],
            x['Y'],
            s=300 * x['xG'],
            color=ACCENT_COLOR if x['result'] == 'Goal' else BACKGROUND_COLOR,
            ax=ax2,
            alpha=.7,
            linewidth=.8,
            edgecolor=MAIN_COLOR
        )

    ax2.set_axis_off()

    # TODO: Fix layout
    # Add another axis for the stats
    ax3 = fig.add_axes([0, .2, 1, .05])
    ax3.set_facecolor(BACKGROUND_COLOR)
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)

    ax3.text(
        x=0.2,
        y=.5,
        s='Shots',
        fontsize=20,
        fontproperties=OutfitFont.BOLD,
        color=MAIN_COLOR,
        ha='center'
    )

    ax3.text(
        x=0.2,
        y=0,
        s=f'{stats["total_shots"]}',
        fontsize=16,
        fontproperties=OutfitFont.BOLD,
        color=ACCENT_COLOR,
        ha='center'
    )

    ax3.text(
        x=0.4,
        y=.5,
        s='Goals',
        fontsize=20,
        fontproperties=OutfitFont.BOLD,
        color=MAIN_COLOR,
        ha='center'
    )

    ax3.text(
        x=0.4,
        y=0,
        s=f'{stats["total_goals"]}',
        fontsize=16,
        fontproperties=OutfitFont.BOLD,
        color=ACCENT_COLOR,
        ha='center'
    )

    ax3.text(
        x=0.6,
        y=.5,
        s='xG',
        fontsize=20,
        fontproperties=OutfitFont.BOLD,
        color=MAIN_COLOR,
        ha='center'
    )

    ax3.text(
        x=0.6,
        y=0,
        s=f'{stats["total_xG"]:.2f}',
        fontsize=16,
        fontproperties=OutfitFont.BOLD,
        color=ACCENT_COLOR,
        ha='center'
    )

    ax3.text(
        x=0.8,
        y=.5,
        s='xG/Shot',
        fontsize=20,
        fontproperties=OutfitFont.BOLD,
        color=MAIN_COLOR,
        ha='center'
    )

    ax3.text(
        x=0.8,
        y=0,
        s=f'{stats["xG_per_shot"]:.2f}',
        fontsize=16,
        fontproperties=OutfitFont.BOLD,
        color=ACCENT_COLOR,
        ha='center'
    )

    ax3.set_axis_off()

    return fig


def create_shotmap_fig(player_name, year):
    data = get_player_data(player_name, year)
    return create_shotmap_fig_form_data(player_name, year, data)


def create_shotmap(player_name, year):
    file_name = f"./media/{player_name.lower().replace(" ", "_")}_{year}.png"

    fig = create_shotmap_fig(player_name, year)
    fig.savefig(file_name, facecolor=BACKGROUND_COLOR, bbox_inches="tight")
    return file_name


if __name__ == "__main__":
    player_name = "Mohamed Salah"
    year = "2024"

    file_name = create_shotmap(player_name, year)
    print(f"Shotmap created at: '{file_name}'.")
