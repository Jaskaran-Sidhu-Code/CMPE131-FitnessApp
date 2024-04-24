#gym finder
#PLACES_API_KEY = 'AIzaSyBPMpgZnvRwyiD47P-togXkkGLLAbJ64Jo'
#GEOCODING_API_KEY = 'AIzaSyBPMpgZnvRwyiD47P-togXkkGLLAbJ64Jo'
import sqlite3
from flask import Flask, render_template, request, g
import requests

app = Flask(__name__)

# Google API Keys
PLACES_API_KEY = 'AIzaSyBPMpgZnvRwyiD47P-togXkkGLLAbJ64Jo'
GEOCODING_API_KEY = 'AIzaSyBPMpgZnvRwyiD47P-togXkkGLLAbJ64Jo'

DATABASE = 'gyms.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def close_db(exception=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Create gyms table if not exists
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.teardown_appcontext
def teardown_db(exception=None):
    close_db(exception)

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

        # Insert gyms into the database
        db = get_db()
        cursor = db.cursor()
        for gym in nearby_gyms:
            cursor.execute("INSERT INTO gyms (name, city, latitude, longitude) VALUES (?, ?, ?, ?)",
                           (gym, city, lat, lng))
        db.commit()

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
    init_db()
    app.run(debug=True)