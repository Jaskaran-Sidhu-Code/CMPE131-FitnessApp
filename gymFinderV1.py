#gym finder
import 

def find_nearby_gyms(location):
    api_key = "YOUR_GOOGLE_MAPS_API_KEY"
    endpoint = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    params = {
        "key": api_key,
        "location": location,    
        "radius": 5000,
        "keyword": "gym"
    }
    
    try:
        response = requests.get(endpoint, params=params)
        data = response.json()
        
        if data["status"] == "OK":
            gyms = []
            for result in data["results"]:
                name = result["name"]
                vicinity = result["vicinity"]
                gyms.append({"name": name, "vicinity": vicinity})
            return gyms
        else:
            print("Error:", data["status"])
            return None
    except Exception as e:
        print("An error occurred:", e)
        return None

if __name__ == "__main__":
    location = input("Enter your location (latitude, longitude): ")
    nearby_gyms = find_nearby_gyms(location)
    if nearby_gyms:
        print("Nearby Gyms:")
        for gym in nearby_gyms:
            print(gym["name"], "-", gym["vicinity"])
    else:
        print("No gyms found nearby.")
