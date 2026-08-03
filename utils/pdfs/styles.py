from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

styles = getSampleStyleSheet()


# ==========================================================
# COLORS
# ==========================================================

PRIMARY = colors.HexColor("#1565C0")      # Blue

SECONDARY = colors.HexColor("#42A5F5")

SUCCESS = colors.HexColor("#2E7D32")

WARNING = colors.HexColor("#EF6C00")

INFO = colors.HexColor("#6A1B9A")

BACKGROUND = colors.HexColor("#F5F7FA")

LIGHT_BLUE = colors.HexColor("#E3F2FD")

LIGHT_GREEN = colors.HexColor("#E8F5E9")

LIGHT_ORANGE = colors.HexColor("#FFF3E0")

LIGHT_PURPLE = colors.HexColor("#F3E5F5")

GRAY = colors.HexColor("#616161")

BLACK = colors.black

WHITE = colors.white


# ==========================================================
# TITLE
# ==========================================================

TITLE = ParagraphStyle(
    "TITLE",

    parent=styles["Heading1"],

    fontName="Helvetica-Bold",

    fontSize=28,

    textColor=PRIMARY,

    alignment=TA_CENTER,

    spaceAfter=20,
)


# ==========================================================
# SUBTITLE
# ==========================================================

SUBTITLE = ParagraphStyle(
    "SUBTITLE",

    parent=styles["Heading2"],

    fontName="Helvetica-Bold",

    fontSize=16,

    textColor=PRIMARY,

    spaceBefore=15,

    spaceAfter=10,
)


# ==========================================================
# SECTION HEADER
# ==========================================================

SECTION = ParagraphStyle(
    "SECTION",

    parent=styles["Heading2"],

    fontName="Helvetica-Bold",

    fontSize=18,

    textColor=PRIMARY,

    spaceBefore=20,

    spaceAfter=15,
)


# ==========================================================
# BODY
# ==========================================================

BODY = ParagraphStyle(
    "BODY",

    parent=styles["BodyText"],

    fontName="Helvetica",

    fontSize=11,

    leading=18,

    textColor=BLACK,

    alignment=TA_LEFT,
)


# ==========================================================
# SMALL TEXT
# ==========================================================

SMALL = ParagraphStyle(
    "SMALL",

    parent=BODY,

    fontSize=9,

    leading=12,

    textColor=GRAY,
)


# ==========================================================
# FOOTER
# ==========================================================

FOOTER = ParagraphStyle(
    "FOOTER",

    parent=BODY,

    alignment=TA_CENTER,

    fontSize=9,

    textColor=GRAY,
)


# ==========================================================
# DAY TITLE
# ==========================================================

DAY_TITLE = ParagraphStyle(
    "DAY_TITLE",

    parent=styles["Heading2"],

    fontName="Helvetica-Bold",

    fontSize=18,

    textColor=SUCCESS,

    spaceBefore=18,

    spaceAfter=10,
)


# ==========================================================
# CARD TITLE
# ==========================================================

CARD_TITLE = ParagraphStyle(
    "CARD_TITLE",

    parent=styles["Heading3"],

    fontName="Helvetica-Bold",

    fontSize=13,

    textColor=PRIMARY,

    spaceAfter=8,
)