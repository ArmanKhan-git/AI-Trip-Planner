from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)

from reportlab.lib import colors

from schemas.itinerary import Itinerary
from utils.pdfs.styles import *


def build_itinerary(story, itinerary: Itinerary):

    story.append(
        Paragraph(
            "🗓 Day-by-Day Itinerary",
            SECTION
        )
    )

    story.append(Spacer(1, 15))

    for index, day in enumerate(itinerary.itinerary):

        # -------------------------------------------------
        # New page every 2 days
        # -------------------------------------------------

        if index != 0 and index % 2 == 0:
            story.append(PageBreak())

        # -------------------------------------------------
        # DAY TITLE
        # -------------------------------------------------

        story.append(
            Paragraph(
                f"🗓 DAY {day.day}",
                DAY_TITLE
            )
        )

        # -------------------------------------------------
        # TIMELINE TABLE
        # -------------------------------------------------

        table = Table(
            [

                ["🌅 Morning", day.morning],

                ["☀ Afternoon", day.afternoon],

                ["🌙 Evening", day.evening],

                ["🍜 Restaurant", day.restaurant],

                [
                    "🎯 Attractions",
                    "<br/>".join(day.attractions)
                ],

            ],
            colWidths=[130, 330]
        )

        table.setStyle(

            TableStyle([

                ("GRID",(0,0),(-1,-1),0.5,colors.grey),

                ("BACKGROUND",(0,0),(0,-1),LIGHT_ORANGE),

                ("BACKGROUND",(1,0),(1,-1),colors.white),

                ("BOTTOMPADDING",(0,0),(-1,-1),10),

                ("TOPPADDING",(0,0),(-1,-1),10),

                ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),

                ("VALIGN",(0,0),(-1,-1),"TOP"),

            ])

        )

        story.append(table)

        story.append(Spacer(1, 20))

    story.append(PageBreak())