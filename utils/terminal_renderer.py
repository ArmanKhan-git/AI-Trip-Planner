from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule

from schemas.itinerary import Itinerary

console = Console()


def render_itinerary(itinerary: Itinerary):

    console.clear()

    # ======================================================
    # HEADER
    # ======================================================

    console.print()

    console.print(
        Panel.fit(
            "[bold cyan]✈ VOYAGE AI[/bold cyan]\n"
            "[green]AI Powered Travel Planner[/green]",
            border_style="bright_blue",
        )
    )

    console.print()

    # ======================================================
    # TRIP SUMMARY
    # ======================================================

    trip = itinerary.trip_summary

    summary = Table(title="📍 Trip Summary")

    summary.add_column("Field", style="cyan")
    summary.add_column("Value", style="green")

    summary.add_row("Destination", trip.destination)
    summary.add_row("Departure", trip.departure_city)
    summary.add_row(
        "Dates",
        f"{trip.departure_date} → {trip.return_date}"
    )
    summary.add_row("Travelers", str(trip.travelers))
    summary.add_row(
        "Budget",
        f"{trip.currency}{trip.budget:,.0f}"
    )

    console.print(summary)

    # ======================================================
    # FLIGHT
    # ======================================================

    console.print(Rule("[bold blue]Selected Flight"))

    flight = itinerary.selected_flight

    flight_table = Table()

    flight_table.add_column("Property", style="cyan")
    flight_table.add_column("Value")

    flight_table.add_row("Airline", flight.airline)
    flight_table.add_row("Price", f"₹{flight.price_inr:,.0f}")
    flight_table.add_row("Stops", str(flight.stops))
    flight_table.add_row("Duration", flight.duration)

    console.print(flight_table)

    # ======================================================
    # HOTEL
    # ======================================================

    console.print(Rule("[bold green]Selected Hotel"))

    hotel = itinerary.selected_hotel

    hotel_table = Table()

    hotel_table.add_column("Property", style="cyan")
    hotel_table.add_column("Value")

    hotel_table.add_row("Hotel", hotel.name)
    hotel_table.add_row("Rating", str(hotel.rating))
    hotel_table.add_row(
        "Estimated Cost",
        f"₹{hotel.estimated_total_cost:,.0f}"
    )

    console.print(hotel_table)

    # ======================================================
    # BUDGET
    # ======================================================

    console.print(Rule("[bold yellow]Budget"))

    budget = itinerary.budget

    budget_table = Table()

    budget_table.add_column("Expense")
    budget_table.add_column("Cost", justify="right")

    budget_table.add_row(
        "Flights",
        f"₹{budget.flights:,.0f}"
    )

    budget_table.add_row(
        "Hotel",
        f"₹{budget.hotel:,.0f}"
    )

    budget_table.add_row(
        "Food",
        f"₹{budget.food:,.0f}"
    )

    budget_table.add_row(
        "Transport",
        f"₹{budget.transport:,.0f}"
    )

    budget_table.add_row(
        "Misc",
        f"₹{budget.miscellaneous:,.0f}"
    )

    budget_table.add_section()

    budget_table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold green]₹{budget.total:,.0f}[/bold green]"
    )

    budget_table.add_row(
        "[bold]Remaining[/bold]",
        f"[bold cyan]₹{budget.remaining:,.0f}[/bold cyan]"
    )

    console.print(budget_table)

    # ======================================================
    # ITINERARY
    # ======================================================

    console.print(Rule("[bold magenta]Day-wise Itinerary"))

    for day in itinerary.itinerary:

        attractions = "\n".join(
            f"• {x}" for x in day.attractions
        )

        text = f"""
🌅 Morning
{day.morning}

☀ Afternoon
{day.afternoon}

🌙 Evening
{day.evening}

🍜 Restaurant
{day.restaurant}

📍 Attractions
{attractions}
"""

        console.print(
            Panel(
                text,
                title=f"Day {day.day}",
                border_style="cyan",
            )
        )

    # ======================================================
    # MONEY SAVING
    # ======================================================

    console.print(Rule("[bold green]Money Saving Tips"))

    for tip in itinerary.money_saving_tips:

        console.print(
            f"💰 {tip.tip} "
            f"[green](Save ₹{tip.estimated_saving:,.0f})[/green]"
        )

    # ======================================================
    # TRAVEL TIPS
    # ======================================================

    console.print(Rule("[bold blue]Travel Tips"))

    for tip in itinerary.travel_tips:

        console.print(f"• {tip}")

    console.print()

    console.print(
        Panel.fit(
            "[bold green]✔ Itinerary Generated Successfully[/bold green]",
            border_style="green",
        )
    )