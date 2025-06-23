import pandas as pd

# Reload CSV after reset
csv_path = "aac_shelter_outcomes.csv"
df = pd.read_csv(csv_path)
# Convert to JSON array format
json_array = df.to_json(orient="records", lines=False)

# Save as .json file
with open("animal_outcomes.json", "w") as f:
    f.write(json_array)



