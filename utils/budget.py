def calculate_budget_percentages(budget):

    if budget.total <= 0:
        return budget

    budget.flight_percent = round(
        budget.flights / budget.total * 100, 1
    )

    budget.hotel_percent = round(
        budget.hotel / budget.total * 100, 1
    )

    budget.food_percent = round(
        budget.food / budget.total * 100, 1
    )

    budget.transport_percent = round(
        budget.transport / budget.total * 100, 1
    )

    budget.miscellaneous_percent = round(
        budget.miscellaneous / budget.total * 100, 1
    )

    return budget