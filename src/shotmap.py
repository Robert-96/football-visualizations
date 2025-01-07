"""This module generates shotmaps for football matches and players."""

import asyncio

from .utils import prepare_shot_data, calculate_shots_stats, get_season_label
from .scrape import get_player_shots_data, get_match_shots, get_match_stats
from .style import OutfitFont, Colors

import matplotlib.pyplot as plt
from mplsoccer import Pitch, VerticalPitch


def add_header_section(ax, title, subtitle):
    ax.text(x=0.5, y=0.8, s=title, fontsize=24, fontproperties=OutfitFont.BLACK, color=Colors.MAIN, ha="center")
    ax.text(x=0.5, y=0.65, s=subtitle, fontsize=14, fontproperties=OutfitFont.BOLD, color=Colors.MAIN, ha="center")

    ax.text(x=0.25, y=0.45, s=f"Low Quality Chance", fontsize=12, fontproperties=OutfitFont.BOLD, color=Colors.MAIN, ha="center")

    # Add a scatter point between the two texts
    points = [
        { "x": 0.37, "y": 0.48, "s": 100 },
        { "x": 0.42, "y": 0.48, "s": 200 },
        { "x": 0.48, "y": 0.48, "s": 300 },
        { "x": 0.54, "y": 0.48, "s": 400 },
        { "x": 0.60, "y": 0.48, "s": 500 }
    ]
    for point in points:
        ax.scatter(x=point["x"], y=point["y"], s=point["s"], color=Colors.BACKGROUND, edgecolor=Colors.MAIN, linewidth=0.8)

    ax.text(x=0.75, y=0.45, s="High Quality Chance", fontsize=12, fontproperties=OutfitFont.BOLD, color=Colors.MAIN, ha="center")

    ax.text(x=0.45, y=0.23, s="Goal", fontsize=10, fontproperties=OutfitFont.BOLD, color=Colors.MAIN, ha="right")
    ax.scatter(x=0.47, y=0.26, s=100, color=Colors.ACCENT, edgecolor=Colors.MAIN, linewidth=0.8, alpha=0.7)

    ax.scatter(x=0.53, y=0.26, s=100, color=Colors.BACKGROUND, edgecolor=Colors.MAIN, linewidth=0.8)
    ax.text(x=0.55, y=0.23, s="No Goal", fontsize=10, fontproperties=OutfitFont.BOLD, color=Colors.MAIN, ha="left")


def add_average_distance_section(ax, average_distance):
    ax.scatter(x=90, y=average_distance, s=100, color=Colors.MAIN, linewidth=0.8)
    ax.plot([90, 90], [100, average_distance], color=Colors.MAIN, linewidth=2)
    ax.text(x=90, y=average_distance - 4, s=f"Average Distance\n{average_distance:.1f} meters", fontsize=10, fontproperties=OutfitFont.BOLD, color=Colors.MAIN, ha="center")


def create_shotmap_fig_form_data(data, title="Shotmap", subtitle="All shots"):
    if len(data) == 0:
        return

    df = prepare_shot_data(data)
    stats = calculate_shots_stats(df)

    fig = plt.figure(figsize=(8, 12))
    fig.patch.set_facecolor(Colors.BACKGROUND)

    ax1 = fig.add_axes([0, 0.7, 1, .2])
    ax1.set_facecolor(Colors.BACKGROUND)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    add_header_section(ax1, title, subtitle)
    ax1.set_axis_off()

    ax2 = fig.add_axes([.05, 0.25, 0.9, .5])
    ax2.set_facecolor(Colors.BACKGROUND)

    pitch = VerticalPitch(
        pitch_type="opta",
        half=True,
        corner_arcs=True,
        pitch_color=Colors.BACKGROUND,
        line_color=Colors.MAIN,
        pad_bottom=0.25,
    )
    pitch.draw(ax=ax2)

    add_average_distance_section(ax2, stats["points_average_distance"])

    for x in df.to_dict(orient="records"):
        color=Colors.ACCENT if x["result"] == "Goal" else Colors.BACKGROUND,
        pitch.scatter(x["X"], x["Y"], s=300 * x["xG"], color=color, ax=ax2, alpha=0.7, linewidth=0.8, edgecolor=Colors.MAIN)

    ax2.set_axis_off()

    # Add another axis for the stats
    ax3 = fig.add_axes([0, .2, 1, .05])
    ax3.set_facecolor(Colors.BACKGROUND)
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)

    stats = [
        {"text": "Shots", "value": f"{stats["total_shots"]}", "x": 0.2},
        {"text": "Goals", "value": f"{stats["total_goals"]}", "x": 0.4},
        {"text": "xG", "value": f"{stats["total_xG"]:.2f}", "x": 0.6},
        {"text": "xG/Shot", "value": f"{stats["xG_per_shot"]:.2f}", "x": 0.8}
    ]
    for stat in stats:
        ax3.text(x=stat["x"], y=0.5, s=stat["text"], fontsize=20, fontproperties=OutfitFont.BOLD, color=Colors.MAIN, ha="center")
        ax3.text(x=stat["x"], y=0, s=stat["value"], fontsize=16, fontproperties=OutfitFont.BOLD, color=Colors.ACCENT, ha="center")

    ax3.set_axis_off()

    return fig


def create_match_shotmap_fig_from_data(data, title="Shotmap", subtitle="All shots"):
    if len(data) == 0:
        return

    home_data = data['h']
    away_data = data['a']

    home_df = prepare_shot_data(home_data)
    away_df = prepare_shot_data(away_data)

    home_team = home_data[0]['h_team']
    away_team = home_data[0]['a_team']

    home_stats = calculate_shots_stats(home_df)
    away_stats = calculate_shots_stats(away_df)

    fig = plt.figure(figsize=(8, 12))
    fig.patch.set_facecolor(Colors.BACKGROUND)

    ax1 = fig.add_axes([0, 0.7, 1, .2])
    ax1.set_facecolor(Colors.BACKGROUND)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    add_header_section(ax1, title, subtitle)
    ax1.set_axis_off()

    ax2 = fig.add_axes([.05, 0.285, .9, .5])
    ax2.set_facecolor(Colors.BACKGROUND)

    pitch = Pitch(
        pitch_type="opta",
        corner_arcs=True,
        pitch_color=Colors.BACKGROUND,
        line_color=Colors.MAIN,
        pad_bottom=0.25,
    )
    pitch.draw(ax=ax2)

    ax2.text(x=25, y=90, s=home_team, fontsize=14, fontproperties=OutfitFont.BOLD, color=Colors.MAIN, ha="center")
    ax2.text(x=75, y=90, s=away_team, fontsize=14, fontproperties=OutfitFont.BOLD, color=Colors.MAIN, ha="center")

    for x in home_df.to_dict(orient="records"):
        color = Colors.ACCENT if x["result"] == "Goal" else Colors.BACKGROUND
        pitch.scatter(100 - x["X"], x["Y"], s=300 * x["xG"], color=color, ax=ax2, alpha=0.7, linewidth=0.8, edgecolor=Colors.MAIN)

    for x in away_df.to_dict(orient='records'):
        color = Colors.ACCENT if x["result"] == "Goal" else Colors.BACKGROUND
        pitch.scatter(x["X"], x["Y"], s=300 * x["xG"], color=color, ax=ax2, alpha=0.7, linewidth=.8, edgecolor=Colors.MAIN)

    ax2.set_axis_off()

    ax3 = fig.add_axes([0, .275, 1, .05])
    ax3.set_facecolor(Colors.BACKGROUND)
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)

    stats = [
        {"text": "Shots", "value": f"{home_stats["total_shots"]}", "x": 0.14},
        {"text": "xG", "value": f"{home_stats["total_xG"]:.2f}", "x": 0.26},
        {"text": "xG/Shot", "value": f"{home_stats["xG_per_shot"]:.2f}", "x": 0.38},
        {"text": "Shots", "value": away_stats["total_shots"], "x": 0.58},
        {"text": "xG", "value": f"{away_stats["total_xG"]:.2f}", "x": 0.70},
        {"text": "xG/Shot", "value": f"{away_stats["xG_per_shot"]:.2f}", "x": 0.82}
    ]
    for stat in stats:
        ax3.text(x=stat["x"], y=0.5, s=stat["text"], fontsize=18, fontproperties=OutfitFont.BOLD, color=Colors.MAIN, ha="center")
        ax3.text(x=stat["x"], y=0, s=stat["value"], fontsize=16, fontproperties=OutfitFont.BOLD, color=Colors.ACCENT, ha="center")

    ax3.set_axis_off()

    return fig


def create_player_shotmap_fig(player_name, year):
    data = asyncio.run(get_player_shots_data(player_name, year))

    title = player_name
    subtitle = f'All shots in Premier League in {get_season_label(year)}'

    return create_shotmap_fig_form_data(data, title=title, subtitle=subtitle)


def create_match_shotmap_fig(home_team, away_team, year):
    data = asyncio.run(get_match_shots(home_team, away_team, year))
    result = asyncio.run(get_match_stats(home_team, away_team, year))

    title = f"{home_team} {result["h_goals"]} - {result["a_goals"]} {away_team}"
    subtitle = f'All shots in {home_team} - {away_team} fixture in {get_season_label(year)}'

    return create_match_shotmap_fig_from_data(data, title=title, subtitle=subtitle)


def create_player_shotmap(player_name, year):
    file_name = f"./media/{player_name.lower().replace(" ", "_")}_{year}_shotmap.png"

    fig = create_player_shotmap_fig(player_name, year)
    if fig is None:
        return

    fig.savefig(file_name, facecolor=Colors.BACKGROUND, bbox_inches="tight")
    return file_name


def create_match_shotmap(home_team, away_team, year):
    normalized_match_name = f"{home_team}_{away_team}".replace(" ", "_").lower()
    file_name = f"./media/{normalized_match_name}_{year}_shotmap.png"

    fig = create_match_shotmap_fig(home_team, away_team, year)
    if fig is None:
        return

    fig.savefig(file_name, facecolor=Colors.BACKGROUND, bbox_inches="tight")
    return file_name


if __name__ == "__main__":
    player_name = "Mohamed Salah"
    year = "2024"

    home_team = "West Ham"
    away_team = "Liverpool"

    file_name = create_player_shotmap(player_name, year)
    print(f"Shotmap created at: '{file_name}'.")

    file_name = create_match_shotmap(home_team, away_team, year)
    print(f"Shotmap created at: '{file_name}'.")
