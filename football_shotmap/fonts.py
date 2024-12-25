import matplotlib.font_manager as font_manager


class OutfitFont:
    BLACK = font_manager.FontProperties(fname="./fonts/static/Outfit-Black.ttf", weight=900)
    EXTRA_BOLD = font_manager.FontProperties(fname="./fonts/static/Outfit-ExtraBold.ttf", weight=800)
    BOLD = font_manager.FontProperties(fname="./fonts/static/Outfit-Bold.ttf", weight=700)
    SEMI_BOLD = font_manager.FontProperties(fname="./fonts/static/Outfit-SemiBold.ttf", weight=600)
    MEDIUM = font_manager.FontProperties(fname="./fonts/static/Outfit-Medium.ttf", weight=500)
    REGULAR = font_manager.FontProperties(fname="./fonts/static/Outfit-Regular.ttf", weight=400)
    LIGHT = font_manager.FontProperties(fname="./fonts/static/Outfit-Light.ttf", weight=300)
    EXTRA_LIGHT = font_manager.FontProperties(fname="./fonts/static/Outfit-ExtraLight.ttf", weight=200)
    THIN = font_manager.FontProperties(fname="./fonts/static/Outfit-ExtraLight.ttf", weight=100)


class Colors:
    BACKGROUND = "#0c0a09"
    MAIN = "#e5e7eb"
    ACCENT = "#c084fc"
