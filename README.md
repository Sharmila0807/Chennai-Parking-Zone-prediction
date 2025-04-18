# Chennai-Parking-Zone-prediction
## 🌐 Project Overview
The Chennai Parking Safety Map is a web application built using Flask and Leaflet.js that provides users with information about safe and dangerous parking zones in Chennai based on various factors such as crime rate, traffic density, and lighting quality.

---

## 🧠Features
- Interactive Map: Visualizes parking zones in Chennai, color-coded for safety.
- Current Location Safety: Displays whether the current location is safe or in a danger zone.
- Distance Calculation: Calculates and displays the nearest safe and danger zones relative to the user's location.

---

## 🧪 Model Details

- **Model Used**: Random Forest Classifier
- **Accuracy Achieved**: ~100%
- **Input Features**: Location coordinates
- **Output Classes**:  
  - `Safe`  
  - `Danger`

---

## 📁 Folder Structure

```
Project /
│
├── app.py                         # Flask backend
├── parking_zone_model.pkl        # Trained ML model
├── parking_zones.csv             # Dataset used for predictions
├── Dataset.ipynb                 # Code for dataset used for predictions
├── Model.ipynb                   # Code for Trained ML model
│
├── static/
│   └── favicon.png               # Browser tab icon
│
└── templates/
    └── index.html                # Home and map view
```

---
**Run the Application:**
python app.py
The application will be accessible at http://localhost:5000 by default.


**Technologies Used:** 
Python (Flask),
HTML/CSS/JavaScript (Bootstrap, Leaflet.js),
Pandas for data handling,
Scikit-learn for machine learning models and 
Folium for interactive maps .

---
