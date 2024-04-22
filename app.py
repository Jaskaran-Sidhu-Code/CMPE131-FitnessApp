#gym finder
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Google API Keys
PLACES_API_KEY = 'AIzaSyBPMpgZnvRwyiD47P-togXkkGLLAbJ64Jo'
GEOCODING_API_KEY = 'AIzaSyBPMpgZnvRwyiD47P-togXkkGLLAbJ64Jo'

def geocode_address(address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': address,
        'key': GEOCODING_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        latitude = location['lat']
        longitude = location['lng']
        return latitude, longitude
    else:
        return None

def get_nearby_gyms(city):
    coordinates = geocode_address(city)
    if coordinates:
        lat, lng = coordinates
        url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
        params = {
            'location': f"{lat},{lng}",
            'radius': 5000,  # Search radius in meters
            'type': 'gym',
            'key': PLACES_API_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()
        nearby_gyms = [place['name'] for place in data.get('results', [])]
        return nearby_gyms
    else:
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find_gyms', methods=['POST'])
def find_gyms():
    city = request.form['city']
    nearby_gyms = get_nearby_gyms(city)
    return render_template('gyms.html', city=city, gyms=nearby_gyms)

if __name__ == '__main__':
    app.run(debug=True)
