""" Diarium2HTML
    This script converts Diarium JSON export files into HTML pages
    Place the .py and a.css in the uncompressed folder and execute the script
    It can handle multiple JSON files at once
    See the Readme.md for more information and samples

    Version:    0.0.1
    Date:       3-9-2025
    Author:     HM
    """

import os
import json
import requests
from datetime import datetime
import locale

# Set locale for month names
try:
    locale.setlocale(locale.LC_TIME, 'nl_NL.UTF-8')
except:
    print("Locale not available.")

# Reverse geocode coordinates to location name
def get_location_name(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "zoom": 10,
        "addressdetails": 1
    }
    headers = {"User-Agent": "DiariumConverter/1.0"}
    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        return data.get("display_name", "")
    except Exception as e:
        print(f"Error fetching location: {e}")
        return ""

# Find first .css file in current folder
css_files = [f for f in os.listdir(os.getcwd()) if f.endswith(".css")]
css_filename = css_files[0] if css_files else None
css_link = f'<link rel="stylesheet" href="{css_filename}">' if css_filename else ""

# Scan current folder for JSON files
json_files = [f for f in os.listdir(os.getcwd()) if f.endswith(".json")]

if not json_files:
    print("No JSON-files found.")
    exit()

for filename in json_files:
    print(f"Input file:  {filename}")
    file_path = os.path.join(os.getcwd(), filename)
    with open(file_path, "r", encoding="utf-8") as f:
        entries = json.load(f)

    entries.sort(key=lambda e: datetime.fromisoformat(e["date"]))

    html_content = f"""
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <title>Diarium Reisdagboek</title>
    {css_link}
</head>
<body>
    <h1>📔 Diarium Reisdagboek</h1>
"""

    for entry in entries:
        print(".",end="")
        date_obj = datetime.fromisoformat(entry["date"])
        date_str = date_obj.strftime("%d %B %Y %H:%M")
        folder_name = date_obj.strftime("%Y-%m-%d_%H%M%S000")
        heading = entry.get("heading", "")
        html = entry.get("html", "")

        # Tags
        tags_list = entry.get("tags", [])
        tags_html = f'<div class="tags">🏷️ Tags: {", ".join(tags_list)}</div>' if tags_list else ""

        # Location
        location_coords = entry.get("location", [])
        location_html = ""
        if len(location_coords) == 2:
            lat, lon = location_coords
            location_name = ""
            # Comment out the next line to exclude location names.
            location_name = get_location_name(lat, lon)
            map_url = f"https://www.google.com/maps?q={lat},{lon}"
            if location_name:
                location_html = f'<div class="location">📍 <a href="{map_url}" target="_blank">{location_name}</a></div>'

        # Weather
        weather = entry.get("weather", "")
        weather_html = ""
        if isinstance(weather, str) and weather.strip():
            weather_html = f'<div class="weather">🌡️ Weer: {weather}</div>'

        # Rating
        rating = entry.get("rating")
        rating_html = ""
        if isinstance(rating, int) and 1 <= rating <= 5:
            stars = "★" * rating + "☆" * (5 - rating)
            rating_html = f'<span class="rating">{stars}</span>'

        # Photos
        photo_dir = os.path.join("media", folder_name)
        photo_html = ""
        if os.path.isdir(photo_dir):
            images = [img for img in os.listdir(photo_dir) if img.lower().endswith(".jpg")]
            if images:
                photo_html += '<div class="photos">'
                for img in images:
                    img_path = os.path.join(photo_dir, img).replace("\\", "/")
                    photo_html += f'<img src="{img_path}" alt="Foto">'
                photo_html += '</div>'

        html_content += f"""
        <div class="entry">
            <div class="date">🗓️ {date_str}</div>
            <div class="heading">
                <span class="title">{heading}</span>
                {rating_html}
            </div>
            {tags_html}
            {location_html}
            {weather_html}
            <div class="content">{html}</div>
            {photo_html}
        </div>
        """

    html_content += "</body></html>"

    html_filename = filename.replace(".json", ".html")
    with open(html_filename, "w", encoding="utf-8") as f_out:
        f_out.write(html_content)

    print(f"\r\nOutput file: {html_filename}\r\n")