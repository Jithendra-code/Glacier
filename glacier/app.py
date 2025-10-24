from flask import Flask, render_template, request
import folium
import requests
import os

app = Flask(__name__)

# Sample glacier info
glacier_info = {
    "Gangotri Glacier": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/4/4b/Gangotri_Glacier_terminus_detail_in_2018_satellite_image%2C_India_ESA415382_%28cropped%29.jpg",
        "description": "Gangotri Glacier is one of the primary sources of the Ganges River, located in Uttarakhand, India.",
        "country": "India",
        "length_km": 30,
        "area_km2": 200,
        "elevation_m": "3,415–7,756",
        "fact": "It is receding at a rate of about 22 meters per year due to climate change."
    },
    "Siachen Glacier": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/4/4e/SiachenGlacier_satellite.jpg",
        "description": "Siachen Glacier is the longest glacier in the Karakoram and second-longest outside polar regions.",
        "country": "India/Pakistan",
        "length_km": 76,
        "area_km2": 700,
        "elevation_m": "3,620–6,700",
        "fact": "It is known as the highest battlefield in the world due to military presence."
    },
    "Yamunotri Glacier": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/1/10/Yamunotri_temple.jpg",
        "description": "Yamunotri Glacier is the source of the Yamuna River, Uttarkashi district, India.",
        "country": "India",
        "length_km": 10,
        "area_km2": 20,
        "elevation_m": "3,293–6,387",
        "fact": "The glacier feeds the sacred Yamuna River and is visited by thousands of pilgrims annually."
    }
}

# 🎥 Add video links for each glacier
glacier_videos = {
    "Gangotri Glacier": "https://www.youtube.com/embed/bUIcOywV6bE",
    "Siachen Glacier": "https://www.youtube.com/embed/lhB6t9kQ39Y",
    "Yamunotri Glacier": "https://www.youtube.com/embed/TX6hhiOjhRA"
}


# Geocoding using OpenStreetMap
def geocode_location_free(location_name):
    url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json"
    response = requests.get(url, headers={"User-Agent": "GlacierApp/1.0"})
    data = response.json()
    if data:
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return lat, lon
    return None, None


@app.route("/", methods=["GET", "POST"])
def index():
    map_file = None
    images = {}
    markers = []

    if request.method == "POST":
        glacier_names = request.form.get("glacier_names")
        glacier_list = [g.strip() for g in glacier_names.split(",")]

        map_glaciers = folium.Map(location=[30, 78], zoom_start=5, tiles='Esri.WorldImagery')
        marker_coords = []

        for g in glacier_list:
            lat, lon = geocode_location_free(g + " India")
            if lat and lon:
                popup_html = f'<a href="/glacier/{g}?lat={lat}&lon={lon}" target="_blank">{g}</a>'
                folium.Marker([lat, lon], popup=popup_html).add_to(map_glaciers)
                marker_coords.append([lat, lon])
                if g in glacier_info:
                    images[g] = glacier_info[g]["image"]

        if marker_coords:
            map_glaciers.fit_bounds(marker_coords)

        os.makedirs("static", exist_ok=True)
        map_file = "static/map.html"
        map_glaciers.save(map_file)

    return render_template("index.html", map_file=map_file, images=images)


@app.route("/glacier/<name>")
def glacier_detail(name):
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    info = glacier_info.get(name, {"image": None, "description": "No information available."})
    video = glacier_videos.get(name, "")
    return render_template("glacier_detail.html", name=name, lat=lat, lon=lon, info=info, video=video)


if __name__ == "__main__":
    os.makedirs("templates", exist_ok=True)
    app.run(debug=True)
