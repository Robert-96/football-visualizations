"""This module generates shotzones for football matches and players."""

import asyncio
import copy

from .utils import prepare_shot_data, calculate_shots_stats, get_season_label
from .scrape import get_player_shots_data, get_teams_players
from .style import OutfitFont, Colors

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mplsoccer import VerticalPitch


def is_inside_zone(x, y, zone):
    """Checks if a point is inside a zone."""

    return zone["x"] - zone["width"] < x <= zone["x"] and zone["y"] - zone["height"] < y <= zone["y"]


def calculate_zones_stats(df, zones, vertical=True):
    """Calculates the stats for each zone."""

    stats = copy.deepcopy(zones)
    for stat in stats:
        stat["shots"] = 0
        stat["xG"] = 0

    for shot in df.to_dict(orient="records"):
        if vertical:
            x, y = shot["Y"], shot["X"]
        else:
            x, y = shot["X"], shot["Y"]

        for zone in stats:
            if is_inside_zone(x, y, zone):
                zone["shots"] += 1
                zone["xG"] += shot["xG"]
                break

    return stats


def draw_zone(ax, zone, color, text):
    """Draws a zone on the pitch."""

    # Set zorder to 0 to draw the rectangle behind the pitch
    # TODO: Fix the zone x, y coordinates to be the opposite corner of the rectangle, so we don't need to subtract the width and height
    rect = Rectangle((zone["x"] - zone["width"], zone["y"] - zone["height"]), zone["width"], zone["height"], facecolor=color, linewidth=0, alpha=0.5, zorder=0)

    ax.add_patch(rect)
    ax.annotate(f"{text}", (0.5, 0.5), xycoords=rect, color=Colors.MAIN, fontsize=12, fontproperties=OutfitFont.BOLD, ha="center", va="center")


def draw_zone_borders(ax, zone):
    draw = zone.get("draw")
    if not draw:
        return

    lines = []

    if "top" in draw:
        lines.append([(zone["x"], zone["y"]), (zone["x"] - zone["width"], zone["y"])])

    if "bottom" in draw:
        lines.append([(zone["x"], zone["y"] - zone["height"]), (zone["x"] - zone["width"], zone["y"] - zone["height"])])

    if "left" in draw:
        lines.append([(zone["x"], zone["y"]), (zone["x"], zone["y"] - zone["height"])])

    if "right" in draw:
        lines.append([(zone["x"] - zone["width"], zone["y"]), (zone["x"] - zone["width"], zone["y"] - zone["height"])])

    for line in lines:
        ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], color=Colors.ACCENT, linewidth=2, linestyle="dashed")


def draw_zones(ax, zones, total):
    for index, zone in enumerate(sorted(zones, key=lambda x: x["shots"], reverse=True)):
        if zone["shots"] > 0:
            average_shots = zone["shots"] * 100 / total
            draw_zone(ax, zone, Colors.PURPLES[index], f"{average_shots:.2f}%\n{zone["xG"]:.2f} xG")

        draw_zone_borders(ax, zone)


def create_shotzone_fig_from_data(data, title="Title", subtitle="Subtitle"):
    if len(data) == 0:
        return

    df = prepare_shot_data(data)
    stats = calculate_shots_stats(df)

    fig = plt.figure(figsize=(8, 12))
    fig.patch.set_facecolor(Colors.BACKGROUND)

    ax1 = fig.add_axes([.05, 0.6, 0.9, 0.2])
    ax1.text(x=0.5, y=0.8, s=title, fontsize=24, fontproperties=OutfitFont.BLACK, color=Colors.MAIN, ha="center")
    ax1.text(x=0.5, y=0.65, s=subtitle, fontsize=14, fontproperties=OutfitFont.BOLD, color=Colors.MAIN, ha="center")
    ax1.set_axis_off()

    ax2 = fig.add_axes([.05, 0.25, 0.9, .5])
    ax2.set_facecolor(Colors.BACKGROUND)

    pitch = VerticalPitch(
        pitch_type="opta",
        half=True,
        corner_arcs=True,
        pitch_color=Colors.BACKGROUND,
        line_color=Colors.MAIN,
        spot_scale=0,
        pad_bottom=0.25
    )
    pitch.draw(ax=ax2)

    zones = [
        {"x": 100, "y": 100, "width": 21, "height": 17, "draw": ["bottom"]},
        {"x": 79, "y": 100, "width": 15.8, "height": 17, "draw": []},
        {"x": 63.2, "y": 100, "width": 26.4, "height": 5.8, "draw": []},
        {"x": 63.2, "y": 94.2, "width": 26.4, "height": 11.2, "draw": ["left", "right"]},
        {"x": 36.8, "y": 100, "width": 15.8, "height": 17, "draw": []},
        {"x": 21, "y": 100, "width": 21, "height": 17, "draw": ["bottom"]},
        {"x": 100, "y": 83, "width": 21, "height": 33, "draw": ["right"]},
        {"x": 79, "y": 83, "width": 58, "height": 11, "draw": ["bottom"]},
        {"x": 79, "y": 72, "width": 58, "height": 22, "draw": []},
        {"x": 21, "y": 83, "width": 21, "height": 33, "draw": ["left"]},
    ]

    zone_stats = calculate_zones_stats(df, zones)
    draw_zones(ax2, zone_stats, df.shape[0])
    ax2.set_axis_off()

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


def create_player_shotzone_fig(player_name, year):
    data = asyncio.run(get_player_shots_data(player_name, year))

    return create_shotzone_fig_from_data(data, title=f"{player_name}", subtitle=f"All shots in the Premier League in {get_season_label(year)} season")


def create_player_shotzone(player_name, year):
    file_name = f"./media/{player_name.lower().replace(" ", "_")}_{year}_shotzone.png"

    fig = create_player_shotzone_fig(player_name, year)
    if fig is None:
        return

    fig.savefig(file_name, facecolor=Colors.BACKGROUND, bbox_inches="tight")
    return file_name


if __name__ == "__main__":
    player_name = "Mohamed Salah"
    year = "2024"

    create_player_shotzone(player_name, year)

    team = "Liverpool"
    players = asyncio.run(get_teams_players(team, year))

    from .shotmap import create_player_shotmap
    for player in players:
        print(player["player_name"], player["position"])

        if "F" in player["position"] or "S" in player["position"]:
            create_player_shotmap(player["player_name"], year)
