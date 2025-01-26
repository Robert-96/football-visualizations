from dataclasses import dataclass, field

from .style import Colors, OutfitFont

from matplotlib.patches import Rectangle
from mplsoccer.dimensions import opta_dims


PITCH_DIMS = opta_dims()

# Pitch side is the pitch size minus the penalty area size
PITCH_SIDE_WIDTH = (PITCH_DIMS.width - PITCH_DIMS.penalty_area_width) / 2
PITCH_SIDE_LENGTH = (PITCH_DIMS.length / 2) - PITCH_DIMS.penalty_area_length

# Penalty area side is the penalty area size minus the six yard size
PENALTY_AREA_SIDE_WIDTH = (PITCH_DIMS.penalty_area_width - PITCH_DIMS.six_yard_width) / 2
PENALTY_AREA_SIDE_LENGTH = PITCH_DIMS.penalty_area_length - PITCH_DIMS.six_yard_length


@dataclass
class Zone:
    x: float
    y: float
    width: float
    height: float
    draw: list[int] = field(default_factory=list)
    values: dict = field(default_factory=dict)

    def is_inside(self, x, y, vertical=False):
        """Checks if a point is inside a zone."""

        if not vertical:
            x, y = y, x

        return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height


def make_default_zones():
    # All the zones are defined for the horizontal pitch but work for the vertical pitch as well.
    zones = []

    # First row
    zones.append(Zone(0, 0, PITCH_DIMS.penalty_area_length, PITCH_SIDE_WIDTH, draw=["right"]))
    zones.append(Zone(0, PITCH_SIDE_WIDTH, PITCH_DIMS.penalty_area_length, PENALTY_AREA_SIDE_WIDTH))
    zones.append(Zone(0, PITCH_DIMS.six_yard_bottom, PITCH_DIMS.six_yard_length, PITCH_DIMS.six_yard_width))
    zones.append(Zone(PITCH_DIMS.six_yard_length, PITCH_DIMS.six_yard_bottom, PENALTY_AREA_SIDE_LENGTH, PITCH_DIMS.six_yard_width, draw=["top", "bottom"]))
    zones.append(Zone(0, PITCH_DIMS.six_yard_top, PITCH_DIMS.penalty_area_length, PENALTY_AREA_SIDE_WIDTH))
    zones.append(Zone(0, PITCH_DIMS.penalty_area_top, PITCH_DIMS.penalty_area_length, PITCH_SIDE_WIDTH, draw=["right"]))

    # Next 6 rows
    width = PITCH_SIDE_LENGTH / 3
    for i in range(6):
        x = PITCH_DIMS.penalty_area_length + i * width
        draw = ["top", "right"] if i != 2 and i != 5 else ["top"]

        zones.append(Zone(x, 0, width, PITCH_SIDE_WIDTH, draw=draw))
        zones.append(Zone(x, PITCH_SIDE_WIDTH, width, PENALTY_AREA_SIDE_WIDTH, draw=draw))
        zones.append(Zone(x, PITCH_DIMS.six_yard_bottom, width, PITCH_DIMS.six_yard_width, draw=draw))
        zones.append(Zone(x, PITCH_DIMS.six_yard_top, width, PENALTY_AREA_SIDE_WIDTH, draw=draw))
        zones.append(Zone(x, PITCH_DIMS.penalty_area_top, width, PITCH_SIDE_WIDTH, draw=["right"] if i != 2 and i != 5 else []))

    # Last row
    zones.append(Zone(PITCH_DIMS.penalty_area_right, 0, PITCH_DIMS.penalty_area_length, PITCH_SIDE_WIDTH, draw=["left"]))
    zones.append(Zone(PITCH_DIMS.penalty_area_right, PITCH_SIDE_WIDTH, PITCH_DIMS.penalty_area_length, PENALTY_AREA_SIDE_WIDTH))
    zones.append(Zone(PITCH_DIMS.six_yard_right, PITCH_DIMS.six_yard_bottom, PITCH_DIMS.six_yard_length, PITCH_DIMS.six_yard_width))
    zones.append(Zone(PITCH_DIMS.penalty_area_right, PITCH_DIMS.six_yard_bottom, PENALTY_AREA_SIDE_LENGTH, PITCH_DIMS.six_yard_width, draw=["top", "bottom"]))
    zones.append(Zone(PITCH_DIMS.penalty_area_right, PITCH_DIMS.six_yard_top, PITCH_DIMS.penalty_area_length, PENALTY_AREA_SIDE_WIDTH))
    zones.append(Zone(PITCH_DIMS.penalty_area_right, PITCH_DIMS.penalty_area_top, PITCH_DIMS.penalty_area_length, PITCH_SIDE_WIDTH, draw=["left"]))

    return zones


def make_simplified_zones():
    """TODO"""


def make_detailed_zones():
    pass


@dataclass
class Zones:
    zones: list[Zone] = field(default_factory=make_default_zones)

    def __iter__(self):
        return iter(self.zones)


def draw_zone_borders(pitch, ax, zone, color=Colors.ACCENT):
    """TODO: Write docstring."""

    draw = zone.draw
    if not draw:
        return

    lines = []

    if "top" in draw:
        lines.append([(zone.x, zone.y + zone.height), (zone.x + zone.width, zone.y + zone.height)])

    if "bottom" in draw:
        lines.append([(zone.x, zone.y), (zone.x + zone.width, zone.y)])

    if "left" in draw:
        lines.append([(zone.x, zone.y), (zone.x, zone.y + zone.height)])

    if "right" in draw:
        lines.append([(zone.x + zone.width, zone.y), (zone.x + zone.width, zone.y + zone.height)])

    for line in lines:
        pitch.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], color=color, linewidth=2, linestyle="dashed",  ax=ax)


def draw_zone_fill(pitch, ax, zone, text="Hello, World!", color=Colors.ACCENT):
    x = zone.x
    y = zone.y
    width = zone.width
    height = zone.height

    if pitch.vertical:
        x, y = y, x
        width, height = height, width

    rect = Rectangle((x, y), width, height, facecolor=color, linewidth=0, alpha=0.4, zorder=0)

    ax.add_patch(rect)
    ax.annotate(f"{text}", (0.5, 0.5), xycoords=rect, color=Colors.MAIN, fontsize=12, fontproperties=OutfitFont.BOLD, ha="center", va="center")


def draw_zones(pitch, ax, zones):
    for zone in zones:
        draw_zone_borders(pitch, ax, zone)


if __name__ == "__main__":
    from mplsoccer import Pitch, VerticalPitch

    horizontal_pitch = Pitch(
        pitch_type="opta",
        corner_arcs=True,
        pitch_color="black",
        line_color="white",
        spot_scale=0
    )

    vertical_pitch = VerticalPitch(
        pitch_type="opta",
        corner_arcs=True,
        pitch_color="black",
        line_color="white",
        spot_scale=0
    )

    for pitch in [horizontal_pitch, vertical_pitch]:
        fig, ax = pitch.draw(figsize=(16, 9))

        zones = Zones()
        draw_zones(pitch, ax, zones)

        fig.savefig(f"./media/test_{"vertical_" if pitch.vertical else ""}zones.png", bbox_inches="tight")
