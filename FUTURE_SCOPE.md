# Voyage AI — Future Scope & Known Limitations

This file tracks what Voyage AI does not do yet, why, and how each item would be implemented.
It is kept up to date as the project evolves.

_Last updated: 2026-11-26_

---

## 1. Flights

### 1.1 Switch Duffel from test mode to live mode
- **Current state:** The project uses a Duffel **test** key (`duffel_test_...`). Test mode returns sample data,
  including the fictional airline **"Duffel Airways" (code `ZZ`)**. Prices and schedules are not real.
- **Why it matters:** Users see sample flights, and the AI often picks the fake direct "Duffel Airways" offer
  because it is cheap and non-stop.
- **Implementation:**
  1. Verify the Duffel account and generate a live key (`duffel_live_...`).
  2. Replace `DUFFEL_API_KEY` in `.env` (local) and in the Render environment settings.
  3. No code change is required. The request format is the same in both modes.
- **Before switching:** Check Duffel's current pricing. Duffel earns money per booking and may charge for searches
  when the search-to-booking ratio is very high. Voyage AI only searches and never books.

### 1.2 Search with one passenger per traveler (true group fares)
- **Current state:** `tools/flights.py` searches for **1 adult**. The per-person price is then multiplied by the
  number of travelers in code.
- **Why it matters:** Airlines may have only a few seats left at the cheapest fare, so a group can pay more per person.
  Multiplying a single-seat fare underestimates group cost.
- **Implementation:** Send `passengers: [{"type": "adult"}] * travelers` to Duffel and use the offer's
  `total_amount` as the group price (and `total_amount / travelers` for per-person display).
  This only matters once live mode (1.1) is enabled.

### 1.3 Show the group flight total on the boarding pass
- **Current state:** The boarding pass and flight list show the **per-person** round-trip price. The group total
  (price × travelers) appears only in the budget breakdown.
- **Implementation:** Add a line under the price, for example "₹42,032 × 2 travelers = ₹84,064".

### 1.4 Hide sample-airline offers while in test mode (optional)
- **Implementation:** Filter out offers where `airline_code == "ZZ"` in `tools/flights.py`, and show a
  "sample flight data" label in the UI while a test key is in use.

### 1.5 More flight providers
- Add a second provider (for example Amadeus Self-Service or Kiwi Tequila) for wider coverage and price comparison.

---

## 2. Hotels

### 2.1 Real hotel prices
- **Current state:** Google Places provides hotel names, ratings and review counts but **no room prices**.
  Nightly rates are estimated by the LLM (total = nightly rate × nights is calculated in code).
- **Implementation:** Integrate a hotel-pricing API (for example Amadeus Hotel Search, Duffel Stays or
  Booking.com Demand API) and pass real nightly rates to the itinerary agent.

### 2.2 Smarter hotel search
- **Current state:** `agents/hotel_agent.py` runs one Google Places text search, `"hotel in {destination city}"`,
  and keeps the top 5 results. The search is independent of the flight: it doesn't use the arrival airport,
  arrival/departure times, trip dates, availability or the budget. The AI then picks one based on rating,
  review count and location.
- **Why it matters:** Results can all be outside the user's budget or unavailable on the trip dates, and for
  very late arrivals / very early departures a night near the airport can be more practical.
- **Implementation:**
  1. Add the budget style to the query (e.g. "budget hotel", "mid-range hotel", "luxury hotel") or filter by `priceLevel`.
  2. Bias results toward the city centre or the main attractions with the Places `locationBias` parameter.
  3. When the flight lands after ~23:00 or departs before ~07:00, also search "hotel near {airport}" and suggest an
     airport hotel for that night.
  4. Check real availability and prices for the trip dates with a hotel-booking API (see 2.1).

---

## 3. Restaurants & Food

### 3.1 Validate dinner picks in code
- **Current state:** A prompt rule now forbids picking hotels as dinner, but nothing checks it in code.
- **Implementation:** Validate in code that each dinner pick's name exists in the fetched restaurant list
  (fuzzy match), and flag or replace picks that don't.

### 3.1b High-end prices are still only partly grounded
- **Current state:** Restaurant prices are checked against Google's per-person price range. Bounded ranges
  (e.g. "THB 200-400") make everyday prices accurate, but Google's top bucket is open-ended ("THB 2000+"),
  so fine-dining prices are only raised to at least 1.5× that minimum — still below real tasting-menu prices
  in some cities.
- **Implementation:** Use a source with real menu prices (e.g. restaurant websites / booking platforms), or
  maintain a small per-city table of typical fine-dining prices.

### 3.1c Enforce the mid-range rule for the recommended dinner in code
- **Current state:** The prompt forbids $$$$ restaurants as the recommended dinner, but the model occasionally
  still picks one (seen once after "Regenerate itinerary": Godaime Wagyu Tokyo).
- **Implementation:** After the AI responds, if the recommended dinner's Google tier is $$$$, swap in the
  cheapest unused $$–$$$ restaurant from the fetched list.

### 3.2 Real distances instead of estimates
- **Current state:** `distance_km` on restaurants is estimated by the LLM.
- **Implementation:** Request `places.location` from Google Places and compute the distance in code
  (haversine formula) from the hotel or the day's main attraction.

### 3.3 Confirm Google Places billing for price fields
- `priceLevel` and `priceRange` were added to the Places field mask so dinner tiers use real data.
  Confirm on Google's pricing page that this does not move requests to a more expensive SKU.

### 3.4 Places request cost
- Each trip now makes **4** Places Text Search requests (hotels, attractions, popular restaurants, fine-dining
  restaurants). Monitor Google Places billing; cache results per city for a few hours to cut repeat costs.

---

## 4. AI Quality & Trust

### 4.1 Automated evaluation
- Build a small LangSmith evaluation dataset (fixed trip inputs) and check: budget arithmetic, no repeated
  restaurants/attractions, dinner tiers respected, all days populated.

### 4.2 Monitor cost per itinerary
- Measured in LangSmith (8-day Tokyo trip, `gemini-3.5-flash-lite`): ≈ $0.02 per full plan (~17K tokens) and
  ≈ $0.01 per regenerate (~11K tokens), before the compact-JSON optimisation. Re-measure after deployment and
  update the README figures; consider caching Places results per city to cut repeat costs.

### 4.3 Layover details
- Show the layover city and waiting time for one-stop flights (e.g. "1 stop · 14 hr in Singapore").
  Duffel's response already contains every segment.

---

## 5. Feature Roadmap

Effort: 🟢 small (a day or two) · 🟡 medium (about a week) · 🔴 large (needs accounts, payments or partners)

### 5.1 Visual & maps
| Feature | What it adds | How | Effort |
|---|---|---|---|
| 📸 Photos of hotels, restaurants & attractions | A photo on every hotel card, dinner box and attraction; a destination hero image on the results page and PDF cover | Add `places.photos` to the Google Places field mask, then fetch images with the Place Photos API (billed per photo — cache them). Unsplash API as a free fallback for city hero images | 🟢 |
| 🗺️ Map links | "Open in Google Maps" on every hotel, restaurant and attraction | Request `places.googleMapsUri` (or build a maps search URL) — no extra API call | 🟢 |
| 🗺️ Day route map | A small map per day with the hotel, attractions and dinner pinned in visiting order | Request `places.location`; render with Google Maps JavaScript API or Leaflet + OpenStreetMap (free) | 🟡 |
| 📍 Real distances & travel times | "12 min by metro from your hotel" instead of AI-estimated km | Haversine distance from `places.location`; Google Routes API for transit times | 🟡 |

### 5.2 Booking
| Feature | What it adds | How | Effort |
|---|---|---|---|
| 🔗 "Book this" deep links | One-click links to book the chosen flight and hotel on partner sites | Affiliate/deep links (Booking.com, Skyscanner, Agoda, Google Hotels/Flights) — no payment handling | 🟢 |
| ✈️ Real flight booking | Book the selected flight inside Voyage AI | Duffel **live** mode: create an order via the Orders API, take payment with Duffel Payments, collect passenger details (name, DOB, passport) | 🔴 |
| 🏨 Real hotel booking | Book the selected hotel inside Voyage AI | Duffel Stays, Amadeus Hotel Booking or Booking.com Demand API (partner approval required) | 🔴 |
| 🎟️ Attraction tickets & tours | Bookable tickets for the day's attractions (Skytree, Grand Palace…) with real prices | GetYourGuide or Viator partner APIs | 🟡 |
| 🔔 Flight price alerts | Email when the chosen route gets cheaper | Scheduled job re-running the Duffel search + email (e.g. Resend/SendGrid) | 🟡 |

### 5.3 Smarter planning
| Feature | What it adds | How | Effort |
|---|---|---|---|
| 🌦️ Weather-aware plans | Indoor activities on rainy days; forecast shown per day | Open-Meteo (free, no key) daily forecast passed into the itinerary prompt | 🟢 |
| 🧳 Traveler preferences | Vegetarian/halal food, pace (relaxed/packed), interests (food, culture, nightlife, shopping), budget style | Extra form fields → prompt rules + restaurant/attraction search queries | 🟢 |
| 💬 Chat to edit the plan | "Make day 3 more relaxed", "swap dinner for something vegetarian" | Re-use the LangGraph conversation path (checkpointer per user session) to edit single days | 🟡 |
| 🎉 Local events | Concerts, festivals and markets happening during the trip dates | Ticketmaster Discovery or PredictHQ API | 🟡 |
| 🌍 Any city & multi-city trips | Search any destination; trips like Tokyo → Kyoto → Osaka | Replace the hard-coded airport table with Duffel's Places/airports API; chain multiple legs | 🟡 |
| 🛂 Visa & entry requirements | Visa, passport validity and health requirements for the traveler's nationality | Sherpa° or similar travel-requirements API | 🟡 |
| 💱 More currencies | EUR, GBP, AED, etc. | Exchange-rate API already supports them; extend the currency list and symbols | 🟢 |

### 5.4 User experience
| Feature | What it adds | How | Effort |
|---|---|---|---|
| 👤 Accounts & saved trips | Log in, save trips, reopen them later | Auth (Supabase/Firebase/Clerk) + a database (Postgres/Supabase) | 🟡 |
| 🔗 Share a trip | Public read-only link to an itinerary | Store the itinerary JSON with a share ID; read-only results page | 🟢 |
| 📅 Calendar export | Add each day's plan and flights to Google/Apple Calendar | Generate an `.ics` file from the days and flight legs | 🟢 |
| 📤 Send PDF by email / WhatsApp | Share the PDF in one tap | Email service API; WhatsApp share link with the PDF URL | 🟢 |
| 🌐 Multiple languages | Hindi and other languages for the UI and itinerary | i18n in React + ask the LLM to answer in the chosen language | 🟡 |
| 📱 Mobile app / offline PDF | Itinerary available offline while travelling | PWA (installable web app) caching the last trip | 🟡 |

### 5.5 Recommended next steps for the project demo
1. **Photos + map links (5.1)** — the biggest visual upgrade for the least work.
2. **Weather-aware plans (5.3)** — free API, shows the AI adapting to real-world data.
3. **"Book this" deep links (5.2)** — makes the plan actionable without payment complexity.

### 5.6 Clean-up
- 🧹 Remove the unused alternative PDF builder files in `utils/pdfs/` (cover.py, sections.py, helpers.py, itinerary.py).

---

## 6. Engineering & Deployment

- **Render cold starts:** The free instance sleeps; the frontend waits up to ~60 s on `/ping`.
  A paid instance or a scheduled keep-alive ping would remove the delay.
- **`.env.example`:** Add one with placeholder values (the README lists the variables to set).
- **`requirements.txt` encoding:** The file is saved as UTF-16. Re-save it as UTF-8 for wider tool compatibility,
  and remove notebook-only packages (ipykernel, jupyter) from the production requirements.
- **Tests:** Add unit tests for budget recalculation, date/night math, duration formatting and flight enrichment,
  plus an API test for `/plan` with mocked external services.

---

## Recently Completed (for reference)

| Improvement | Details |
|---|---|
| Structured API input | `/plan` takes form fields directly; the LLM extractor is skipped for API requests (one fewer LLM call) |
| Correct trip length | Nov 28 → Dec 5 = 7 nights / 8 days; hotel cost = nightly rate × nights in code |
| Return flight details | Outbound and return legs (times, duration, stops) filled from live Duffel data, not the LLM |
| Duration formatting | Multi-day ISO durations (`P1DT6H15M` → "30 hr 15 min") |
| Stateless API | No shared conversation memory between users; CLI keeps its own memory |
| Travelers & currency | Travelers selectable (1–9); INR/USD carried through prompt, conversion and UI |
| Budget recalculated in code | Flights, hotel, food, total and remaining computed deterministically |
| Dinner options | Per day: recommended mid-range dinner + fine-dining alternative, user-selectable |
| Breakfast/lunch allowance | Per-person café/convenience-store estimate per day; food total = Σ(dinner + allowance) × travelers |
| Real price tiers | Google Places `priceLevel` / `priceRange` used to classify restaurants |
| Regenerate itinerary | Changing the hotel or flight shows a banner; `/itinerary` re-plans only the days (~13 s vs ~35 s) without new API calls |
| Flight-time-aware days | Code computes arrival/return notes (travel days, late arrivals, midnight check-out) and the model follows them |
| Day dates | Each day shows its calendar date |
| Genuine fine dining | Dedicated "fine dining restaurants" Places search; fine dining on every evening at the destination |
| No duplicates | Selected hotel/flight never repeated in comparison lists; attractions never repeated across days |
| Google price-range check | Restaurant prices are pulled into Google's per-person price range (midpoint if outside; open-ended top tier lifted to ≥1.5× its minimum while keeping differences); the range is shown on each dinner card |
| PDF download | "Download PDF" builds a PDF of exactly what's on screen — chosen flight/hotel, regenerated days, fine-dining picks — with the budget recalculated |
| Designed PDF | PDF matches the web app: navy cover with route graphic and stat tiles, boarding-pass card, budget bar, day timeline cards, attraction pills, confidence chips; Fraunces / Inter / IBM Plex Mono fonts (OFL, in `fonts/`); named like `Delhi_to_Tokyo_8_Days_Plan.pdf` |
| PDF always up to date | Download regenerates the days first if the hotel/flight changed; "YOUR PICK" vs "AI PICK" badges; fine-dining picks labelled |
| Travel days | Days with an overnight flight or early departure show "dinner at the airport or on board" and exclude dinner from the food cost |
| Consistent restaurant prices | Regenerated days reuse each restaurant's price from the first plan; price tier ($–$$$$) always from Google; prompt gives the local currency rate (e.g. 1 JPY = 0.58 INR) |
| Honest minimum prices | When Google only gives an open-ended range ("JPY 10000+") and the AI's estimate is below it, the price is shown as "from ₹8,700"; tier shown as $–$$$$, never a raw currency range |
| Travel-day meals | Travel days keep a breakfast/lunch allowance (≈80% of a normal day) even if the model leaves it at 0 |
| Cleaner AI output | Code resets fields only it may set (dates, travel days, "from" prices, savings) after every AI response; fine-dining prices use the model's knowledge of each specific restaurant |
| Lower token usage | Data is sent to the AI as compact JSON with native (non-escaped) characters |
| PDF text fix | Accented names (e.g. "Héritage") are normalised before rendering |
| Confidence from data source | Flight High (live offer), hotel/food/transport/misc Medium (estimates), set in code |
