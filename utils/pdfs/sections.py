from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors

from schemas.itinerary import Itinerary

from utils.pdfs.styles import *
from utils.pdfs.styles import FOOTER


# ==========================================================
# FLIGHT
# ==========================================================

def build_flight_section(story, itinerary: Itinerary):

    flight = itinerary.selected_flight

    story.append(
        Paragraph(
            "✈ Selected Flight",
            SECTION
        )
    )

    table = Table([

        ["Airline", flight.airline],

        ["Airline Code", flight.airline_code],

        ["Price (USD)", f"${flight.price_usd:,.2f}"],

        ["Price (INR)", f"₹{flight.price_inr:,.0f}"],

        ["Duration", flight.duration],

        ["Stops", str(flight.stops)],

        ["Reason", flight.reason],

    ], colWidths=[150,320])

    table.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),0.5,colors.grey),

        ("BACKGROUND",(0,0),(0,-1),LIGHT_BLUE),

        ("BOTTOMPADDING",(0,0),(-1,-1),8),

        ("TOPPADDING",(0,0),(-1,-1),8),

        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),

    ]))

    story.append(table)

    story.append(Spacer(1,20))


# ==========================================================
# HOTEL
# ==========================================================

def build_hotel_section(story, itinerary: Itinerary):

    hotel = itinerary.selected_hotel

    story.append(
        Paragraph(
            "🏨 Selected Hotel",
            SECTION
        )
    )

    table = Table([

        ["Hotel", hotel.name],

        ["Rating", str(hotel.rating)],

        ["Reviews", str(hotel.reviews)],

        ["Nightly Estimate",
         f"₹{hotel.estimated_nightly_cost:,.0f}"],

        ["Total Estimate",
         f"₹{hotel.estimated_total_cost:,.0f}"],

        ["Reason", hotel.reason],

    ], colWidths=[150,320])

    table.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),0.5,colors.grey),

        ("BACKGROUND",(0,0),(0,-1),LIGHT_GREEN),

        ("BOTTOMPADDING",(0,0),(-1,-1),8),

        ("TOPPADDING",(0,0),(-1,-1),8),

        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),

    ]))

    story.append(table)

    story.append(Spacer(1,20))


# ==========================================================
# BUDGET
# ==========================================================

def build_budget_section(story, itinerary: Itinerary):

    budget = itinerary.budget

    story.append(
        Paragraph(
            "💰 Budget Breakdown",
            SECTION
        )
    )

    table = Table([

        ["Expense","Cost"],

        ["Flights",
         f"₹{budget.flights:,.0f}"],

        ["Hotel",
         f"₹{budget.hotel:,.0f}"],

        ["Food",
         f"₹{budget.food:,.0f}"],

        ["Transport",
         f"₹{budget.transport:,.0f}"],

        ["Miscellaneous",
         f"₹{budget.miscellaneous:,.0f}"],

        ["Grand Total",
         f"₹{budget.total:,.0f}"],

        ["Remaining",
         f"₹{budget.remaining:,.0f}"],

    ], colWidths=[220,180])

    table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),WARNING),

        ("TEXTCOLOR",(0,0),(-1,0),WHITE),

        ("GRID",(0,0),(-1,-1),0.5,colors.grey),

        ("BOTTOMPADDING",(0,0),(-1,-1),10),

        ("TOPPADDING",(0,0),(-1,-1),10),

        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

        ("FONTNAME",(0,-2),(-1,-1),"Helvetica-Bold"),

    ]))

    story.append(table)

    story.append(Spacer(1,20))


# ==========================================================
# MONEY SAVING
# ==========================================================

def build_money_saving_section(story, itinerary: Itinerary):

    story.append(
        Paragraph(
            "💡 Money Saving Tips",
            SECTION
        )
    )

    for tip in itinerary.money_saving_tips:

        story.append(

            Paragraph(

                f"• <b>{tip.tip}</b><br/>"

                f"Estimated Saving: "

                f"<font color='green'>"

                f"₹{tip.estimated_saving:,.0f}"

                f"</font>",

                BODY

            )

        )

        story.append(Spacer(1,10))


# ==========================================================
# TRAVEL TIPS
# ==========================================================

def build_travel_tips_section(story, itinerary: Itinerary):

    story.append(

        Paragraph(

            "🌍 Travel Tips",

            SECTION

        )

    )

    for tip in itinerary.travel_tips:

        story.append(

            Paragraph(

                f"• {tip}",

                BODY

            )

        )

    story.append(Spacer(1,20))


# ==========================================================
# IMPORTANT NOTES
# ==========================================================

def build_notes_section(story):

    story.append(

        Paragraph(

            "⚠ Important Notes",

            SECTION

        )

    )

    notes = [

        "Flight prices are live and may change.",

        "Hotel prices are estimated using seasonal averages.",

        "Food costs assume mid-range restaurants.",

        "Transportation assumes metro/public transport.",

        "Always verify attraction timings before visiting."

    ]

    for note in notes:

        story.append(

            Paragraph(

                f"• {note}",

                BODY

            )

        )

    story.append(Spacer(1,20))


# ==========================================================
# FOOTER
# ==========================================================

def build_footer(story):

    story.append(
        Spacer(1,25)
    )

    story.append(

        Paragraph(

            "<b>Generated by Voyage AI</b><br/>"

            "AI Powered Travel Planner",

            FOOTER

        )

    )