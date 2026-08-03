import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(
    TTFont(
        "DejaVuSans",
        "fonts/DejaVuSans.ttf"
    )
)

pdfmetrics.registerFont(
    TTFont(
        "DejaVuSans-Bold",
        "fonts/DejaVuSans-Bold.ttf"
    )
)
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from utils.formatter import format_duration
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from schemas.itinerary import Itinerary

# ----------------------------------------------------------------
# Safe Font Registration with Helvetica Fallback
# ----------------------------------------------------------------
FONT_REGULAR = "DejaVuSans"
FONT_BOLD = "DejaVuSans-Bold"

RUPEE = "\u20B9"

def save_pdf(itinerary: Itinerary, output_filename: str = "Voyage_AI_Itinerary.pdf"):
    output_dir = os.path.dirname(output_filename)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()

    # ---------------- Typography ----------------
    cover_brand_style = ParagraphStyle(
        "CoverBrand", alignment=TA_CENTER,
        fontName=FONT_BOLD, fontSize=14, leading=18,
        textColor=colors.HexColor("#93C5FD"), spaceAfter=20,
    )
    cover_destination_style = ParagraphStyle(
        "CoverDestination", alignment=TA_CENTER,
        fontName=FONT_BOLD, fontSize=38, leading=44,
        textColor=colors.white, spaceAfter=18,
    )
    cover_dates_style = ParagraphStyle(
        "CoverDates", alignment=TA_CENTER,
        fontName=FONT_REGULAR, fontSize=13, leading=18,
        textColor=colors.HexColor("#E2E8F0"), spaceAfter=6,
    )
    cover_meta_style = ParagraphStyle(
        "CoverMeta", alignment=TA_CENTER,
        fontName=FONT_REGULAR, fontSize=11, leading=15,
        textColor=colors.HexColor("#94A3B8"), spaceAfter=4,
    )
    cover_footer_style = ParagraphStyle(
        "CoverFooter", alignment=TA_CENTER,
        fontName=FONT_REGULAR, fontSize=10, leading=13,
        textColor=colors.HexColor("#64748B"),
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        fontName=FONT_BOLD, fontSize=13, leading=16,
        textColor=colors.HexColor("#1E293B"), spaceBefore=10, spaceAfter=6,
    )
    table_header = ParagraphStyle(
        "TableHeader",
        fontName=FONT_BOLD, fontSize=9.5, leading=13,
        textColor=colors.HexColor("#334155"),
    )
    table_value = ParagraphStyle(
        "TableValue",
        fontName=FONT_REGULAR, fontSize=9.5, leading=13,
        textColor=colors.HexColor("#0F172A"),
    )
    budget_header = ParagraphStyle(
        "BudgetHeader",
        fontName=FONT_BOLD, fontSize=9.5, leading=13,
        textColor=colors.white,
    )
    comparison_header = ParagraphStyle(
        "ComparisonHeader",
        fontName=FONT_BOLD, fontSize=9, leading=12,
        textColor=colors.white,
    )
    comparison_value = ParagraphStyle(
        "ComparisonValue",
        fontName=FONT_REGULAR, fontSize=8.5, leading=11,
        textColor=colors.HexColor("#0F172A"),
    )
    index_day_style = ParagraphStyle(
        "IndexDay", alignment=TA_LEFT,
        fontName=FONT_BOLD, fontSize=10.5, leading=14,
        textColor=colors.HexColor("#1565C0"),
    )
    index_highlight_style = ParagraphStyle(
        "IndexHighlight", alignment=TA_LEFT,
        fontName=FONT_REGULAR, fontSize=9.5, leading=13,
        textColor=colors.HexColor("#334155"),
    )

    story = []
    printable_width = doc.width
    k_col1 = 140
    k_col2 = printable_width - k_col1

    def make_row(key: str, val: str):
        return [Paragraph(f"<b>{key}</b>", table_header), Paragraph(str(val), table_value)]

    # ============================================================
    # COVER PAGE
    # ============================================================
    trip = itinerary.trip_summary

    # Reduced Spacers to prevent accidental overflow
    story.append(Spacer(1, 120))
    story.append(Paragraph("✈ &nbsp; V O Y A G E &nbsp; A I", cover_brand_style))
    story.append(Paragraph(trip.destination, cover_destination_style))

    divider = Table([[""]], colWidths=[80], rowHeights=[1.2])
    divider.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, -1), 1.2, colors.HexColor("#3B82F6")),
    ]))
    divider.hAlign = "CENTER"
    story.append(divider)
    story.append(Spacer(1, 18))

    story.append(Paragraph(f"{trip.departure_date}  →  {trip.return_date}", cover_dates_style))
    story.append(Paragraph(
        f"{trip.travelers} traveler{'s' if trip.travelers != 1 else ''}  ·  "
        f"{trip.currency} {trip.budget:,.0f} budget  ·  from {trip.departure_city}",
        cover_meta_style,
    ))

    story.append(Spacer(1, 140))
    story.append(Paragraph("AI-GENERATED TRAVEL ITINERARY", cover_footer_style))
    story.append(PageBreak())

    # ============================================================
    # DAY INDEX
    # ============================================================
    if len(itinerary.itinerary) > 1:
        story.append(Paragraph("Trip at a Glance", section_heading))
        story.append(Spacer(1, 4))

        index_rows = []
        for day in itinerary.itinerary:
            highlight = day.attractions[0] if day.attractions else day.morning
            index_rows.append([
                Paragraph(f"Day {day.day}", index_day_style),
                Paragraph(highlight, index_highlight_style),
            ])

        index_table = Table(index_rows, colWidths=[70, printable_width - 70])
        index_table.setStyle(TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(index_table)
        story.append(Spacer(1, 20))

    # ============================================================
    # TRIP SUMMARY
    # ============================================================
    story.append(Paragraph("Trip Summary", section_heading))
    summary_table = Table([
        make_row("Destination", trip.destination),
        make_row("Departure City", trip.departure_city),
        make_row("Departure Date", trip.departure_date),
        make_row("Return Date", trip.return_date),
        make_row("Travelers", str(trip.travelers)),
        make_row("Budget", f"{trip.currency} {trip.budget:,.0f}"),
    ], colWidths=[k_col1, k_col2])
    summary_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E3F2FD")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 15))

    # ============================================================
    # SELECTED FLIGHT
    # ============================================================
    flight = itinerary.selected_flight
    story.append(Paragraph("Selected Flight", section_heading))
    flight_table = Table([
        make_row(
        "Airline",
        flight.airline
        ),

        make_row(
        "Code",
        flight.airline_code
        ),
        make_row("Price (USD)", f"${flight.price_usd:,.2f}"),
        make_row("Price (INR)", f"{RUPEE}{flight.price_inr:,.0f}"),
        make_row("Stops", str(flight.stops)),
        make_row("Duration", format_duration(flight.duration)),
        make_row("Reason", flight.reason),
    ], colWidths=[k_col1, k_col2])
    flight_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#BBDEFB")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(flight_table)
    story.append(Spacer(1, 10))

    if itinerary.flight_comparison:
        story.append(Paragraph("Other Flight Options Considered", section_heading))
        rows = [[
            Paragraph("Airline", comparison_header),
            Paragraph("Price", comparison_header),
            Paragraph("Duration", comparison_header),
            Paragraph("Stops", comparison_header),
            Paragraph("Pros", comparison_header),
            Paragraph("Cons", comparison_header),
        ]]
        for fc in itinerary.flight_comparison:
            rows.append([
                Paragraph(fc.airline, comparison_value),
                Paragraph(f"${fc.price:,.2f}", comparison_value),
                Paragraph(fc.duration, comparison_value),
                Paragraph(str(fc.stops), comparison_value),
                Paragraph(fc.pros, comparison_value),
                Paragraph(fc.cons, comparison_value),
            ])
        
        # Calculate exact pixel widths to prevent rounding layout shifts
        widths = [
            printable_width * 0.16,
            printable_width * 0.12,
            printable_width * 0.14,
            printable_width * 0.08,
            printable_width * 0.25,
        ]
        widths.append(printable_width - sum(widths)) # remainder for final col

        fc_table = Table(rows, colWidths=widths)
        fc_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565C0")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(fc_table)
        story.append(Spacer(1, 15))

    # ============================================================
    # SELECTED HOTEL
    # ============================================================
    hotel = itinerary.selected_hotel
    story.append(Paragraph("Selected Hotel", section_heading))
    hotel_table = Table([
        make_row("Hotel", hotel.name),
        make_row("Rating", f"★ {hotel.rating}"),
        make_row("Reviews", f"{hotel.reviews:,}"),
        make_row("Nightly Estimate", f"{RUPEE}{hotel.estimated_nightly_cost:,.0f}"),
        make_row("Total Estimate", f"{RUPEE}{hotel.estimated_total_cost:,.0f}"),
        make_row("Reason", hotel.reason),
    ], colWidths=[k_col1, k_col2])
    hotel_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#C8E6C9")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(hotel_table)
    story.append(Spacer(1, 10))

    if itinerary.hotel_comparison:
        story.append(Paragraph("Other Hotel Options Considered", section_heading))
        rows = [[
            Paragraph("Hotel", comparison_header),
            Paragraph("Rating", comparison_header),
            Paragraph("Est. Cost", comparison_header),
            Paragraph("Pros", comparison_header),
            Paragraph("Cons", comparison_header),
        ]]
        for hc in itinerary.hotel_comparison:
            rows.append([
                Paragraph(hc.name, comparison_value),
                Paragraph(f"★ {hc.rating}", comparison_value),
                Paragraph(f"{RUPEE}{hc.estimated_cost:,.0f}", comparison_value),
                Paragraph(hc.pros, comparison_value),
                Paragraph(hc.cons, comparison_value),
            ])
            
        hc_widths = [
            printable_width * 0.22,
            printable_width * 0.12,
            printable_width * 0.16,
            printable_width * 0.25,
        ]
        hc_widths.append(printable_width - sum(hc_widths))

        hc_table = Table(rows, colWidths=hc_widths)
        hc_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E7D32")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(hc_table)
        story.append(Spacer(1, 15))

    # ============================================================
    # BUDGET
    # ============================================================
    budget = itinerary.budget
    story.append(Paragraph("Budget Breakdown", section_heading))
    b_col1 = printable_width * 0.6
    b_col2 = printable_width - b_col1
    budget_table = Table([
        [Paragraph("Expense Category", budget_header), Paragraph(f"Cost ({RUPEE})", budget_header)],
        [Paragraph("Flights", table_value), Paragraph(f"{RUPEE}{budget.flights:,.0f}", table_value)],
        [Paragraph("Hotel", table_value), Paragraph(f"{RUPEE}{budget.hotel:,.0f}", table_value)],
        [Paragraph("Food", table_value), Paragraph(f"{RUPEE}{budget.food:,.0f}", table_value)],
        [Paragraph("Transport", table_value), Paragraph(f"{RUPEE}{budget.transport:,.0f}", table_value)],
        [Paragraph("Miscellaneous", table_value), Paragraph(f"{RUPEE}{budget.miscellaneous:,.0f}", table_value)],
        [Paragraph("<b>TOTAL</b>", table_value), Paragraph(f"<b>{RUPEE}{budget.total:,.0f}</b>", table_value)],
        [Paragraph("<b>Remaining</b>", table_value), Paragraph(f"<b>{RUPEE}{budget.remaining:,.0f}</b>", table_value)],
    ], colWidths=[b_col1, b_col2])
    budget_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565C0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ]))
    story.append(budget_table)
    story.append(Spacer(1, 15))

    # ============================================================
    # MONEY SAVING TIPS
    # ============================================================
    if itinerary.money_saving_tips:
        story.append(Paragraph("Money Saving Tips", section_heading))
        for tip in itinerary.money_saving_tips:
            story.append(Paragraph(
                f"• <b>{tip.tip}</b> (Estimated Saving: {RUPEE}{tip.estimated_saving:,.0f})",
                table_value,
            ))
            story.append(Spacer(1, 3))
        story.append(Spacer(1, 10))

    # ============================================================
    # DAY-BY-DAY ITINERARY
    # ============================================================
    story.append(PageBreak())
    story.append(Paragraph("Day-by-Day Itinerary", section_heading))
    story.append(Spacer(1, 5))

    for day in itinerary.itinerary:
        story.append(Paragraph(f"<b>Day {day.day}</b>", section_heading))
        attractions_str = "<br/>".join([f"• {att}" for att in day.attractions])
        day_table = Table([
            make_row("🌅 Morning", day.morning),
            make_row("☀ Afternoon", day.afternoon),
            make_row("🌙 Evening", day.evening),
            make_row("🍜 Restaurant", day.restaurant),
            make_row("🎯 Attractions", attractions_str),
        ], colWidths=[k_col1, k_col2])
        day_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#FFF8E1")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(day_table)
        story.append(Spacer(1, 10))

    # ============================================================
    # TRAVEL TIPS
    # ============================================================
    if itinerary.travel_tips:
        story.append(Paragraph("Travel Tips", section_heading))
        for tip in itinerary.travel_tips:
            story.append(Paragraph(f"• {tip}", table_value))
            story.append(Spacer(1, 3))
        story.append(Spacer(1, 10))

    # ============================================================
# IMPORTANT NOTES
# ============================================================

    story.append(
        Paragraph(
            "Important Notes",
            section_heading
        )
    )

    notes = [

    "✔ Flight prices are fetched live and may change anytime.",

    "✔ Hotel prices are estimated based on city averages.",

    "✔ Food, transport and miscellaneous expenses are estimated.",

    "✔ Exchange rates may fluctuate before booking.",

    "✔ Verify hotel availability before making payments.",

    "✔ Attraction timings may change depending on holidays."

    ]

    for note in notes:

        story.append(
            Paragraph(
                note,
                table_value
            )
        )

        story.append(
            Spacer(1,4)
        )

    # ============================================================
    # CANVAS CALLBACKS
    # ============================================================
    # ============================================================
    # CANVAS CALLBACKS
    # ============================================================

    def draw_first_page(canvas, doc_):
        canvas.saveState()

        page_w, page_h = doc_.pagesize

        canvas.setFillColor(colors.HexColor("#0F172A"))
        canvas.rect(0, 0, page_w, page_h, fill=1, stroke=0)

        canvas.restoreState()


    def draw_later_pages(canvas, doc_):
        canvas.saveState()

        page_num = canvas.getPageNumber()

        canvas.setFont(FONT_REGULAR, 8)
        canvas.setFillColor(colors.HexColor("#64748B"))

        canvas.drawString(
            40,
            20,
            "Voyage AI"
        )

        canvas.drawRightString(
            doc_.pagesize[0]-40,
            20,
            f"Page {page_num-1}"
        )

        canvas.restoreState()


    doc.build(
        story,
        onFirstPage=draw_first_page,
        onLaterPages=draw_later_pages
    )