# LAB EXERCISE 05
import requests
from bs4 import BeautifulSoup

### SET UP BEGINS Do not modify
punctuations = ["", "-", ":"]
city_locations = [
{"name": "Boston", "latitude": 42.36, "longitude": -71.06},
{"name": "New York", "latitude": 40.71, "longitude": -74.01},
{"name": "Fake City", "latitude": 999, "longitude": -999}
]
### SET UP ENDS Do not modify
# PROBLEM 01

def scrape_quotes_by_author(num_pages):/;
    """Takes number of pages to scrape
    and scrapes quotes from url"""
    result = {}
    for page in range(1, num_pages + 1):
        url = f"http://quotes.toscrape.com/page/{page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        quotes = soup.find_all("div", class_="quote")
        if not quotes:
            break

        for quote in quotes:
            text = quote.find("span", class_="text").text.strip()
            author = quote.find("small", class_="author").text.strip()

            if author not in result:
                result[author] = []

            result[author].append(text)
    return result

# PROBLEM 02


def scrape_study_abroad_countries():
    """Scrapes course catalog and returns unique countries that are international study"""
    url = "https://catalog.northeastern.edu/course-descriptions/abrd/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    course_titles = soup.find_all("p", class_="courseblocktitle")
    countries = []

    for title in course_titles:
        text = title.get_text().strip()
        if "International Study" not in text:
            continue
        country = text.split("International Study")[1].strip()

        for p in punctuations:
            country = country.replace(p, "").strip()
    
        if "(" in country:
            country = country.split("(")[0].strip()

        country = country.replace("—", "").replace("\xa0","").replace(".","").strip()
    
        if country and country not in countries:
            countries.append(country)

    return countries

# PROBLEM 03
def get_weather_summary(cities):
    """Retrieves current weather info for multiple cities"""
    result = {}
    
    for city in cities:
        name = city["name"]
        lat = city["latitude"]
        lon = city["longitude"]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=True"

        try:
            response = requests.get(url)
            data = response.json()
            weather = data["current_weather"]
            result[name] = {
                "temperature": float(weather["temperature"]),
                "windspeed": float(weather["windspeed"]),
                "weathercode": int(weather["weathercode"])
            }

        except Exception:
            result[name] = {"temperature": "NA",
                            "windspeed": "NA",
                            "weathercode": "NA"}
    return result

def main():

    # problem 1
    quotes = scrape_quotes_by_author(2)
    print(quotes)

    # problem 2
    countries = scrape_study_abroad_countries()
    print(countries)

    # problem 3
    city_locations = [
        {"name": "Boston", "latitude": 42.36, "longitude": -71.06},
        {"name": "New York", "latitude": 40.71, "longitude": -74.01}
    ]

    weather = get_weather_summary(city_locations)
    print(weather)

if __name__ == '__main__':
    main()