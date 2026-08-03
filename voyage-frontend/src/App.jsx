import React, { useState, useMemo } from "react";
import {
  Plane, Building2, MapPin, Utensils, Wallet, Send,
  ChevronDown, ChevronUp, CheckCircle2, TrendingDown,
  ArrowRight, RotateCcw, Star, ArrowUpDown, Check,
  Calendar, Users
} from "lucide-react";

// ---------------------------------------------------------------------
// Configure API endpoint
// ---------------------------------------------------------------------
const API_BASE_URL = "http://localhost:8000";

// ---------------------------------------------------------------------
// Airport / City Mapping Dataset
// ---------------------------------------------------------------------
const CITY_TO_AIRPORT = {
  // India — major metros
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
  "Goa": "GOX",
  "Lucknow": "LKO",
  "Chandigarh": "IXC",
  "Thiruvananthapuram": "TRV",

  // Japan
  "Tokyo": "NRT",
  "Osaka": "KIX",
  "Kyoto": "KIX",

  // Southeast & East Asia
  "Bangkok": "BKK",
  "Phuket": "HKT",
  "Bali": "DPS",
  "Singapore": "SIN",
  "Kuala Lumpur": "KUL",
  "Hong Kong": "HKG",
  "Seoul": "ICN",
  "Ho Chi Minh City": "SGN",
  "Hanoi": "HAN",

  // Middle East
  "Dubai": "DXB",
  "Abu Dhabi": "AUH",
  "Doha": "DOH",

  // Maldives
  "Male": "MLE",

  // Europe
  "London": "LHR",
  "Paris": "CDG",
  "Rome": "FCO",
  "Amsterdam": "AMS",
  "Frankfurt": "FRA",
  "Zurich": "ZRH",
  "Barcelona": "BCN",
  "Istanbul": "IST",

  // Oceania
  "Sydney": "SYD",
  "Melbourne": "MEL",

  // North America
  "New York": "JFK",
  "Los Angeles": "LAX",
  "San Francisco": "SFO",
  "Chicago": "ORD",
  "Toronto": "YYZ",
};

const DEPARTURE_CITIES = [
  "Delhi", "Mumbai", "Bengaluru", "Hyderabad", "Chennai",
  "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Kochi", "Goa",
  "Lucknow", "Chandigarh", "Thiruvananthapuram", "London", "New York"
];

const DESTINATION_CITIES = Object.keys(CITY_TO_AIRPORT);

// ---------------------------------------------------------------------
// Design tokens
// ---------------------------------------------------------------------
const C = {
  navy: "#0B1D2E",
  navyLight: "#152C42",
  paper: "#EFF3F6",
  paperCard: "#FFFFFF",
  ink: "#0F2233",
  inkSoft: "#4C6072",
  brass: "#B8862F",
  brassLight: "#D9A94B",
  brassBg: "#FBF3E7",
  brassBorder: "#EEDDBD",
  line: "#D7DEE4",
  green: "#2F7A4F",
  greenBg: "#E7F3EB",
  red: "#B23B3B",
  redBg: "#FAEAEA",
};

function FontImport() {
  return (
    <style>{`
      @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
      .voyage-root * { font-family: 'Inter', sans-serif; box-sizing: border-box; }
      .voyage-display { font-family: 'Fraunces', serif; }
      .voyage-mono { font-family: 'IBM Plex Mono', monospace; }
      .voyage-option-row:hover { border-color: ${C.brass} !important; }
      .voyage-select { -webkit-appearance: none; appearance: none; }
    `}</style>
  );
}

function airportCode(city) {
  return CITY_TO_AIRPORT[city] || (city || "???").replace(/[^a-zA-Z]/g, "").slice(0, 3).toUpperCase();
}

function formatCurrency(value, currency = "INR") {
  const symbol = currency === "INR" ? "₹" : currency === "USD" ? "$" : currency + " ";
  return symbol + Math.round(value).toLocaleString("en-IN");
}

function parseDuration(duration) {
  if (!duration) return "";
  const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?/);
  if (!match) return duration;
  const hours = match[1];
  const minutes = match[2];
  return [hours ? `${hours} hr` : "", minutes ? `${minutes} min` : ""].join(" ").trim();
}

// ---------------------------------------------------------------------
// Dropdown Form Input Screen
// ---------------------------------------------------------------------
function DropdownInput({ onSubmit }) {
  const [departureCity, setDepartureCity] = useState("Delhi");
  const [destinationCity, setDestinationCity] = useState("Tokyo");
  const [departureDate, setDepartureDate] = useState("2026-08-10");
  const [returnDate, setReturnDate] = useState("2026-08-18");
  const [travelers, setTravelers] = useState(1);
  const [budget, setBudget] = useState(500000);
  const [currency, setCurrency] = useState("INR");

  // Calculate days dynamically
  const days = useMemo(() => {
    if (!departureDate || !returnDate) return 0;
    const dep = new Date(departureDate);
    const ret = new Date(returnDate);
    const diffTime = ret - dep;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
  }, [departureDate, returnDate]);

  function handleFormSubmit(e) {
    e.preventDefault();
    if (days <= 0) {
      alert("Return date must be after departure date.");
      return;
    }

    // Format prompt text for backend NLP parsing
    const formattedPrompt = `Plan a ${days} day trip to ${destinationCity} from ${departureCity} for ${travelers} traveler${travelers > 1 ? "s" : ""} with a budget of ${budget} ${currency} from ${departureDate} to ${returnDate}.`;
    
    // Also send explicit structured payload alongside prompt
    const payload = {
      prompt: formattedPrompt,
      departure_city: departureCity,
      destination_city: destinationCity,
      departure_date: departureDate,
      return_date: returnDate,
      travelers: Number(travelers),
      budget: Number(budget),
      currency: currency,
      days: days
    };

    onSubmit(payload);
  }

  return (
    <div style={{ minHeight: "85vh", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", padding: "2rem 1.5rem" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}>
        <Plane size={22} color={C.brass} style={{ transform: "rotate(-45deg)" }} />
        <span className="voyage-mono" style={{ fontSize: 13, letterSpacing: "0.2em", color: C.brass, fontWeight: 600 }}>VOYAGE AI</span>
      </div>

      <h1 className="voyage-display" style={{ fontSize: "clamp(28px, 4.5vw, 48px)", fontWeight: 600, color: C.ink, textAlign: "center", maxWidth: 600, lineHeight: 1.15, marginBottom: 10 }}>
        Build your tailored trip
      </h1>
      <p style={{ color: C.inkSoft, fontSize: 15, textAlign: "center", maxWidth: 460, marginBottom: 32 }}>
        Select your travel details below — I'll find live flights, hotel options, and build a full custom itinerary.
      </p>

      <form
        onSubmit={handleFormSubmit}
        style={{
          width: "100%", maxWidth: 680, background: C.paperCard, border: `1px solid ${C.line}`,
          borderRadius: 20, padding: "28px 24px", boxShadow: "0 4px 20px rgba(11,29,46,0.06)",
          display: "flex", flexDirection: "column", gap: 20
        }}
      >
        {/* Origin & Destination */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 16 }}>
          <div>
            <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: C.inkSoft, marginBottom: 6 }}>DEPARTURE CITY</label>
            <div style={{ position: "relative" }}>
              <select
                className="voyage-select"
                value={departureCity}
                onChange={(e) => setDepartureCity(e.target.value)}
                style={{
                  width: "100%", background: C.paper, border: `1px solid ${C.line}`, borderRadius: 12,
                  padding: "12px 36px 12px 14px", fontSize: 14, color: C.ink, fontWeight: 500, cursor: "pointer"
                }}
              >
                {DEPARTURE_CITIES.map((city) => (
                  <option key={city} value={city}>{city} ({CITY_TO_AIRPORT[city] || "AIR"})</option>
                ))}
              </select>
              <ChevronDown size={16} color={C.inkSoft} style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", pointerEvents: "none" }} />
            </div>
          </div>

          <div>
            <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: C.inkSoft, marginBottom: 6 }}>DESTINATION CITY</label>
            <div style={{ position: "relative" }}>
              <select
                className="voyage-select"
                value={destinationCity}
                onChange={(e) => setDestinationCity(e.target.value)}
                style={{
                  width: "100%", background: C.paper, border: `1px solid ${C.line}`, borderRadius: 12,
                  padding: "12px 36px 12px 14px", fontSize: 14, color: C.ink, fontWeight: 500, cursor: "pointer"
                }}
              >
                {DESTINATION_CITIES.map((city) => (
                  <option key={city} value={city}>{city} ({CITY_TO_AIRPORT[city]})</option>
                ))}
              </select>
              <ChevronDown size={16} color={C.inkSoft} style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", pointerEvents: "none" }} />
            </div>
          </div>
        </div>

        {/* Dates & Travelers */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 16 }}>
          <div>
            <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: C.inkSoft, marginBottom: 6 }}>DEPARTURE DATE</label>
            <input
              type="date"
              value={departureDate}
              onChange={(e) => setDepartureDate(e.target.value)}
              style={{
                width: "100%", background: C.paper, border: `1px solid ${C.line}`, borderRadius: 12,
                padding: "11px 12px", fontSize: 13.5, color: C.ink, fontWeight: 500, outline: "none"
              }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: C.inkSoft, marginBottom: 6 }}>RETURN DATE</label>
            <input
              type="date"
              value={returnDate}
              onChange={(e) => setReturnDate(e.target.value)}
              style={{
                width: "100%", background: C.paper, border: `1px solid ${C.line}`, borderRadius: 12,
                padding: "11px 12px", fontSize: 13.5, color: C.ink, fontWeight: 500, outline: "none"
              }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: C.inkSoft, marginBottom: 6 }}>TRAVELERS</label>
            <div style={{ position: "relative" }}>
              <select
                className="voyage-select"
                value={travelers}
                onChange={(e) => setTravelers(e.target.value)}
                style={{
                  width: "100%", background: C.paper, border: `1px solid ${C.line}`, borderRadius: 12,
                  padding: "12px 36px 12px 14px", fontSize: 14, color: C.ink, fontWeight: 500, cursor: "pointer"
                }}
              >
                {[1, 2, 3, 4, 5, 6].map((num) => (
                  <option key={num} value={num}>{num} Traveler{num > 1 ? "s" : ""}</option>
                ))}
              </select>
              <ChevronDown size={16} color={C.inkSoft} style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", pointerEvents: "none" }} />
            </div>
          </div>
        </div>

        {/* Budget Input & Trip Summary Preview */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 120px", gap: 16 }}>
          <div>
            <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: C.inkSoft, marginBottom: 6 }}>TOTAL BUDGET</label>
            <input
              type="number"
              value={budget}
              step={10000}
              min={10000}
              onChange={(e) => setBudget(e.target.value)}
              style={{
                width: "100%", background: C.paper, border: `1px solid ${C.line}`, borderRadius: 12,
                padding: "12px 14px", fontSize: 14, color: C.ink, fontWeight: 600, outline: "none"
              }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: C.inkSoft, marginBottom: 6 }}>CURRENCY</label>
            <div style={{ position: "relative" }}>
              <select
                className="voyage-select"
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                style={{
                  width: "100%", background: C.paper, border: `1px solid ${C.line}`, borderRadius: 12,
                  padding: "12px 30px 12px 12px", fontSize: 14, color: C.ink, fontWeight: 600, cursor: "pointer"
                }}
              >
                <option value="INR">INR (₹)</option>
                <option value="USD">USD ($)</option>
              </select>
              <ChevronDown size={16} color={C.inkSoft} style={{ position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", pointerEvents: "none" }} />
            </div>
          </div>
        </div>

        {/* Calculation Summary Bar */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 16px", background: C.brassBg, border: `1px solid ${C.brassBorder}`, borderRadius: 12 }}>
          <span style={{ fontSize: 13, color: C.brass, fontWeight: 600 }}>
            Duration: {days} Days / {Math.max(days - 1, 0)} Nights
          </span>
          <span className="voyage-mono" style={{ fontSize: 13, color: C.brass, fontWeight: 600 }}>
            Estimated {formatCurrency(budget / (days || 1), currency)}/day
          </span>
        </div>

        <button
          type="submit"
          style={{
            marginTop: 6, width: "100%", background: C.navy, color: "#fff", border: "none",
            borderRadius: 12, padding: "14px 18px", display: "flex", alignItems: "center",
            justifyContent: "center", gap: 8, cursor: "pointer", fontSize: 15, fontWeight: 600,
            boxShadow: "0 4px 12px rgba(11,29,46,0.15)"
          }}
        >
          Generate Trip Itinerary <Send size={16} />
        </button>
      </form>
    </div>
  );
}

// ---------------------------------------------------------------------
// Loading screen
// ---------------------------------------------------------------------
function LoadingScreen() {
  return (
    <div style={{ minHeight: "70vh", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", gap: 22 }}>
      <div style={{ position: "relative", width: 200, height: 2 }}>
        <div style={{ position: "absolute", inset: 0, borderTop: `2px dashed ${C.line}` }} />
        <Plane
          size={20}
          color={C.brass}
          style={{ position: "absolute", top: -10, left: 0, transform: "rotate(90deg)", animation: "voyage-fly 1.8s ease-in-out infinite" }}
        />
      </div>
      <style>{`@keyframes voyage-fly { 0% { left: 0; } 50% { left: 180px; } 100% { left: 0; } }`}</style>
      <p className="voyage-mono" style={{ color: C.inkSoft, fontSize: 13, letterSpacing: "0.05em" }}>
        Fetching live flights, hotels, and generating itinerary...
      </p>
    </div>
  );
}

// ---------------------------------------------------------------------
// Error screen
// ---------------------------------------------------------------------
function ErrorScreen({ message, onRetry }) {
  return (
    <div style={{ minHeight: "60vh", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", gap: 14, padding: "2rem" }}>
      <p style={{ color: C.red, fontWeight: 600, fontSize: 16 }}>Trip planning failed</p>
      <p style={{ color: C.inkSoft, fontSize: 14, textAlign: "center", maxWidth: 420 }}>{message}</p>
      <button onClick={onRetry} style={{ display: "flex", alignItems: "center", gap: 6, background: C.navy, color: "#fff", border: "none", borderRadius: 10, padding: "10px 16px", fontSize: 14, cursor: "pointer" }}>
        <RotateCcw size={14} /> Try again
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------
// Boarding pass card
// ---------------------------------------------------------------------
function BoardingPass({ trip, flight, hotel }) {
  const origin = airportCode(trip.departure_city);
  const dest = airportCode(trip.destination);

  return (
    <div style={{ background: C.navy, borderRadius: 18, overflow: "hidden", display: "flex", flexWrap: "wrap", boxShadow: "0 8px 30px rgba(11,29,46,0.18)" }}>
      {/* Flight stub */}
      <div style={{ flex: "1 1 320px", padding: "26px 28px", position: "relative" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 18 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Plane size={16} color={C.brassLight} />
            <span className="voyage-mono" style={{ color: C.brassLight, fontSize: 11, letterSpacing: "0.15em" }}>BOARDING PASS</span>
          </div>
          {flight.isRecommended && (
            <span className="voyage-mono" style={{ fontSize: 9.5, color: C.navy, background: C.brassLight, padding: "3px 8px", borderRadius: 999, fontWeight: 700, letterSpacing: "0.05em" }}>
              AI PICK
            </span>
          )}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 18, marginBottom: 22 }}>
          <div>
            <div className="voyage-mono" style={{ fontSize: 30, fontWeight: 600, color: "#fff", letterSpacing: "0.03em" }}>{origin}</div>
            <div style={{ fontSize: 11.5, color: "rgba(255,255,255,0.55)" }}>{trip.departure_city}</div>
          </div>
          <div style={{ flex: 1, position: "relative", height: 1, borderTop: "1.5px dashed rgba(255,255,255,0.3)", margin: "0 4px" }}>
            <Plane size={13} color={C.brassLight} style={{ position: "absolute", right: -2, top: -7, transform: "rotate(90deg)" }} />
          </div>
          <div>
            <div className="voyage-mono" style={{ fontSize: 30, fontWeight: 600, color: "#fff", letterSpacing: "0.03em" }}>{dest}</div>
            <div style={{ fontSize: 11.5, color: "rgba(255,255,255,0.55)", textAlign: "right" }}>{trip.destination}</div>
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14, marginBottom: 14 }}>
          <Field label="AIRLINE" value={`${flight.airline}`} />
          <Field label="STOPS" value={flight.stops === 0 ? "Direct" : `${flight.stops} stop`} />
          <Field label="DURATION" value={flight.duration} />
          <Field label="DEPART" value={trip.departure_date} />
          <Field label="RETURN" value={trip.return_date} />
        </div>

        <div style={{ marginTop: 16, paddingTop: 14, borderTop: "1px solid rgba(255,255,255,0.12)" }}>
          <div className="voyage-mono" style={{ fontSize: 22, fontWeight: 600, color: C.brassLight }}>
            ₹{Math.round(flight.price_inr).toLocaleString("en-IN")}
          </div>
          <div style={{ fontSize: 12, color: "rgba(255,255,255,0.55)", marginTop: 6, lineHeight: 1.5 }}>{flight.note}</div>
        </div>
      </div>

      {/* Perforation */}
      <div style={{ width: 0, position: "relative", display: "flex", flexDirection: "column", justifyContent: "space-evenly", padding: "10px 0" }}>
        {Array.from({ length: 14 }).map((_, i) => (
          <div key={i} style={{ width: 8, height: 8, borderRadius: "50%", background: C.paper, marginLeft: -4 }} />
        ))}
      </div>

      {/* Hotel stub */}
      <div style={{ flex: "1 1 260px", padding: "26px 28px", background: C.navyLight }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 18 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Building2 size={16} color={C.brassLight} />
            <span className="voyage-mono" style={{ color: C.brassLight, fontSize: 11, letterSpacing: "0.15em" }}>STAY</span>
          </div>
          {hotel.isRecommended && (
            <span className="voyage-mono" style={{ fontSize: 9.5, color: C.navy, background: C.brassLight, padding: "3px 8px", borderRadius: 999, fontWeight: 700, letterSpacing: "0.05em" }}>
              AI PICK
            </span>
          )}
        </div>

        <div style={{ fontSize: 18, fontWeight: 600, color: "#fff", marginBottom: 6 }}>{hotel.name}</div>
        <div style={{ fontSize: 12.5, color: "rgba(255,255,255,0.6)", marginBottom: 18 }}>
          ⭐ {hotel.rating}{hotel.reviews ? ` · ${hotel.reviews.toLocaleString("en-IN")} reviews` : ""}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 14 }}>
          <Field label="PER NIGHT" value={hotel.nightly ? `₹${Math.round(hotel.nightly).toLocaleString("en-IN")}` : "—"} />
          <Field label="TOTAL" value={`₹${Math.round(hotel.cost).toLocaleString("en-IN")}`} />
        </div>

        <div style={{ fontSize: 12, color: "rgba(255,255,255,0.55)", lineHeight: 1.5 }}>{hotel.note}</div>
      </div>
    </div>
  );
}

function Field({ label, value }) {
  return (
    <div>
      <div className="voyage-mono" style={{ fontSize: 9.5, color: "rgba(255,255,255,0.4)", letterSpacing: "0.1em", marginBottom: 3 }}>{label}</div>
      <div style={{ fontSize: 13, color: "#fff", fontWeight: 500 }}>{value}</div>
    </div>
  );
}

// ---------------------------------------------------------------------
// Budget breakdown
// ---------------------------------------------------------------------
function BudgetSection({ flightCost, hotelCost, food, transport, misc, currency, totalBudget }) {
  const total = flightCost + hotelCost + food + transport + misc;
  const remaining = totalBudget - total;
  const pct = (v) => (total > 0 ? (v / total) * 100 : 0);

  const segments = [
    { key: "flights", label: "Flights", value: flightCost, color: C.navy },
    { key: "hotel", label: "Hotel", value: hotelCost, color: C.brass },
    { key: "food", label: "Food", value: food, color: "#6E8B7A" },
    { key: "transport", label: "Transport", value: transport, color: "#93A6B8" },
    { key: "miscellaneous", label: "Misc", value: misc, color: C.line },
  ];

  const affordable = remaining >= 0;

  return (
    <SectionCard icon={<Wallet size={16} color={C.brass} />} title="Budget breakdown">
      <div style={{ display: "flex", height: 14, borderRadius: 8, overflow: "hidden", marginBottom: 16 }}>
        {segments.map((s) => (
          <div key={s.key} style={{ width: `${pct(s.value)}%`, background: s.color, transition: "width 0.25s ease" }} title={`${s.label}: ${formatCurrency(s.value, currency)}`} />
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", gap: "10px 20px", marginBottom: 18 }}>
        {segments.map((s) => (
          <div key={s.key} style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 9, height: 9, borderRadius: 3, background: s.color, flexShrink: 0 }} />
            <div style={{ fontSize: 13, color: C.ink }}>{s.label}</div>
            <div className="voyage-mono" style={{ fontSize: 12.5, color: C.inkSoft, marginLeft: "auto" }}>
              {formatCurrency(s.value, currency)}
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "14px 16px", background: affordable ? C.greenBg : C.redBg, borderRadius: 10 }}>
        <span style={{ fontSize: 13.5, color: affordable ? C.green : C.red, fontWeight: 600 }}>
          {affordable ? "Remaining budget" : "Over budget by"}
        </span>
        <span className="voyage-mono" style={{ fontSize: 16, color: affordable ? C.green : C.red, fontWeight: 600 }}>
          {formatCurrency(Math.abs(remaining), currency)}
        </span>
      </div>
    </SectionCard>
  );
}

function PriceBar({ value, max }) {
  const pct = max > 0 ? Math.max(4, (value / max) * 100) : 0;
  return (
    <div style={{ width: "100%", height: 5, background: C.paper, borderRadius: 4, overflow: "hidden", marginTop: 8 }}>
      <div style={{ width: `${pct}%`, height: "100%", background: `linear-gradient(90deg, ${C.brassLight}, ${C.brass})`, borderRadius: 4 }} />
    </div>
  );
}

function OptionPicker({ icon, title, options, selectedId, onSelect, currency, renderMeta, renderPros }) {
  const [expanded, setExpanded] = useState(true);
  const [sortAsc, setSortAsc] = useState(true);

  const sorted = useMemo(() => {
    const arr = [...options];
    arr.sort((a, b) => (sortAsc ? a.price - b.price : b.price - a.price));
    return arr;
  }, [options, sortAsc]);

  const maxPrice = useMemo(() => Math.max(...options.map((o) => o.price)), [options]);
  const minPrice = useMemo(() => Math.min(...options.map((o) => o.price)), [options]);

  return (
    <SectionCard>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: expanded ? 16 : 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {icon}
          <span style={{ fontSize: 15, fontWeight: 600, color: C.ink }}>{title}</span>
          <span className="voyage-mono" style={{ fontSize: 11, color: C.inkSoft, background: C.paper, padding: "2px 8px", borderRadius: 999 }}>
            {options.length} options
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <button
            onClick={() => setSortAsc((s) => !s)}
            title="Sort by price"
            style={{ display: "flex", alignItems: "center", gap: 5, background: "none", border: `1px solid ${C.line}`, borderRadius: 8, padding: "5px 9px", fontSize: 11.5, color: C.inkSoft, cursor: "pointer" }}
          >
            <ArrowUpDown size={11} /> {sortAsc ? "Cheapest first" : "Priciest first"}
          </button>
          <button
            onClick={() => setExpanded((e) => !e)}
            style={{ background: "none", border: "none", cursor: "pointer", display: "flex", padding: 4 }}
          >
            {expanded ? <ChevronUp size={18} color={C.inkSoft} /> : <ChevronDown size={18} color={C.inkSoft} />}
          </button>
        </div>
      </div>

      <div style={{ position: "relative", marginBottom: expanded ? 18 : 0 }}>
        <select
          className="voyage-select"
          value={selectedId}
          onChange={(e) => onSelect(e.target.value)}
          style={{
            width: "100%", background: C.paper, border: `1px solid ${C.line}`, borderRadius: 10,
            padding: "12px 36px 12px 14px", fontSize: 13.5, color: C.ink, cursor: "pointer", fontWeight: 500,
          }}
        >
          {sorted.map((o) => (
            <option key={o.id} value={o.id}>
              {o.label} — {formatCurrency(o.price, currency)}{o.id === selectedId ? " (selected)" : ""}
            </option>
          ))}
        </select>
        <ChevronDown size={15} color={C.inkSoft} style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", pointerEvents: "none" }} />
      </div>

      {expanded && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {sorted.map((o) => {
            const isSelected = o.id === selectedId;
            const diffFromMax = maxPrice - o.price;
            const isPriciest = o.price === maxPrice;
            const isCheapest = o.price === minPrice && minPrice !== maxPrice;
            return (
              <div
                key={o.id}
                className="voyage-option-row"
                onClick={() => onSelect(o.id)}
                style={{
                  border: `1.5px solid ${isSelected ? C.brass : C.line}`,
                  background: isSelected ? C.brassBg : C.paperCard,
                  borderRadius: 12, padding: "14px 16px", cursor: "pointer", transition: "border-color 0.12s",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start" }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                      <span style={{ fontSize: 14, fontWeight: 600, color: C.ink }}>{o.label}</span>
                      {o.isRecommended && (
                        <span className="voyage-mono" style={{ fontSize: 9.5, color: "#fff", background: C.navy, padding: "2px 7px", borderRadius: 999, fontWeight: 700 }}>AI PICK</span>
                      )}
                      {isCheapest && (
                        <span className="voyage-mono" style={{ fontSize: 9.5, color: C.green, background: C.greenBg, padding: "2px 7px", borderRadius: 999, fontWeight: 700 }}>CHEAPEST</span>
                      )}
                      {isSelected && (
                        <span style={{ display: "flex", alignItems: "center", gap: 3, fontSize: 9.5, color: C.brass, fontWeight: 700 }}>
                          <Check size={11} /> SELECTED
                        </span>
                      )}
                    </div>
                    {renderMeta && <div style={{ fontSize: 12, color: C.inkSoft, marginTop: 4 }}>{renderMeta(o)}</div>}
                    {renderPros && (
                      <div style={{ marginTop: 6 }}>
                        <div style={{ fontSize: 12, color: C.green }}>+ {o.pros}</div>
                        {o.cons && <div style={{ fontSize: 12, color: "#A5847A", marginTop: 1 }}>− {o.cons}</div>}
                      </div>
                    )}
                  </div>

                  <div style={{ textAlign: "right", flexShrink: 0 }}>
                    <div className="voyage-mono" style={{ fontSize: 15, fontWeight: 600, color: C.ink }}>
                      {formatCurrency(o.price, currency)}
                    </div>
                    {isPriciest ? (
                      <div style={{ fontSize: 11, color: C.inkSoft, marginTop: 2 }}>priciest option</div>
                    ) : (
                      <div style={{ fontSize: 11, color: C.green, marginTop: 2 }}>
                        −{formatCurrency(diffFromMax, currency)} vs priciest
                      </div>
                    )}
                  </div>
                </div>
                <PriceBar value={o.price} max={maxPrice} />
              </div>
            );
          })}
        </div>
      )}
    </SectionCard>
  );
}

function DayRestaurantPicker({ day, currency }) {
  const options = useMemo(() => {
    const map = new Map();
    map.set(day.restaurant.name, { ...day.restaurant, isPrimary: true });
    (day.nearby_restaurants || []).forEach((r) => {
      if (!map.has(r.name)) map.set(r.name, { ...r, isPrimary: false });
    });
    return Array.from(map.values());
  }, [day]);

  const [selectedName, setSelectedName] = useState(day.restaurant.name);
  const current = options.find((o) => o.name === selectedName) || options[0];
  const saving = current.estimated_saving ?? 0;

  return (
    <div style={{ marginTop: 10, padding: "12px 14px", background: C.paper, borderRadius: 10 }}>
      <div style={{ display: "flex", alignItems: "flex-start", gap: 8 }}>
        <Utensils size={14} color={C.brass} style={{ marginTop: 2, flexShrink: 0 }} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 7, flexWrap: "wrap" }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: C.ink }}>{current.name}</span>
            <span style={{ fontSize: 12, color: C.inkSoft }}>· {current.cuisine} · {current.price_range}</span>
            {current.isPrimary && (
              <span className="voyage-mono" style={{ fontSize: 9, color: "#fff", background: C.navy, padding: "1.5px 6px", borderRadius: 999, fontWeight: 700 }}>AI PICK</span>
            )}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 4, flexWrap: "wrap" }}>
            {current.rating != null && (
              <span style={{ display: "flex", alignItems: "center", gap: 3, fontSize: 11.5, color: C.inkSoft }}>
                <Star size={11} fill={C.brass} color={C.brass} /> {current.rating}
              </span>
            )}
            {current.distance_km != null && (
              <span style={{ display: "flex", alignItems: "center", gap: 3, fontSize: 11.5, color: C.inkSoft }}>
                <MapPin size={11} /> {current.distance_km} km away
              </span>
            )}
          </div>
          <div style={{ fontSize: 12, color: C.inkSoft, marginTop: 4 }}>{current.reason}</div>
        </div>

        <div style={{ textAlign: "right", flexShrink: 0 }}>
          <div className="voyage-mono" style={{ fontSize: 13, fontWeight: 600, color: C.ink }}>
            {formatCurrency(current.average_cost_per_person, currency)}
          </div>
          <div style={{ fontSize: 10.5, color: C.inkSoft }}>per person</div>
          {saving !== 0 && (
            <div className="voyage-mono" style={{ fontSize: 10.5, marginTop: 3, color: saving > 0 ? C.green : C.red }}>
              {saving > 0 ? `saves ${formatCurrency(saving, currency)}` : `+${formatCurrency(Math.abs(saving), currency)}`}
            </div>
          )}
        </div>
      </div>

      {options.length > 1 && (
        <div style={{ marginTop: 10, position: "relative" }}>
          <select
            className="voyage-select"
            value={current.name}
            onChange={(e) => setSelectedName(e.target.value)}
            style={{ width: "100%", background: "#fff", border: `1px solid ${C.line}`, borderRadius: 8, padding: "8px 30px 8px 10px", fontSize: 12, color: C.inkSoft, cursor: "pointer" }}
          >
            {options.map((o) => (
              <option key={o.name} value={o.name}>
                {o.name}{o.isPrimary ? " (AI pick)" : ""} — {formatCurrency(o.average_cost_per_person, currency)}/person · {o.distance_km} km · ⭐ {o.rating}
              </option>
            ))}
          </select>
          <ChevronDown size={13} color={C.inkSoft} style={{ position: "absolute", right: 9, top: "50%", transform: "translateY(-50%)", pointerEvents: "none" }} />
        </div>
      )}
    </div>
  );
}

function DayTimeline({ days, currency }) {
  return (
    <SectionCard icon={<MapPin size={16} color={C.brass} />} title="Day-by-day itinerary">
      <div style={{ position: "relative", paddingLeft: 6 }}>
        <div style={{ position: "absolute", left: 15, top: 8, bottom: 8, width: 0, borderLeft: `1.5px dashed ${C.line}` }} />
        {days.map((day, i) => (
          <div key={day.day} style={{ display: "flex", gap: 18, marginBottom: i === days.length - 1 ? 0 : 26 }}>
            <div style={{ flexShrink: 0, width: 32, height: 32, borderRadius: "50%", background: C.navy, display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1 }}>
              <span className="voyage-mono" style={{ color: C.brassLight, fontSize: 12, fontWeight: 600 }}>{day.day}</span>
            </div>
            <div style={{ flex: 1, paddingTop: 4 }}>
              <DayRow label="Morning" text={day.morning} />
              <DayRow label="Afternoon" text={day.afternoon} />
              <DayRow label="Evening" text={day.evening} />

              <DayRestaurantPicker day={day} currency={currency} />

              {day.attractions?.length > 0 && (
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 10 }}>
                  {day.attractions.map((a, ai) => (
                    <span key={ai} style={{ fontSize: 11.5, color: C.brass, background: C.brassBg, padding: "4px 10px", borderRadius: 999, border: `1px solid ${C.brassBorder}` }}>
                      {a}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}

function DayRow({ label, text }) {
  return (
    <div style={{ display: "flex", gap: 10, marginBottom: 6 }}>
      <span className="voyage-mono" style={{ fontSize: 10.5, color: C.inkSoft, letterSpacing: "0.05em", width: 64, flexShrink: 0, paddingTop: 1 }}>{label.toUpperCase()}</span>
      <span style={{ fontSize: 13, color: C.ink, lineHeight: 1.5 }}>{text}</span>
    </div>
  );
}

function TipsSection({ savingTips, travelTips, currency }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20 }}>
      <SectionCard icon={<TrendingDown size={16} color={C.green} />} title="Money-saving tips">
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {savingTips.map((tip, i) => (
            <div key={i} style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start" }}>
              <span style={{ fontSize: 13, color: C.ink, lineHeight: 1.5 }}>{tip.tip}</span>
              <span className="voyage-mono" style={{ fontSize: 12.5, color: C.green, fontWeight: 600, flexShrink: 0, whiteSpace: "nowrap" }}>
                −{formatCurrency(tip.estimated_saving, currency)}
              </span>
            </div>
          ))}
        </div>
      </SectionCard>

      <SectionCard icon={<CheckCircle2 size={16} color={C.brass} />} title="Travel tips">
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {travelTips.map((tip, i) => (
            <div key={i} style={{ fontSize: 12.5, color: C.inkSoft, lineHeight: 1.5, display: "flex", gap: 8 }}>
              <span style={{ color: C.brass }}>·</span>
              <span>{tip}</span>
            </div>
          ))}
        </div>
      </SectionCard>
    </div>
  );
}

function ConfidenceRow({ confidence }) {
  const badgeColor = (level) => {
    const l = String(level).toLowerCase();
    if (l.startsWith("high")) return { bg: C.greenBg, fg: C.green };
    if (l.startsWith("low")) return { bg: C.redBg, fg: C.red };
    return { bg: C.brassBg, fg: C.brass };
  };
  const entries = [
    ["Flight", confidence.flight], ["Hotel", confidence.hotel], ["Food", confidence.food],
    ["Transport", confidence.transport], ["Misc", confidence.miscellaneous],
  ];
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center" }}>
      <span className="voyage-mono" style={{ fontSize: 11, color: C.inkSoft, letterSpacing: "0.05em", marginRight: 4 }}>DATA CONFIDENCE</span>
      {entries.map(([label, level]) => {
        const c = badgeColor(level);
        return (
          <span key={label} style={{ fontSize: 11.5, background: c.bg, color: c.fg, padding: "4px 10px", borderRadius: 999, fontWeight: 500 }}>
            {label}: {level}
          </span>
        );
      })}
    </div>
  );
}

function SectionCard({ icon, title, children }) {
  return (
    <div style={{ background: C.paperCard, border: `1px solid ${C.line}`, borderRadius: 16, padding: "22px 24px" }}>
      {title && (
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
          {icon}
          <span style={{ fontSize: 15, fontWeight: 600, color: C.ink }}>{title}</span>
        </div>
      )}
      {children}
    </div>
  );
}

// ---------------------------------------------------------------------
// Results view
// ---------------------------------------------------------------------
function ResultsView({ data, onReset }) {
  const { summary, trip_summary, selected_flight, selected_hotel, budget,
    flight_comparison, hotel_comparison, itinerary,
    money_saving_tips, travel_tips, confidence } = data;

  const flightOptions = useMemo(() => {
    const rec = {
      id: "flight-recommended",
      label: `${selected_flight.airline}${selected_flight.airline_code ? ` (${selected_flight.airline_code})` : ""}`,
      airline: selected_flight.airline,
      price: selected_flight.price_inr,
      duration: parseDuration(selected_flight.duration) || selected_flight.duration,
      stops: selected_flight.stops,
      pros: selected_flight.reason,
      cons: "",
      note: selected_flight.reason,
      isRecommended: true,
    };
    const others = (flight_comparison || []).map((f, i) => ({
      id: `flight-${i}`,
      label: f.airline,
      airline: f.airline,
      price: f.price,
      duration: parseDuration(f.duration) || f.duration,
      stops: f.stops,
      pros: f.pros,
      cons: f.cons,
      note: f.pros,
      isRecommended: false,
    }));
    return [rec, ...others];
  }, [selected_flight, flight_comparison]);

  const hotelOptions = useMemo(() => {
    const rec = {
      id: "hotel-recommended",
      label: selected_hotel.name,
      name: selected_hotel.name,
      price: selected_hotel.estimated_total_cost,
      nightly: selected_hotel.estimated_nightly_cost,
      rating: selected_hotel.rating,
      reviews: selected_hotel.reviews,
      pros: selected_hotel.reason,
      cons: "",
      note: selected_hotel.reason,
      isRecommended: true,
    };
    const others = (hotel_comparison || []).map((h, i) => ({
      id: `hotel-${i}`,
      label: h.name,
      name: h.name,
      price: h.estimated_cost,
      nightly: summary.days > 1 ? h.estimated_cost / (summary.days - 1) : h.estimated_cost,
      rating: h.rating,
      reviews: null,
      pros: h.pros,
      cons: h.cons,
      note: h.pros,
      isRecommended: false,
    }));
    return [rec, ...others];
  }, [selected_hotel, hotel_comparison, summary.days]);

  const [selectedFlightId, setSelectedFlightId] = useState("flight-recommended");
  const [selectedHotelId, setSelectedHotelId] = useState("hotel-recommended");

  const currentFlight = flightOptions.find((f) => f.id === selectedFlightId) || flightOptions[0];
  const currentHotel = hotelOptions.find((h) => h.id === selectedHotelId) || hotelOptions[0];

  const isCustomized = selectedFlightId !== "flight-recommended" || selectedHotelId !== "hotel-recommended";

  const boardingFlight = { ...currentFlight, price_inr: currentFlight.price };
  const boardingHotel = { ...currentHotel, cost: currentHotel.price };

  return (
    <div style={{ maxWidth: 860, margin: "0 auto", padding: "0 1.5rem 4rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "24px 0" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Plane size={16} color={C.brass} style={{ transform: "rotate(-45deg)" }} />
          <span className="voyage-mono" style={{ fontSize: 12, letterSpacing: "0.15em", color: C.brass, fontWeight: 600 }}>VOYAGE AI</span>
        </div>
        <button onClick={onReset} style={{ display: "flex", alignItems: "center", gap: 6, background: "none", border: `1px solid ${C.line}`, borderRadius: 999, padding: "7px 14px", fontSize: 12.5, color: C.inkSoft, cursor: "pointer" }}>
          <RotateCcw size={12} /> Plan another trip
        </button>
      </div>

      <div style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6, flexWrap: "wrap" }}>
          <h1 className="voyage-display" style={{ fontSize: 32, fontWeight: 600, color: C.ink, margin: 0 }}>{summary.destination}</h1>
          {isCustomized && (
            <span style={{ fontSize: 12, background: C.brassBg, color: C.brass, padding: "5px 12px", borderRadius: 999, fontWeight: 600, border: `1px solid ${C.brassBorder}` }}>
              Customized
            </span>
          )}
        </div>
        <p style={{ color: C.inkSoft, fontSize: 14 }}>
          {summary.departure_date} <ArrowRight size={12} style={{ display: "inline", verticalAlign: "middle", margin: "0 4px" }} /> {summary.return_date}
          {"  ·  "}{summary.days} days · {summary.travelers} traveler{summary.travelers !== 1 ? "s" : ""}
        </p>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        <BoardingPass trip={trip_summary} flight={boardingFlight} hotel={boardingHotel} />

        <BudgetSection
          flightCost={currentFlight.price}
          hotelCost={currentHotel.price}
          food={budget.food}
          transport={budget.transport}
          misc={budget.miscellaneous}
          currency={trip_summary.currency}
          totalBudget={summary.total_budget}
        />

        <OptionPicker
          icon={<Plane size={16} color={C.brass} />}
          title="Choose your flight"
          options={flightOptions}
          selectedId={selectedFlightId}
          onSelect={setSelectedFlightId}
          currency={trip_summary.currency}
          renderMeta={(o) => `${o.duration} · ${o.stops === 0 ? "Direct" : `${o.stops} stop${o.stops > 1 ? "s" : ""}`}`}
          renderPros
        />

        <OptionPicker
          icon={<Building2 size={16} color={C.brass} />}
          title="Choose your hotel"
          options={hotelOptions}
          selectedId={selectedHotelId}
          onSelect={setSelectedHotelId}
          currency={trip_summary.currency}
          renderMeta={(o) => (
            <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <Star size={11} fill={C.brass} color={C.brass} /> {o.rating} rating
            </span>
          )}
          renderPros
        />

        <DayTimeline days={itinerary} currency={trip_summary.currency} />

        <TipsSection savingTips={money_saving_tips} travelTips={travel_tips} currency={trip_summary.currency} />

        <SectionCard>
          <ConfidenceRow confidence={confidence} />
        </SectionCard>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------
// Root app
// ---------------------------------------------------------------------
export default function VoyageApp() {
  const [mode, setMode] = useState("input"); // input | loading | results | error
  const [data, setData] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");

  async function handleSubmit(payload) {
    setMode("loading");
    setErrorMsg("");

    try {
      const res = await fetch(`${API_BASE_URL}/plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`Server responded with ${res.status}`);
      const json = await res.json();
      if (!json.success) throw new Error(json.message || "Trip generation failed");
      setData(json.data);
      setMode("results");
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message);
      setMode("error");
    }
  }

  function handleReset() {
    setMode("input");
    setData(null);
  }

  return (
    <div className="voyage-root" style={{ background: C.paper, minHeight: "100vh" }}>
      <FontImport />
      {mode === "input" && <DropdownInput onSubmit={handleSubmit} />}
      {mode === "loading" && <LoadingScreen />}
      {mode === "error" && <ErrorScreen message={errorMsg} onRetry={() => setMode("input")} />}
      {mode === "results" && data && <ResultsView data={data} onReset={handleReset} />}
    </div>
  );
}