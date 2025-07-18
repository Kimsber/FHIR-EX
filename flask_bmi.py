from flask import Flask, render_template
import requests

app = Flask(__name__)

FHIR_SERVER = "https://twcore.hapi.fhir.tw/fhir/"
LOINC_HEIGHT = "8302-2"
LOINC_WEIGHT = "29463-7"

def fetch_observations(loinc_code, count=10):
    url = str(FHIR_SERVER + f"Observation?code=http://loinc.org|{loinc_code}&_sort=-date&_count={count}")
    results = []
    while url:
        response = requests.get(url)
        if response.status_code != 200:
            break
        bundle = response.json()
        entries = bundle.get("entry", [])
        for entry in entries:
            obs = entry["resource"]
            value = obs.get("valueQuantity", {}).get("value")
            unit = obs.get("valueQuantity", {}).get("unit")
            results.append((value, unit))
        # Find the next page link
        next_url = None
        for link in bundle.get("link", []):
            if link.get("relation") == "next":
                next_url = link.get("url")
                break
        url = next_url
    return results

@app.route('/')
def home():
    return "Welcome to the FHIR API! Try /bmi for BMI calculations."

@app.route('/bmi')
def bmi():
    height_observations = fetch_observations(LOINC_HEIGHT, count=10)
    weight_observations = fetch_observations(LOINC_WEIGHT, count=10)
    num_pairs = min(len(height_observations), len(weight_observations))
    bmi_results = []
    for i in range(num_pairs):
        height_value, height_unit = height_observations[i]
        weight_value, weight_unit = weight_observations[i]
        if height_value and weight_value:
            height_in_m = height_value / 100 if height_unit in ["cm", "centimeter", "centimeters"] else height_value
            bmi = weight_value / (height_in_m ** 2)
            bmi_results.append({
                'index': i+1,
                'height': f"{height_value} {height_unit}",
                'weight': f"{weight_value} {weight_unit}",
                'bmi': f"{bmi:.2f}"
            })
        else:
            bmi_results.append({
                'index': i+1,
                'height': f"{height_value} {height_unit}",
                'weight': f"{weight_value} {weight_unit}",
                'bmi': "Unable to calculate"
            })
    return render_template('index.html', bmi_results=bmi_results)

if __name__ == '__main__':
    app.run(debug=True)
