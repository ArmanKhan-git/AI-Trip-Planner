"""
Voyage AI itinerary PDF — styled to match the web app (navy / brass / paper palette,
Fraunces headings, Inter body text, IBM Plex Mono labels).
"""

import io
import os
import unicodedata
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.platypus import (
    CondPageBreak,
    Flowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from schemas.itinerary import Itinerary

# ----------------------------------------------------------------------
# Fonts (resolved from the project root so the server's working directory doesn't matter)
# ----------------------------------------------------------------------
_FONTS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "fonts")

for _name, _file in [
    ("Display", "Fraunces-SemiBold.ttf"),
    ("Inter", "Inter-Regular.ttf"),
    ("Inter-SemiBold", "Inter-SemiBold.ttf"),
    ("Inter-Bold", "Inter-Bold.ttf"),
    ("Mono", "IBMPlexMono-Regular.ttf"),
    ("Mono-SemiBold", "IBMPlexMono-SemiBold.ttf"),
    ("Symbols", "DejaVuSans.ttf"),  # only font with ✈
]:
    pdfmetrics.registerFont(TTFont(_name, os.path.join(_FONTS, _file)))

# <b> inside Inter paragraphs -> Inter SemiBold
addMapping("Inter", 0, 0, "Inter")
addMapping("Inter", 1, 0, "Inter-SemiBold")
addMapping("Inter", 0, 1, "Inter")
addMapping("Inter", 1, 1, "Inter-SemiBold")

# ----------------------------------------------------------------------
# Palette (same values as the web app's `C` object)
# ----------------------------------------------------------------------
NAVY = colors.HexColor("#0B1D2E")
NAVY_LIGHT = colors.HexColor("#152C42")
PAPER = colors.HexColor("#EFF3F6")
CARD = colors.white
INK = colors.HexColor("#0F2233")
INK_SOFT = colors.HexColor("#4C6072")
BRASS = colors.HexColor("#B8862F")
BRASS_LIGHT = colors.HexColor("#D9A94B")
BRASS_BG = colors.HexColor("#FBF3E7")
BRASS_BORDER = colors.HexColor("#EEDDBD")
LINE = colors.HexColor("#D7DEE4")
GREEN = colors.HexColor("#2F7A4F")
GREEN_BG = colors.HexColor("#E7F3EB")
RED = colors.HexColor("#B23B3B")
RED_BG = colors.HexColor("#FAEAEA")
FOOD_GREEN = colors.HexColor("#6E8B7A")
TRANSPORT_BLUE = colors.HexColor("#93A6B8")


def _mix(c1, c2, t):
    """Blend c1 toward c2 by t (0..1) — stands in for transparency on dark cards."""
    return colors.Color(
        c1.red + (c2.red - c1.red) * t,
        c1.green + (c2.green - c1.green) * t,
        c1.blue + (c2.blue - c1.blue) * t,
    )


WHITE_90 = _mix(NAVY, colors.white, 0.9)
WHITE_60 = _mix(NAVY, colors.white, 0.6)
WHITE_45 = _mix(NAVY, colors.white, 0.45)
LEG_BG = _mix(NAVY, colors.white, 0.06)

PAGE_W, PAGE_H = A4
MARGIN = 36
CONTENT_W = PAGE_W - 2 * MARGIN

CURRENCY_SYMBOLS = {"INR": "₹", "USD": "$"}


# ----------------------------------------------------------------------
# Text helpers
# ----------------------------------------------------------------------
def _t(text) -> str:
    # NFC joins "e" + combining accent into "é", which the bundled fonts can draw.
    return escape(unicodedata.normalize("NFC", str(text if text is not None else "")))


def _group_indian(n: int) -> str:
    s = str(abs(n))
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ",".join(parts) + "," + tail


def make_money(currency: str):
    symbol = CURRENCY_SYMBOLS.get(currency, currency + " ")

    def money(value) -> str:
        n = int(round(float(value or 0)))
        grouped = _group_indian(n) if currency == "INR" else f"{abs(n):,}"
        return f"{'−' if n < 0 else ''}{symbol}{grouped}"

    return money


def _parse_dt(iso):
    try:
        return datetime.strptime(iso[:16], "%Y-%m-%dT%H:%M")
    except (TypeError, ValueError):
        return None


def _leg_time(iso) -> str:
    dt = _parse_dt(iso)
    return f"{dt.day} {dt:%b}, {dt:%H:%M}" if dt else "—"


def _date(date_str, fmt="%a, %d %b") -> str:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime(fmt)
    except (TypeError, ValueError):
        return ""


def _stops(n) -> str:
    return "Direct" if n == 0 else f"{n} stop{'s' if n > 1 else ''}"


def _style(name, font="Inter", size=9.5, color=INK, leading=None, **kw):
    return ParagraphStyle(name, fontName=font, fontSize=size, textColor=color,
                          leading=leading or size * 1.4, **kw)


S_BODY = _style("body")
S_BODY_SOFT = _style("bodySoft", color=INK_SOFT)
S_SMALL = _style("small", size=8, color=INK_SOFT)
S_SMALL_GREEN = _style("smallGreen", size=7.5, color=GREEN)
S_LABEL = _style("label", font="Mono", size=7, color=INK_SOFT, leading=10)
S_LABEL_BRASS = _style("labelBrass", font="Mono-SemiBold", size=7.5, color=BRASS, leading=10)
S_NAME = _style("name", font="Inter-SemiBold", size=10, leading=13)
S_PRICE = _style("price", font="Mono-SemiBold", size=10, leading=13, alignment=2)
S_PRICE_SUB = _style("priceSub", size=7, color=INK_SOFT, leading=9, alignment=2)
S_TH = _style("th", font="Mono-SemiBold", size=7, color=colors.white, leading=9)
S_TD = _style("td", size=8, leading=10.5)
S_TD_SOFT = _style("tdSoft", size=8, color=INK_SOFT, leading=10.5)
S_TD_MONO = _style("tdMono", font="Mono-SemiBold", size=8, leading=10.5)
S_ON_DARK = _style("onDark", size=8, color=WHITE_60, leading=11)
S_ON_DARK_TITLE = _style("onDarkTitle", font="Inter-Bold", size=13, color=colors.white, leading=16)


# ----------------------------------------------------------------------
# Building blocks
# ----------------------------------------------------------------------
def card(flowables, bg=CARD, padding=14, width=CONTENT_W, border=LINE, radius=10):
    """White rounded card, like the web app's SectionCard."""
    table = Table([[flowables]], colWidths=[width])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.6, border),
        ("ROUNDEDCORNERS", [radius] * 4),
        ("LEFTPADDING", (0, 0), (-1, -1), padding),
        ("RIGHTPADDING", (0, 0), (-1, -1), padding),
        ("TOPPADDING", (0, 0), (-1, -1), padding),
        ("BOTTOMPADDING", (0, 0), (-1, -1), padding),
    ]))
    return table


class SectionTitle(Flowable):
    """Brass accent bar + title, with an optional mono caption on the right."""

    def __init__(self, title, caption=""):
        super().__init__()
        self.title, self.caption = title, caption

    def wrap(self, aw, ah):
        self.width = aw
        return aw, 20

    def draw(self):
        c = self.canv
        c.setFillColor(BRASS)
        c.roundRect(0, 4, 3, 13, 1.5, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("Inter-SemiBold", 12.5)
        c.drawString(10, 6, self.title)
        if self.caption:
            c.setFillColor(INK_SOFT)
            c.setFont("Mono", 7.5)
            c.drawRightString(self.width, 7, self.caption)


class Pill(Flowable):
    def __init__(self, text, fg, bg, border=None, font="Mono-SemiBold", size=6.8):
        super().__init__()
        self.text, self.fg, self.bg, self.border, self.font, self.size = text, fg, bg, border, font, size

    def wrap(self, aw, ah):
        self.width = pdfmetrics.stringWidth(self.text, self.font, self.size) + 12
        self.height = self.size + 7
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        if self.border:
            c.setStrokeColor(self.border)
            c.setLineWidth(0.6)
        c.roundRect(0, 0, self.width, self.height, self.height / 2, stroke=1 if self.border else 0, fill=1)
        c.setFillColor(self.fg)
        c.setFont(self.font, self.size)
        c.drawCentredString(self.width / 2, 3.6, self.text)


class PillRow(Flowable):
    """Wrapping row of pills (attractions, confidence chips)."""

    def __init__(self, items, gap=5):
        """items: list of (text, fg, bg, border, font, size)"""
        super().__init__()
        self.items, self.gap = items, gap

    def _layout(self, aw):
        rows, x, y, h = [], 0, 0, 0
        for text, fg, bg, border, font, size in self.items:
            w = pdfmetrics.stringWidth(text, font, size) + 14
            ph = size + 8
            if x and x + w > aw:
                x, y = 0, y + h + self.gap
            rows.append((x, y, w, ph, text, fg, bg, border, font, size))
            x += w + self.gap
            h = ph
        return rows, (y + h if rows else 0)

    def wrap(self, aw, ah):
        self.width = aw
        self._rows, self.height = self._layout(aw)
        return aw, self.height

    def draw(self):
        c = self.canv
        for x, y, w, h, text, fg, bg, border, font, size in self._rows:
            yy = self.height - y - h
            c.setFillColor(bg)
            c.setStrokeColor(border or bg)
            c.setLineWidth(0.6)
            c.roundRect(x, yy, w, h, h / 2, stroke=1, fill=1)
            c.setFillColor(fg)
            c.setFont(font, size)
            c.drawCentredString(x + w / 2, yy + 4.2, text)


class DayBadge(Flowable):
    def __init__(self, number):
        super().__init__()
        self.number = number

    def wrap(self, aw, ah):
        return 28, 28

    def draw(self):
        c = self.canv
        c.setFillColor(NAVY)
        c.circle(14, 14, 14, stroke=0, fill=1)
        c.setFillColor(BRASS_LIGHT)
        c.setFont("Mono-SemiBold", 11)
        c.drawCentredString(14, 10, str(self.number))


def _spaced(c, x, y, text, font, size, color, spacing):
    """Letter-spaced label; the spacing is scoped so it can't leak into later text."""
    c.saveState()
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setCharSpace(spacing)
    t.setFillColor(color)
    t.textOut(text)
    c.drawText(t)
    c.restoreState()
    return pdfmetrics.stringWidth(text, font, size) + spacing * len(text)


def _plane(c, x, y, size, color):
    c.setFillColor(color)
    c.setFont("Symbols", size)
    c.drawString(x, y, "✈")


class BudgetBar(Flowable):
    def __init__(self, segments, height=11):
        super().__init__()
        self.segments, self.bar_h = segments, height

    def wrap(self, aw, ah):
        self.width = aw
        return aw, self.bar_h

    def draw(self):
        c = self.canv
        total = sum(v for _, v, _ in self.segments) or 1
        c.saveState()
        path = c.beginPath()
        path.roundRect(0, 0, self.width, self.bar_h, self.bar_h / 2)
        c.clipPath(path, stroke=0, fill=0)
        x = 0
        for _, value, color in self.segments:
            w = self.width * value / total
            c.setFillColor(color)
            c.rect(x, 0, w + 0.5, self.bar_h, stroke=0, fill=1)
            x += w
        c.restoreState()


class BoardingPass(Flowable):
    """Navy flight stub + hotel stub with a perforation, like the web app's BoardingPass."""

    def __init__(self, itinerary, money, origin, dest, flight_pick, hotel_pick):
        super().__init__()
        self.it, self.money = itinerary, money
        self.origin, self.dest = origin, dest
        self.flight_pick, self.hotel_pick = flight_pick, hotel_pick

    def wrap(self, aw, ah):
        self.width = aw
        self.left_w = aw * 0.58
        self.right_w = aw - self.left_w
        f, h = self.it.selected_flight, self.it.selected_hotel

        self.flight_reason = Paragraph(_t(f.reason), S_ON_DARK)
        _, frh = self.flight_reason.wrap(self.left_w - 36, 200)
        legs = sum(1 for leg in (f.outbound, f.return_leg) if leg) or 1
        left_h = 18 + 14 + 20 + 34 + 16 + legs * 52 + 14 + 26 + frh + 18

        self.hotel_name = Paragraph(_t(h.name), S_ON_DARK_TITLE)
        _, hnh = self.hotel_name.wrap(self.right_w - 36, 200)
        self.hotel_reason = Paragraph(_t(h.reason), S_ON_DARK)
        _, hrh = self.hotel_reason.wrap(self.right_w - 36, 300)
        right_h = 18 + 14 + 20 + hnh + 22 + 40 + hrh + 18

        self.height = max(left_h, right_h)
        return aw, self.height

    def _pick_pill(self, c, x_right, y, text):
        w = pdfmetrics.stringWidth(text, "Mono-SemiBold", 6.8) + 12
        c.setFillColor(BRASS_LIGHT)
        c.roundRect(x_right - w, y - 3, w, 13, 6.5, stroke=0, fill=1)
        c.setFillColor(NAVY)
        c.setFont("Mono-SemiBold", 6.8)
        c.drawCentredString(x_right - w / 2, y + 0.6, text)

    def _field(self, c, x, y, label, value, value_font="Inter-SemiBold", size=9):
        c.setFillColor(WHITE_45)
        c.setFont("Mono", 6.3)
        c.drawString(x, y + 11, label)
        c.setFillColor(colors.white)
        c.setFont(value_font, size)
        c.drawString(x, y, value)

    def draw(self):
        c = self.canv
        H, LW, RW = self.height, self.left_w, self.right_w
        f, h = self.it.selected_flight, self.it.selected_hotel
        trip = self.it.trip_summary
        money = self.money

        # Card backgrounds (one rounded shape, right half lighter)
        c.saveState()
        path = c.beginPath()
        path.roundRect(0, 0, self.width, H, 14)
        c.clipPath(path, stroke=0, fill=0)
        c.setFillColor(NAVY)
        c.rect(0, 0, LW, H, stroke=0, fill=1)
        c.setFillColor(NAVY_LIGHT)
        c.rect(LW, 0, RW, H, stroke=0, fill=1)
        c.restoreState()

        # Perforation
        c.setFillColor(PAPER)
        n = int(H // 18)
        for i in range(n):
            c.circle(LW, H - 12 - i * (H - 24) / max(n - 1, 1), 3, stroke=0, fill=1)

        # ---------------- Flight stub ----------------
        x0, y = 18, H - 18
        _plane(c, x0, y - 9, 10, BRASS_LIGHT)
        c.setFillColor(BRASS_LIGHT)
        c.setFont("Mono-SemiBold", 7.5)
        c.drawString(x0 + 15, y - 8, "BOARDING PASS")
        self._pick_pill(c, LW - 18, y - 9, self.flight_pick)

        y -= 46
        c.setFillColor(colors.white)
        c.setFont("Mono-SemiBold", 26)
        c.drawString(x0, y, self.origin)
        c.drawRightString(LW - 18, y, self.dest)
        ow = pdfmetrics.stringWidth(self.origin, "Mono-SemiBold", 26)
        dw = pdfmetrics.stringWidth(self.dest, "Mono-SemiBold", 26)
        c.setStrokeColor(WHITE_45)
        c.setDash(2, 2)
        c.setLineWidth(0.8)
        c.line(x0 + ow + 10, y + 8, LW - 18 - dw - 22, y + 8)
        c.setDash()
        _plane(c, LW - 18 - dw - 19, y + 4, 9, BRASS_LIGHT)
        c.setFillColor(WHITE_60)
        c.setFont("Inter", 7.5)
        c.drawString(x0, y - 12, trip.departure_city)
        c.drawRightString(LW - 18, y - 12, trip.destination)

        y -= 26
        c.setFillColor(WHITE_45)
        c.setFont("Mono", 6.3)
        c.drawString(x0, y, "AIRLINE")
        c.setFillColor(colors.white)
        c.setFont("Inter-SemiBold", 9.5)
        c.drawString(x0, y - 12, f.airline + (f" ({f.airline_code})" if f.airline_code else ""))
        y -= 22

        for label, leg in (("OUTBOUND", f.outbound), ("RETURN", f.return_leg)):
            if not leg:
                continue
            box_h = 46
            y -= box_h
            c.setFillColor(LEG_BG)
            c.roundRect(x0, y, LW - 36, box_h, 7, stroke=0, fill=1)
            c.setFillColor(BRASS_LIGHT)
            c.setFont("Mono-SemiBold", 6.8)
            c.drawString(x0 + 9, y + box_h - 13, f"{label}  ·  {leg.from_code} → {leg.to_code}")
            c.setFillColor(WHITE_60)
            c.setFont("Inter", 7.2)
            c.drawRightString(LW - 27, y + box_h - 13, f"{leg.duration} · {_stops(leg.stops)}")
            self._field(c, x0 + 9, y + 8, "DEPART", _leg_time(leg.departure), size=8.5)
            self._field(c, x0 + (LW - 36) / 2, y + 8, "ARRIVE", _leg_time(leg.arrival), size=8.5)
            y -= 6

        y -= 26
        c.setFillColor(BRASS_LIGHT)
        c.setFont("Mono-SemiBold", 17)
        price = money(f.price)
        c.drawString(x0, y, price)
        pw = pdfmetrics.stringWidth(price, "Mono-SemiBold", 17)
        c.setFillColor(WHITE_60)
        c.setFont("Inter", 7.5)
        sub = "round trip / traveler"
        if trip.travelers > 1:
            sub += f"  ·  {money(f.price * trip.travelers)} for {trip.travelers}"
        c.drawString(x0 + pw + 7, y + 1, sub)
        _, rh = self.flight_reason.wrap(LW - 36, 200)
        self.flight_reason.drawOn(c, x0, y - 8 - rh)

        # ---------------- Hotel stub ----------------
        x1, y = LW + 18, H - 18
        c.setFillColor(BRASS_LIGHT)
        c.setFont("Mono-SemiBold", 7.5)
        c.drawString(x1, y - 8, "STAY")
        self._pick_pill(c, self.width - 18, y - 9, self.hotel_pick)

        y -= 26
        _, hnh = self.hotel_name.wrap(RW - 36, 200)
        self.hotel_name.drawOn(c, x1, y - hnh)
        y -= hnh + 14
        c.setFillColor(BRASS_LIGHT)
        c.setFont("Inter", 9)
        c.drawString(x1, y, "★")
        c.setFillColor(WHITE_60)
        c.setFont("Inter", 8)
        c.drawString(x1 + 11, y, f"{h.rating}" + (f" · {_group_indian(h.reviews)} reviews" if h.reviews else ""))
        y -= 30
        self._field(c, x1, y, "PER NIGHT", money(h.estimated_nightly_cost), size=10)
        self._field(c, x1 + (RW - 36) / 2, y, "TOTAL", money(h.estimated_total_cost), size=10)
        _, hrh = self.hotel_reason.wrap(RW - 36, 300)
        self.hotel_reason.drawOn(c, x1, y - 14 - hrh)


# ----------------------------------------------------------------------
# PDF
# ----------------------------------------------------------------------
def build_pdf(itinerary: Itinerary, flight_pick: str = "AI PICK", hotel_pick: str = "AI PICK") -> bytes:
    """Render the itinerary as a PDF and return its bytes."""

    it = itinerary
    trip, budget, flight = it.trip_summary, it.budget, it.selected_flight
    money = make_money(trip.currency)
    origin = flight.outbound.from_code if flight.outbound else trip.departure_city[:3].upper()
    dest = flight.outbound.to_code if flight.outbound else trip.destination[:3].upper()
    days_count = len(it.itinerary)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN + 18, bottomMargin=MARGIN + 6,
        title=f"Voyage AI — {trip.destination}", author="Voyage AI",
    )

    story = [Spacer(1, 1), PageBreak()]  # page 1 is drawn entirely by draw_cover

    # ================= OVERVIEW =================
    story.append(BoardingPass(it, money, origin, dest, flight_pick, hotel_pick))
    story.append(Spacer(1, 14))

    # Budget card
    segments = [
        ("Flights", budget.flights, NAVY),
        ("Hotel", budget.hotel, BRASS),
        ("Food", budget.food, FOOD_GREEN),
        ("Transport", budget.transport, TRANSPORT_BLUE),
        ("Misc", budget.miscellaneous, LINE),
    ]
    legend_cells = []
    for label, value, color in segments:
        legend_cells.append(Paragraph(
            f"<font color='{color.hexval().replace('0x', '#')}' size=11>●</font>&nbsp; {label}<br/>"
            f"<font name='Mono-SemiBold' size=9 color='#0F2233'>{money(value)}</font>",
            _style("legend", size=8, color=INK_SOFT, leading=12),
        ))
    legend = Table([legend_cells], colWidths=[(CONTENT_W - 28) / 5] * 5)
    legend.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0)]))

    over = budget.remaining < 0
    remaining = Table([[
        Paragraph("Over budget by" if over else "Remaining budget",
                  _style("remL", font="Inter-SemiBold", size=10, color=RED if over else GREEN)),
        Paragraph(money(abs(budget.remaining)),
                  _style("remV", font="Mono-SemiBold", size=14, color=RED if over else GREEN, alignment=2)),
    ]], colWidths=[(CONTENT_W - 28) * 0.6, (CONTENT_W - 28) * 0.4])
    remaining.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), RED_BG if over else GREEN_BG),
        ("ROUNDEDCORNERS", [8] * 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(card([
        SectionTitle("Budget breakdown", f"TOTAL {money(budget.total)} OF {money(trip.budget)}"),
        Spacer(1, 8), BudgetBar(segments), Spacer(1, 10), legend, Spacer(1, 10), remaining,
    ]))
    story.append(Spacer(1, 14))

    # Trip at a glance
    glance_rows = []
    for day in it.itinerary:
        highlight = ", ".join(day.attractions) if day.attractions else day.morning
        glance_rows.append([
            Paragraph(f"<font name='Mono-SemiBold' color='#B8862F'>DAY {day.day}</font><br/>"
                      f"<font size=7.5 color='#4C6072'>{_t(_date(day.date))}</font>",
                      _style("gl", size=8, leading=11)),
            Paragraph(_t(highlight) + ("&nbsp;&nbsp;<font name='Mono-SemiBold' size=6.5 color='#B8862F'>TRAVEL DAY</font>"
                                       if day.travel_day else ""), _style("glt", size=8.5, leading=12)),
        ])
    # A multi-row table (not a single-cell card) so it can continue onto the next page.
    title_row = [[SectionTitle("Trip at a glance", f"{days_count} DAYS"), ""]]
    glance = Table(title_row + glance_rows, colWidths=[84, CONTENT_W - 84], repeatRows=1)
    glance.setStyle(TableStyle([
        ("SPAN", (0, 0), (-1, 0)),
        ("BACKGROUND", (0, 0), (-1, -1), CARD),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("ROUNDEDCORNERS", [10] * 4),
        ("LINEBELOW", (0, 1), (-1, -2), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 14), ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 14), ("BOTTOMPADDING", (0, -1), (-1, -1), 12),
    ]))
    story.append(glance)
    story.append(Spacer(1, 16))

    # ================= DAY BY DAY =================
    story.append(CondPageBreak(160))
    story.append(SectionTitle("Day-by-day itinerary"))
    story.append(Spacer(1, 10))

    inner_w = CONTENT_W - 28 - 40  # card padding + badge column

    def dinner_block(day):
        rows = []
        if day.travel_day:
            rows.append([Paragraph(
                "<font name='Symbols' color='#B8862F'>✈</font>&nbsp; <b>Travel day</b> — dinner at the airport or on board",
                _style("travel", size=9, color=INK_SOFT))])
        else:
            r = day.restaurant
            meta = " · ".join(x for x in (_t(r.cuisine), _t(r.price_range)) if x)
            left = [
                Paragraph(f"<b>{_t(r.name)}</b> <font color='#4C6072' size=8.5>· {meta}</font>"
                          f"&nbsp;&nbsp;<font name='Mono-SemiBold' size=6.5 color='#B8862F'>"
                          f"{'FINE DINING · YOUR PICK' if day.dinner_choice == 'fine' else 'RECOMMENDED'}</font>", S_NAME),
                Paragraph(f"<font color='#B8862F'>★</font> {r.rating}"
                          + (f" &nbsp;·&nbsp; <font color='#2F7A4F'>✓ Google range {_t(r.google_price_range)}</font>"
                             if r.google_price_range else ""), S_SMALL),
                Paragraph(_t(r.reason), S_SMALL),
            ]
            right = [Paragraph(("<font size=7 name='Inter'>from </font>" if r.price_is_minimum else "")
                               + money(r.average_cost_per_person), S_PRICE), Paragraph("per person", S_PRICE_SUB)]
            if r.estimated_saving and r.estimated_saving > 0:
                right.append(Paragraph(f"saves {money(r.estimated_saving)}",
                                       _style("save", font="Mono", size=7, color=GREEN, alignment=2, leading=9)))
            rows.append([left, right])
            if day.fine_dining:
                fd = day.fine_dining
                rows.append([
                    Paragraph(f"<font name='Mono-SemiBold' size=6.5 color='#4C6072'>FINE-DINING OPTION</font>&nbsp; "
                              f"<b>{_t(fd.name)}</b> <font color='#4C6072'>· {_t(fd.price_range)}</font>",
                              _style("fd", size=8.5, leading=12)),
                    Paragraph(("<font size=7 name='Inter'>from </font>" if fd.price_is_minimum else "")
                              + money(fd.average_cost_per_person), _style("fdp", font="Mono", size=8.5, alignment=2)),
                ])
        if day.breakfast_lunch_allowance:
            rows.append([
                Paragraph(f"Breakfast + lunch (cafés / stores, est.) {money(day.breakfast_lunch_allowance)}"
                          f" &nbsp;·&nbsp; <b>Day food total</b>", _style("bl", size=8, color=INK_SOFT)),
                Paragraph(f"{money(day.daily_food_cost_per_person)} / person",
                          _style("blt", font="Mono-SemiBold", size=8.5, alignment=2)),
            ])
        if day.travel_day and len(rows[0]) == 1:
            rows[0].append("")
        table = Table(rows, colWidths=[inner_w - 24 - 115, 115])
        style = [
            ("BACKGROUND", (0, 0), (-1, -1), PAPER),
            ("ROUNDEDCORNERS", [8] * 4),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
        for i in range(1, len(rows)):
            style.append(("LINEABOVE", (0, i), (-1, i), 0.5, LINE))
        table.setStyle(TableStyle(style))
        return table

    for day in it.itinerary:
        header = [Paragraph(
            f"<font name='Mono-SemiBold' color='#B8862F'>{_t(_date(day.date, '%A, %d %B').upper())}</font>"
            + ("&nbsp;&nbsp;<font name='Mono-SemiBold' size=6.5 color='#4C6072'>· TRAVEL DAY</font>" if day.travel_day else ""),
            _style("dh", size=8, leading=11))]
        slots = Table(
            [[Paragraph(lbl, S_LABEL), Paragraph(_t(txt), S_BODY)]
             for lbl, txt in (("MORNING", day.morning), ("AFTERNOON", day.afternoon), ("EVENING", day.evening))],
            colWidths=[62, inner_w - 24 - 62],
        )
        slots.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        body = header + [Spacer(1, 4), slots, Spacer(1, 8), dinner_block(day)]
        if day.attractions:
            body += [Spacer(1, 8), PillRow([(a, BRASS, BRASS_BG, BRASS_BORDER, "Inter", 7.5) for a in day.attractions])]

        row = Table([[DayBadge(day.day), body]], colWidths=[40, CONTENT_W - 28 - 40])
        row.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(KeepTogether([card([row]), Spacer(1, 10)]))

    # ================= OPTIONS =================
    def options_table(header, rows, fractions):
        widths = [(CONTENT_W - 28) * f for f in fractions[:-1]]
        widths.append(CONTENT_W - 28 - sum(widths))
        table = Table([[Paragraph(h, S_TH) for h in header]] + rows, colWidths=widths)
        style = [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("ROUNDEDCORNERS", [6] * 4),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]
        for i in range(1, len(rows) + 1):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0, i), (-1, i), PAPER))
        table.setStyle(TableStyle(style))
        return table

    if it.flight_comparison:
        rows = [[
            Paragraph(_t(fc.airline), S_TD),
            Paragraph(money(fc.price), S_TD_MONO),
            Paragraph(_t(f"{fc.outbound.duration} · {_stops(fc.outbound.stops)}" if fc.outbound else fc.duration), S_TD_SOFT),
            Paragraph(_t(f"{fc.return_leg.duration} · {_stops(fc.return_leg.stops)}" if fc.return_leg else "—"), S_TD_SOFT),
            Paragraph(f"<font color='#2F7A4F'>+</font> {_t(fc.pros)}"
                      + (f"<br/><font color='#B23B3B'>−</font> {_t(fc.cons)}" if fc.cons else ""), S_TD),
        ] for fc in it.flight_comparison]
        story.append(KeepTogether([card([
            SectionTitle("Other flight options", "PRICE IS ROUND TRIP PER TRAVELER"), Spacer(1, 8),
            options_table(["AIRLINE", "PRICE", "OUTBOUND", "RETURN", "PROS / CONS"], rows, [0.17, 0.12, 0.15, 0.15, 0.41]),
        ]), Spacer(1, 12)]))

    if it.hotel_comparison:
        rows = [[
            Paragraph(_t(hc.name), S_TD),
            Paragraph(f"<font color='#B8862F'>★</font> {hc.rating}", S_TD),
            Paragraph(money(hc.estimated_cost), S_TD_MONO),
            Paragraph(f"<font color='#2F7A4F'>+</font> {_t(hc.pros)}"
                      + (f"<br/><font color='#B23B3B'>−</font> {_t(hc.cons)}" if hc.cons else ""), S_TD),
        ] for hc in it.hotel_comparison]
        story.append(KeepTogether([card([
            SectionTitle("Other hotel options", "TOTAL FOR THE STAY"), Spacer(1, 8),
            options_table(["HOTEL", "RATING", "TOTAL", "PROS / CONS"], rows, [0.27, 0.1, 0.14, 0.49]),
        ]), Spacer(1, 12)]))

    # ================= TIPS =================
    half = (CONTENT_W - 12) / 2
    saving_rows = [[Paragraph(_t(tip.tip), _style("tip", size=8.5, leading=12)),
                    Paragraph(f"−{money(tip.estimated_saving)}", _style("tipv", font="Mono-SemiBold", size=8.5, color=GREEN, alignment=2))]
                   for tip in it.money_saving_tips]
    saving_table = Table(saving_rows or [[Paragraph("—", S_SMALL), ""]], colWidths=[half - 28 - 62, 62])
    saving_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                      ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    travel_tips = [Paragraph(f"<font color='#B8862F'>·</font>&nbsp; {_t(tip)}", _style("tt", size=8.5, leading=12, spaceAfter=5))
                   for tip in it.travel_tips] or [Paragraph("—", S_SMALL)]
    tips = Table([[
        card([SectionTitle("Money-saving tips"), Spacer(1, 8), saving_table], width=half),
        card([SectionTitle("Travel tips"), Spacer(1, 8)] + travel_tips, width=half),
    ]], colWidths=[half + 12, half])
    tips.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                              ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0)]))
    story.append(KeepTogether([tips, Spacer(1, 12)]))

    # ================= CONFIDENCE & NOTES =================
    conf = it.confidence

    def chip(label, level):
        lv = str(level).lower()
        fg, bg = (GREEN, GREEN_BG) if lv.startswith("high") else (RED, RED_BG) if lv.startswith("low") else (BRASS, BRASS_BG)
        return (f"{label}: {level}", fg, bg, None, "Inter-SemiBold", 7.5)

    chips = PillRow([chip("Flight", conf.flight), chip("Hotel", conf.hotel), chip("Food", conf.food),
                     chip("Transport", conf.transport), chip("Misc", conf.miscellaneous)])
    notes = [
        "Flight offers come from the Duffel API and can change at any time before booking.",
        "Hotel rates and meal costs are AI estimates; restaurant prices are checked against Google price ranges.",
        "Exchange rates are live but may move before you book.",
        "Check hotel availability and attraction opening hours before travelling.",
    ]
    story.append(KeepTogether([card(
        [SectionTitle("Data confidence & notes"), Spacer(1, 8), chips, Spacer(1, 10)]
        + [Paragraph(f"<font color='#B8862F'>·</font>&nbsp; {_t(n)}", S_SMALL) for n in notes]
    )]))

    # ================= PAGE DECORATION =================
    status = it.trip_status
    generated = datetime.now()

    def draw_cover(c, doc_):
        c.saveState()
        c.setFillColor(NAVY)
        c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
        # decorative flight path: origin dot -> dashed arc -> plane
        c.setStrokeColor(_mix(NAVY, BRASS, 0.55))
        c.setLineWidth(1.1)
        c.setDash(4, 5)
        sx, sy, ex, ey = PAGE_W * 0.42, PAGE_H * 0.80, PAGE_W - 70, PAGE_H * 0.66
        path = c.beginPath()
        path.moveTo(sx, sy)
        path.curveTo(sx + 120, sy + 110, ex - 30, ey + 150, ex, ey + 18)
        c.drawPath(path, stroke=1, fill=0)
        c.setDash()
        c.setFillColor(BRASS_LIGHT)
        c.circle(sx, sy, 3.5, stroke=0, fill=1)
        c.setFillColor(_mix(NAVY, BRASS, 0.25))
        c.circle(ex, ey, 9, stroke=0, fill=1)
        c.setFillColor(BRASS_LIGHT)
        c.circle(ex, ey, 3.5, stroke=0, fill=1)
        c.saveState()
        c.translate(ex + 2, ey + 26)
        c.rotate(-80)
        _plane(c, -7, -5, 15, BRASS_LIGHT)
        c.restoreState()
        c.setFillColor(WHITE_45)
        c.setFont("Mono-SemiBold", 8)
        c.drawCentredString(sx, sy - 16, origin)
        c.drawCentredString(ex, ey - 20, dest)

        x = 54
        _plane(c, x, PAGE_H - 70, 13, BRASS_LIGHT)
        _spaced(c, x + 20, PAGE_H - 69, "VOYAGE AI", "Mono-SemiBold", 10, BRASS_LIGHT, 3)

        y = PAGE_H * 0.58
        _spaced(c, x, y + 70, "YOUR TRIP TO", "Mono", 9, BRASS_LIGHT, 2.5)

        size = 58 if pdfmetrics.stringWidth(trip.destination, "Display", 58) < PAGE_W - 2 * x else 40
        c.setFillColor(colors.white)
        c.setFont("Display", size)
        c.drawString(x, y, trip.destination)

        c.setFillColor(WHITE_90)
        c.setFont("Inter", 13)
        dep, ret = _date(trip.departure_date, "%d %b"), _date(trip.return_date, "%d %b %Y")
        c.drawString(x, y - 30, f"{trip.departure_city}  →  {trip.destination}   ·   {dep} – {ret}")

        c.setStrokeColor(BRASS)
        c.setLineWidth(1.5)
        c.line(x, y - 48, x + 70, y - 48)

        # Stat tiles
        tiles = [
            ("DAYS", str(days_count)),
            ("TRAVELERS", str(trip.travelers)),
            ("ESTIMATED COST", money(budget.total)),
            ("BUDGET", money(trip.budget)),
        ]
        tw, th, gap = (PAGE_W - 2 * x - 3 * 10) / 4, 58, 10
        ty = y - 130
        for i, (label, value) in enumerate(tiles):
            tx = x + i * (tw + gap)
            c.setFillColor(NAVY_LIGHT)
            c.roundRect(tx, ty, tw, th, 9, stroke=0, fill=1)
            c.setFillColor(WHITE_45)
            c.setFont("Mono", 6.8)
            c.drawString(tx + 12, ty + th - 18, label)
            c.setFillColor(colors.white)
            c.setFont("Inter-Bold", 15 if len(value) < 10 else 12.5)
            c.drawString(tx + 12, ty + 15, value)

        # Status pill
        ok = status.is_affordable
        label = (f"AFFORDABLE  ·  {money(budget.remaining)} LEFT" if ok
                 else f"OVER BUDGET  ·  {money(abs(budget.remaining))} SHORT")
        pw = pdfmetrics.stringWidth(label, "Mono-SemiBold", 8) + 1 * len(label) + 24
        c.setFillColor(GREEN if ok else RED)
        c.roundRect(x, ty - 40, pw, 22, 11, stroke=0, fill=1)
        _spaced(c, x + 12, ty - 32.5, label, "Mono-SemiBold", 8, colors.white, 1)

        # Flight + stay summary
        c.setFillColor(WHITE_60)
        c.setFont("Inter", 9)
        c.drawString(x, 120, f"Flight   {flight.airline} · {origin} → {dest}")
        c.drawString(x, 104, f"Stay      {it.selected_hotel.name}")
        c.setStrokeColor(_mix(NAVY, colors.white, 0.15))
        c.setLineWidth(0.6)
        c.line(x, 84, PAGE_W - x, 84)
        c.setFillColor(WHITE_45)
        c.setFont("Mono", 7)
        c.drawString(x, 66, "AI-GENERATED TRAVEL ITINERARY")
        c.drawRightString(PAGE_W - x, 66, f"PREPARED BY VOYAGE AI · {generated.day} {generated:%b %Y}".upper())
        c.restoreState()

    def draw_page(c, doc_):
        c.saveState()
        c.setFillColor(PAPER)
        c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
        # header
        _plane(c, MARGIN, PAGE_H - 30, 8, BRASS)
        _spaced(c, MARGIN + 13, PAGE_H - 29.5, "VOYAGE AI", "Mono-SemiBold", 7.5, BRASS, 1.8)
        c.setFillColor(INK_SOFT)
        c.setFont("Inter", 7.5)
        c.drawRightString(PAGE_W - MARGIN, PAGE_H - 29.5,
                          f"{trip.destination}  ·  {_date(trip.departure_date, '%d %b')} – {_date(trip.return_date, '%d %b %Y')}")
        c.setStrokeColor(LINE)
        c.setLineWidth(0.6)
        c.line(MARGIN, PAGE_H - 38, PAGE_W - MARGIN, PAGE_H - 38)
        # footer
        c.setFillColor(INK_SOFT)
        c.setFont("Mono", 7)
        c.drawString(MARGIN, 22, "AI-generated itinerary · verify prices before booking")
        c.drawRightString(PAGE_W - MARGIN, 22, f"PAGE {c.getPageNumber() - 1}")
        c.restoreState()

    doc.build(story, onFirstPage=draw_cover, onLaterPages=draw_page)
    return buffer.getvalue()


def save_pdf(itinerary: Itinerary, output_filename: str = "Voyage_AI_Itinerary.pdf"):
    """CLI helper: write the PDF to disk."""

    output_dir = os.path.dirname(output_filename)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_filename, "wb") as fh:
        fh.write(build_pdf(itinerary))
