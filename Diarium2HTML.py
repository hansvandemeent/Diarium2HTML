import os
import json
import requests
from datetime import datetime
import locale

# Set Dutch locale for month names
try:
    locale.setlocale(locale.LC_TIME, 'nl_NL.UTF-8')
except:
    print("⚠️ Nederlandse locale niet beschikbaar. Maandnamen blijven Engels.")

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
        print(f"⚠️ Error fetching location: {e}")
        return ""

# Scan current folder for JSON files
json_folder = os.getcwd()
json_files = [f for f in os.listdir(json_folder) if f.endswith(".json")]

if not json_files:
    print("Geen JSON-bestanden gevonden.")
    exit()

for filename in json_files:
    file_path = os.path.join(json_folder, filename)
    with open(file_path, "r", encoding="utf-8") as f:
        entries = json.load(f)

    entries.sort(key=lambda e: datetime.fromisoformat(e["date"]))
    print(f"Processing: {filename}")

    html_content = """
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <title>Diarium Reisdagboek</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Open Sans', sans-serif;
            background: linear-gradient(to bottom, #fdfcfb, #e2e2e2);
            margin: 0;
            padding: 40px;
            line-height: 1.6;
            color: #333;
        }
        h1 {
            font-family: 'Playfair Display', serif;
            font-size: 2.8em;
            margin-bottom: 40px;
            color: #2c2c2c;
            text-align: center;
        }
        .entry {
            background-color: #fff;
            border-radius: 10px;
            padding: 30px;
            margin: 0 auto 50px auto;
            max-width: 700px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.06);
        }
        .date {
            font-size: 0.95em;
            color: #777;
            margin-bottom: 5px;
        }
        .heading {
            font-family: 'Playfair Display', serif;
            font-size: 1.8em;
            margin-bottom: 15px;
            color: #1a1a1a;
        }
        .tags {
            font-size: 0.85em;
            color: #555;
            margin-bottom: 15px;
            font-style: italic;
        }
        .location {
            font-size: 0.9em;
            color: #444;
            margin-bottom: 10px;
        }
        .location a {
            color: #0077cc;
            text-decoration: none;
        }
        .location a:hover {
            text-decoration: underline;
        }
        .content {
            font-size: 1em;
            margin-bottom: 20px;
        }
        .photos {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 20px;
        }
        .photos img {
            max-width: 300px;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            object-fit: contain;
        }
    </style>
</head>
<body>
    <h1>📔 Diarium Reisdagboek</h1>
"""

    for entry in entries:
        date_obj = datetime.fromisoformat(entry["date"])
        date_str = date_obj.strftime("%d %B %Y %H:%M")
        folder_name = date_obj.strftime("%Y-%m-%d_%H%M%S000")
        heading = entry.get("heading", "")
        tags_list = entry.get("tags", [])
        tags_html = f'<div class="tags">🏷️ Tags: {", ".join(tags_list)}</div>' if tags_list else ""
        html = entry.get("html", "")
        location_coords = entry.get("location", [])
        location_html = ""

        if len(location_coords) == 2:
            lat, lon = location_coords
            location_name = ''
            #location_name = get_location_name(lat, lon)
            map_url = f"https://www.google.com/maps?q={lat},{lon}"
            if location_name:
                location_html = f'<div class="location">📍 <a href="{map_url}" target="_blank">{location_name}</a></div>'

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
            <div class="heading">{heading}</div>
            {tags_html}
            {location_html}
            <div class="content">{html}</div>
            {photo_html}
        </div>
        """

    html_content += "</body></html>"

    html_filename = filename.replace(".json", ".html")
    with open(html_filename, "w", encoding="utf-8") as f_out:
        f_out.write(html_content)

    print(f"HTML out:   {html_filename}")