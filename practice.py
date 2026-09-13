import requests

# Mumbai's coordinates as an example
latitude = 19.0760
longitude = 72.8777

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": latitude,
    "longitude": longitude,
    "current": "temperature_2m,wind_speed_10m"
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    temp = data["current"]["temperature_2m"]
    print(f"The current temperature is {temp}°C")
else:
    print(f"Something went wrong: {response.status_code}")