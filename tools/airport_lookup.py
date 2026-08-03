CITY_TO_AIRPORT = {
    # India — major metros (likely departure cities)
    "Delhi": "DEL",
    "Mumbai": "BOM",
    "Bengaluru": "BLR",
    "Hyderabad": "HYD",
    "Chennai": "MAA",
    "Kolkata": "CCU",
    "Pune": "PNQ",
    "Ahmedabad": "AMD",
    "Jaipur": "JAI",
    "Kochi": "COK",
    "Goa": "GOX",          # Manohar International (Mopa) — GOI (Dabolim) still active too
    "Lucknow": "LKO",
    "Chandigarh": "IXC",
    "Thiruvananthapuram": "TRV",
 
    # Japan
    "Tokyo": "NRT",
    "Osaka": "KIX",
    "Kyoto": "KIX",
 
    # Southeast & East Asia
    "Bangkok": "BKK",
    "Phuket": "HKT",
    "Bali": "DPS",
    "Singapore": "SIN",
    "Kuala Lumpur": "KUL",
    "Hong Kong": "HKG",
    "Seoul": "ICN",
    "Ho Chi Minh City": "SGN",
    "Hanoi": "HAN",
 
    # Middle East
    "Dubai": "DXB",
    "Abu Dhabi": "AUH",
    "Doha": "DOH",
 
    # Maldives
    "Male": "MLE",
 
    # Europe
    "London": "LHR",
    "Paris": "CDG",
    "Rome": "FCO",
    "Amsterdam": "AMS",
    "Frankfurt": "FRA",
    "Zurich": "ZRH",
    "Barcelona": "BCN",
    "Istanbul": "IST",
 
    # Oceania
    "Sydney": "SYD",
    "Melbourne": "MEL",
 
    # North America
    "New York": "JFK",
    "Los Angeles": "LAX",
    "San Francisco": "SFO",
    "Chicago": "ORD",
    "Toronto": "YYZ",
}


def get_airport_code(city: str):
    return CITY_TO_AIRPORT.get(city.title())