from pathlib import Path

import matplotlib.font_manager as font_manager

FONT_BASE_PATH = Path("./fonts/static")


class OutfitFont:
    BLACK = font_manager.FontProperties(fname=FONT_BASE_PATH / "Outfit-Black.ttf", weight=900)
    EXTRA_BOLD = font_manager.FontProperties(fname=FONT_BASE_PATH /  "/Outfit-ExtraBold.ttf", weight=800)
    BOLD = font_manager.FontProperties(fname=FONT_BASE_PATH / "Outfit-Bold.ttf", weight=700)
    SEMI_BOLD = font_manager.FontProperties(fname=FONT_BASE_PATH / "Outfit-SemiBold.ttf", weight=600)
    MEDIUM = font_manager.FontProperties(fname=FONT_BASE_PATH / "Outfit-Medium.ttf", weight=500)
    REGULAR = font_manager.FontProperties(fname=FONT_BASE_PATH / "Outfit-Regular.ttf", weight=400)
    LIGHT = font_manager.FontProperties(fname=FONT_BASE_PATH / "Outfit-Light.ttf", weight=300)
    EXTRA_LIGHT = font_manager.FontProperties(fname=FONT_BASE_PATH / "Outfit-ExtraLight.ttf", weight=200)
    THIN = font_manager.FontProperties(fname=FONT_BASE_PATH / "Outfit-ExtraLight.ttf", weight=100)


class Colors:
    PURPLES = ["#9333ea", "#7e22ce", "#6b21a8", "#581c87", "#3b0764"]
    BACKGROUND = "#0c0a09"
    MAIN = "#e5e7eb"
    ACCENT = "#c084fc"
