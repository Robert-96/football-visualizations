"""This module generates shotzones for football matches and players."""

import asyncio

from .utils import prepare_shot_data, calculate_shots_stats, get_season_label
from .scrape import get_player_shots_data
from .style import OutfitFont, Colors, PURPLE_COLORMAP
from .zones import Zones, draw_zone_fill, draw_zones

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mplsoccer import VerticalPitch


def calculate_zones_stats(df, zones, vertical=True):
    """Calculates the stats for each zone."""

    for zone in zones:
        zone.values["shots"] = 0
        zone.values["xG"] = 0

    for shot in df.to_dict(orient="records"):
        x, y = shot["X"], shot["Y"]

        for zone in zones:
            if zone.is_inside(x, y, vertical):
                zone.values["shots"] += 1
                zone.values["xG"] += shot["xG"]
                break

    total_shots = df.shape[0]
    for zone in zones:
        zone.values["percentage"] = zone.values["shots"] * 100 / total_shots


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

    zones = Zones()
    calculate_zones_stats(df, zones, pitch.vertical)
    draw_zones(pitch, ax2, zones)

    zones_to_draw = list(filter(lambda zone: zone.values["shots"] > 0, sorted(zones, key=lambda zone: zone.values["shots"], reverse=True)))
    for index, zone in enumerate(zones_to_draw):
        if zone.values["shots"] > 0:
            draw_zone_fill(pitch, ax2, zone, text=f"{zone.values["percentage"]:.2f}%\n{zone.values["xG"]:.2f}xG", color=PURPLE_COLORMAP((index + 1) / len(zones_to_draw)))

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
