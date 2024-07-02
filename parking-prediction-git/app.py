from flask import Flask, request, jsonify, render_template
import folium
import joblib
import pandas as pd
from geopy.distance import distance

app = Flask(__name__)
model = joblib.load('parking_zone_model.pkl')
data = pd.read_csv('parking_zones.csv')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    # Ensure all required features are included
    try:
        prediction = model.predict([[
            float(data['Crime Rate']),
            float(data['Security Presence']),
            float(data['Traffic Density']),
            float(data['Lighting Quality'])
        ]])

        return jsonify({'safety': prediction[0]})
    except KeyError as e:
        return jsonify({'error': f'Missing feature: {str(e)}'}), 400

@app.route('/map')
def map():
    # Load map centered around Chennai
    chennai_map = folium.Map(location=[13.0827, 80.2707], zoom_start=12)

    # Add marker for current location (Chennai coordinates)
    folium.Marker([13.0827, 80.2707], icon=folium.Icon(color='blue'), tooltip='Current Location').add_to(chennai_map)

    # Calculate distances to all locations and sort by distance
    data['Distance'] = data.apply(lambda row: distance((13.0827, 80.2707), (row['Latitude'], row['Longitude'])).km, axis=1)
    data_sorted = data.sort_values(by='Distance').head(10)

    # Add markers for nearest 10 locations
    for index, row in data_sorted.iterrows():
        color = 'green' if row['Zone Type'] == 'Safe Zone' else 'red'
        folium.Marker([row['Latitude'], row['Longitude']], icon=folium.Icon(color=color), tooltip=row['Zone Type']).add_to(chennai_map)

    return chennai_map._repr_html_()

if __name__ == '__main__':
    app.run(debug=True)

