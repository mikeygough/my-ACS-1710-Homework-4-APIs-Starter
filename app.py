import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim


################################################################################
## SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()

pp = PrettyPrinter(indent=4)

API_KEY = os.getenv("API_KEY")
API_URL = "http://api.openweathermap.org/data/2.5/weather"


################################################################################
## ROUTES
################################################################################


@app.route("/")
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        "min_date": (datetime.now() - timedelta(days=5)),
        "max_date": datetime.now(),
    }
    return render_template("home.html", **context)


def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return "F" if units == "imperial" else "C" if units == "metric" else "K"


def get_weather(city, units):
    """Returns json data for the current weather of a given city in the specified units."""
    params = {"appid": API_KEY, "q": city, "units": units}
    result_json = requests.get(API_URL, params=params).json()

    return result_json


def format_weather_response(json_to_format, units):
    """Selects specific keys values from input and returns dictionary of data. Should be called on return object from get_weather()"""
    results = {
        "date": datetime.now(),
        "city": json_to_format["name"],
        "description": json_to_format["weather"][0]["description"],
        "temp": json_to_format["main"]["temp"],
        "humidity": json_to_format["main"]["humidity"],
        "wind_speed": json_to_format["wind"]["speed"],
        "sunrise": datetime.fromtimestamp(json_to_format["sys"]["sunrise"]),
        "sunset": datetime.fromtimestamp(json_to_format["sys"]["sunset"]),
        "units_letter": get_letter_for_units(units),
    }

    return results


@app.route("/results")
def results():
    """Displays results for current weather conditions."""

    city = request.args.get("city")
    units = request.args.get("units")

    params = {"appid": API_KEY, "q": city, "units": units}

    result_json = requests.get(API_URL, params=params).json()

    # Uncomment the line below to see the results of the API call!
    # pp.pprint(result_json)

    context = {
        "date": datetime.now(),
        "city": result_json["name"],
        "description": result_json["weather"][0]["description"],
        "temp": result_json["main"]["temp"],
        "humidity": result_json["main"]["humidity"],
        "wind_speed": result_json["wind"]["speed"],
        "sunrise": datetime.fromtimestamp(result_json["sys"]["sunrise"]),
        "sunset": datetime.fromtimestamp(result_json["sys"]["sunset"]),
        "units_letter": get_letter_for_units(units),
    }

    return render_template("results.html", **context)


@app.route("/comparison_results")
def comparison_results():
    """Displays the relative weather for 2 different cities."""

    city1 = request.args.get("city1")
    city2 = request.args.get("city2")
    units = request.args.get("units")

    city_1_info = format_weather_response(get_weather(city1, units), units)
    city_2_info = format_weather_response(get_weather(city2, units), units)

    context = {
        "date": datetime.now(),
        "city_1_info": city_1_info,
        "city_2_info": city_2_info,
    }
    
    print(city_1_info)
    print(city_2_info)

    return render_template("comparison_results.html", **context)


if __name__ == "__main__":
    app.config["ENV"] = "development"
    app.run(debug=True)
