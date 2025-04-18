from flask import Flask, request, jsonify, render_template
import folium
import joblib
import pandas as pd
from geopy.distance import distance

app = Flask(__name__)
model = joblib.load('parking_zone_model.pkl')  # Ensure the model is correctly loaded
data = pd.read_csv('chennai_parking.csv')  # Ensure correct path to CSV

# Function to predict safety of a given coordinate based on nearby zones
def predict_safety(lat, lon):
    # Calculate distance from input location to all rows in the data
    data['Distance'] = data.apply(lambda row: distance((lat, lon), (row['Latitude'], row['Longitude'])).km, axis=1)
    
    # Get the closest matching zone from the dataset
    nearest = data.sort_values(by='Distance').iloc[0]
    
    # Extract features for the nearest zone
    features = [[
        nearest['Crime Rate'],
        nearest['Security Presence'],
        nearest['Traffic Density'],
        nearest['Lighting Quality']
    ]]
    
    # Predict the safety using the trained model
    prediction = model.predict(features)[0]
    
    # Return prediction and the nearest zone's details
    return prediction, nearest['Latitude'], nearest['Longitude'], nearest['Zone Type']

@app.route('/')
def index():
    return render_template('index.html')  # Make sure this file exists in the templates folder

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    # Ensure coordinates are provided
    try:
        lat = float(data['latitude'])
        lon = float(data['longitude'])
    except KeyError as e:
        return jsonify({'error': f'Missing parameter: {str(e)}'}), 400
    
    # Get prediction for the given coordinates
    prediction, lat_nearest, lon_nearest, zone_type = predict_safety(lat, lon)
    
    # Return the safety prediction
    return jsonify({
        'safety': prediction,
        'nearest_zone': {'latitude': lat_nearest, 'longitude': lon_nearest, 'zone_type': zone_type}
    })

@app.route('/map', methods=['GET'])
def map():
    # Load the map centered around Chennai
    chennai_map = folium.Map(location=[13.0827, 80.2707], zoom_start=12)

    # Add marker for current location (Chennai coordinates)
    folium.Marker([13.0827, 80.2707], icon=folium.Icon(color='blue'), tooltip='Current Location').add_to(chennai_map)

    # Get the 10 nearest locations based on distance to current location
    data['Distance'] = data.apply(lambda row: distance((13.0827, 80.2707), (row['Latitude'], row['Longitude'])).km, axis=1)
    nearest_data = data.sort_values(by='Distance').head(10)

    # Add markers for nearest locations, color-coded based on Zone Type
    for index, row in nearest_data.iterrows():
        color = 'green' if row['Zone Type'] == 'Safe Zone' else 'red'
        folium.Marker([row['Latitude'], row['Longitude']], icon=folium.Icon(color=color), tooltip=row['Zone Type']).add_to(chennai_map)

    return chennai_map._repr_html_()

if __name__ == '__main__':
    app.run(debug=True)
