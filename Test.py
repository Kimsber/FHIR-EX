import requests

# FHIR server endpoint (Taiwan Core)
FHIR_SERVER = "https://twcore.hapi.fhir.tw/fhir/"

# LOINC codes for height and weight
LOINC_HEIGHT = "8302-2"
LOINC_WEIGHT = "29463-7"
LONIC_Main = "85353-1"  # LONIC: Vital signs, weight, height, head circumference, oxygen saturation and BMI panel

# Fetch the latest observation for a given LOINC code from the FHIR server
def fetch_observations(loinc_code, count=50):
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


# Fetch all available height and weight observations (set a high count, e.g., 100)
height_observations = fetch_observations(LOINC_HEIGHT)
weight_observations = fetch_observations(LOINC_WEIGHT)

# Pair height and weight observations by index and calculate BMI for each pair
num_pairs = min(len(height_observations), len(weight_observations))
for i in range(num_pairs):
    height_value, height_unit = height_observations[i]
    weight_value, weight_unit = weight_observations[i]
    print(f"Pair {i+1}:")
    print(f"  Height: {height_value} {height_unit}")
    print(f"  Weight: {weight_value} {weight_unit}")
    if height_value and weight_value:
        height_in_m = height_value / 100 if height_unit in ["cm", "centimeter", "centimeters"] else height_value
        bmi = weight_value / (height_in_m ** 2)
        print(f"  Calculated BMI: {bmi:.2f}")
    else:
        print("  Unable to calculate BMI for this pair.")