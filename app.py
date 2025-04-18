from flask import Flask, request, jsonify, render_template
import folium
import joblib
import pandas as pd
from geopy.distance import distance

app = Flask(__name__)

# Load ML model and data
model = joblib.load('parking_zone_model.pkl')  # Ensure model file is in the same directory
data = pd.read_csv('chennai_parking.csv')      # Ensure CSV file is in the same directory

# Function to predict safety based on nearest zone
def predict_safety(lat, lon):
    # Calculate distance from input location to all rows in the data
    data['Distance'] = data.apply(lambda row: distance((lat, lon), (row['Latitude'], row['Longitude'])).km, axis=1)
    
    # Get the closest zone
    nearest = data.sort_values(by='Distance').iloc[0]

    # Features for model prediction
    features = pd.DataFrame([{
    'Crime Rate': nearest['Crime Rate'],
    'Security Presence': nearest['Security Presence'],
    'Traffic Density': nearest['Traffic Density'],
    'Lighting Quality': nearest['Lighting Quality']}])

    # Predict using the model
    prediction = model.predict(features)[0]

    return prediction, nearest['Latitude'], nearest['Longitude'], nearest['Zone Type']

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Prediction API
@app.route('/predict', methods=['POST'])
def predict():
    data_req = request.get_json()

    try:
        lat = float(data_req['latitude'])
        lon = float(data_req['longitude'])
    except KeyError as e:
        return jsonify({'error': f'Missing parameter: {str(e)}'}), 400
    
    prediction, lat_nearest, lon_nearest, zone_type = predict_safety(lat, lon)

    return jsonify({
        'safety': prediction,
        'nearest_zone': {
            'latitude': lat_nearest,
            'longitude': lon_nearest,
            'zone_type': zone_type
        }
    })

# Map route with updated safety info in popup
@app.route('/map', methods=['GET'])
def map():
    current_lat = 13.0827
    current_lon = 80.2707

    # Get prediction for current location
    prediction, _, _, _ = predict_safety(current_lat, current_lon)

    # Create map centered at current location
    chennai_map = folium.Map(location=[current_lat, current_lon], zoom_start=12)

    # Add current location marker (always blue), with prediction info
    folium.Marker(
        [current_lat, current_lon],
        icon=folium.Icon(color='blue'),
        popup=f'{prediction}',
        tooltip='Current Location'
    ).add_to(chennai_map)

    # Add markers for 10 nearest zones
    data['Distance'] = data.apply(lambda row: distance((current_lat, current_lon), (row['Latitude'], row['Longitude'])).km, axis=1)
    nearest_data = data.sort_values(by='Distance').head(10)

    for _, row in nearest_data.iterrows():
        color = 'green' if row['Zone Type'] == 'Safe Zone' else 'red'
        folium.Marker(
            [row['Latitude'], row['Longitude']],
            icon=folium.Icon(color=color),
            tooltip=row['Zone Type']
        ).add_to(chennai_map)

    return chennai_map._repr_html_()

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
