import os
from sentinelhub import SHConfig, BBox, CRS, SentinelHubRequest, MimeType, DataCollection
from PIL import Image
import requests

# -----------------------------
# 1️⃣ Add your Sentinel Hub OAuth credentials here
# -----------------------------
os.environ['SH_CLIENT_ID'] = '086897f7-a31f-4da0-bb7b-d2ea5b5da1e4'
os.environ['SH_CLIENT_SECRET'] = '4ruBy5HUKNTGq6DwuUfeiT6hL1fB5aVT'

# -----------------------------
# 2️⃣ Setup Sentinel Hub config
# -----------------------------
config = SHConfig()
config.sh_client_id = os.environ.get('SH_CLIENT_ID')
config.sh_client_secret = os.environ.get('SH_CLIENT_SECRET')

# -----------------------------
# 3️⃣ Function to fetch Sentinel-2 image
# -----------------------------
def fetch_sentinel_image(lat, lon, size=500):
    try:
        bbox = BBox(bbox=[lon - 0.01, lat - 0.01, lon + 0.01, lat + 0.01], crs=CRS.WGS84)

        request = SentinelHubRequest(
            data_folder='satellite_images',
            evalscript="""
            //VERSION=3
            function setup() {
                return {
                    input: ["B04", "B03", "B02"],
                    output: { bands: 3 }
                };
            }
            function evaluatePixel(sample) {
                return [sample.B04, sample.B03, sample.B02];
            }
            """,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A,
                    time_interval=('2023-01-01', '2023-12-31')
                )
            ],
            responses=[
                SentinelHubRequest.output_response('default', MimeType.PNG)
            ],
            bbox=bbox,
            size=(size, size),
            config=config
        )

        image = request.get_data()[0]
        img = Image.fromarray(image)
        os.makedirs('satellite_images', exist_ok=True)
        path = f'satellite_images/sentinel_image_{lat}_{lon}.png'
        img.save(path)
        return path

    except Exception as e:
        print("Error fetching Sentinel image:", e)
        # Fallback image if something fails
        fallback_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Glacier_example.jpg/500px-Glacier_example.jpg"
        os.makedirs('satellite_images', exist_ok=True)
        fallback_path = "satellite_images/fallback_image.png"
        if not os.path.exists(fallback_path):
            img = Image.open(requests.get(fallback_url, stream=True).raw)
            img.save(fallback_path)
        return fallback_path
