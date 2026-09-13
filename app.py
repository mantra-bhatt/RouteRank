import streamlit as st
import requests

ORS_API_KEY = st.secrets["ORS_API_KEY"]

def get_route(start_coords,end_coords,profile = "driving-car"):
    #this is used to get the distance and time between two coords
    url = f"https://api.openrouteservice.org/v2/directions/{profile}"
    
    params = {
        "api_key": ORS_API_KEY,
        "start": f"{start_coords[0]},{start_coords[1]}",
        "end": f"{end_coords[0]},{end_coords[1]}"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.exceptions.RequestException:
        return None, None

    if response.status_code == 200:
        data = response.json()
        summary = data["features"][0]["properties"]["summary"]
        distance = summary["distance"]
        duration = summary["duration"]

        return distance,duration
    
    else:
        return None,None

def geocode(place_name):
    # this is used to convert a place's namae to its coordinates
    url = "https://api.openrouteservice.org/geocode/search"
    params = {
        "api_key": ORS_API_KEY,
        "text": place_name
    }
    try:
        response = requests.get(url,params = params,timeout = 10)
    except requests.exceptions.RequestException:
        return None

    if response.status_code == 200:
        data = response.json()
        features  = data.get("features")
        if not features:
            return None
        coords = data["features"][0]["geometry"]["coordinates"]
        return coords
    else:
        return None
    

def estimate_cost(mode,distance_meters):
    km = distance_meters / 1000
    if mode == "driving-car":
        fuel_cost_per_km = 8
        return km * fuel_cost_per_km
    else:
        return 0
    
def score_routes(results, cost_weight_frac, time_weight_frac):
    times = [r["duration"] for r in results]
    costs = [r["cost"] for r in results]

    min_time, max_time = min(times), max(times)
    min_cost, max_cost = min(costs), max(costs)

    for r in results:
        if max_time == min_time:
            time_score = 1
        else:
            time_score = (max_time - r["duration"]) / (max_time - min_time)

        if max_cost == min_cost:
            cost_score = 1
        else:
            cost_score = (max_cost - r["cost"]) / (max_cost - min_cost)

        r["score"] = (cost_weight_frac * cost_score) + (time_weight_frac * time_score)

    return sorted(results, key=lambda r: r["score"], reverse=True)
st.title("RouteRank")

# Sidebar for priorities
st.sidebar.header("Your priorities")
cost_weight = st.sidebar.slider("How much do you care about cost?", 0, 100, 50)
time_weight = 100 - cost_weight
st.sidebar.write(f"Cost: {cost_weight}% | Time: {time_weight}%")

st.subheader("Enter your trip")
origin = st.text_input("Starting point")
destination = st.text_input("Destination")

mode_icons = {
    "driving-car": "🚗",
    "cycling-regular": "🚲",
    "foot-walking": "🚶"
}

if st.button("Find routes"):
    if not origin.strip() or not destination.strip():
        st.write("Please enter both a starting point and a destination.")
    else:
        cost_weight_frac = cost_weight / 100
        time_weight_frac = time_weight / 100

        with st.spinner("Finding your best route..."):
            start_coords = geocode(origin)
            end_coords = geocode(destination)

            if start_coords and end_coords:
                modes = ["driving-car", "cycling-regular", "foot-walking"]
                results = []

                for mode in modes:
                    distance, duration = get_route(start_coords, end_coords, profile=mode)
                    if distance is not None:
                        cost = estimate_cost(mode, distance)
                        results.append({
                            "mode": mode,
                            "distance": distance,
                            "duration": duration,
                            "cost": cost
                        })

        if not start_coords or not end_coords:
            st.write("Couldn't find one of those locations. Try being more specific.")
        elif not results:
            st.write("Couldn't fetch any routes right now. The routing service may be temporarily unavailable — try again shortly.")
        else:
            ranked = score_routes(results, cost_weight_frac, time_weight_frac)

            st.subheader("Ranked results")
            cols = st.columns(len(ranked))

            for i, (col, r) in enumerate(zip(cols, ranked), start=1):
                km = r["distance"] / 1000
                minutes = r["duration"] / 60
                icon = mode_icons.get(r["mode"], "")

                with col:
                    with st.container(border=True):
                        if i == 1:
                            st.markdown("🏆 **BEST PICK**")
                        st.metric(label=f"{icon} {r['mode']}", value=f"{minutes:.0f} min", delta=f"₹{r['cost']:.0f}")
                        st.caption(f"{km:.1f} km · score: {r['score']:.2f}")