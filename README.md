# RouteRank

RouteRank helps you decide the best way to get from A to B based on what actually matters to *you* — not just the fastest route, but a weighted balance of cost and time.

## How it works

1. Enter a starting point and destination.
2. RouteRank fetches real route data (distance + time) for driving, cycling, and walking using the OpenRouteService API.
3. Since live pricing data isn't freely available, cost is estimated using a simple per-km fuel formula for driving (cycling/walking are free).
4. You set a priority slider (cost vs. time), and RouteRank normalizes all values onto a 0–1 scale and calculates a weighted score for each option — then ranks them from best to worst.

## Tech stack

- **Python** + **Streamlit** for the UI
- **OpenRouteService API** for geocoding and route data
- Custom weighted multi-criteria scoring algorithm (min-max normalization)

## Running it locally

1. Clone this repo
2. Create a virtual environment and install dependencies:
3. Get a free API key from [openrouteservice.org](https://openrouteservice.org) and add it to `.streamlit/secrets.toml`:
4. Run the app:


## What I'd add next

- Save trip history so returning users don't re-enter the same commute
- Support for multiple stops in one trip
- Real transit data, if a suitable free/paid API becomes available