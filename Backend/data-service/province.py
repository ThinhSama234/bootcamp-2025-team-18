import json
# Read JSON data from the file
with open("data.json", "r", encoding="utf8") as f:
    data_province = json.load(f)

# Iterate through all provinces, districts, and wards
list_address = []
for province in data_province:
    _id = province.get('Id')
    province_name = province.get('Name', 'Unknown Province')  # Use 'Unknown Province' if 'Name' is missing
    for district in province.get('Districts', []):  # Use an empty list if 'Districts' is missing
        district_name = district.get('Name', 'Unknown District')  # Default to 'Unknown District' if 'Name' is missing
        for ward in district.get('Wards', []):  # Use an empty list if 'Wards' is missing
            try:
                ward_name = ward['Name']  # Attempt to get the 'Name' key
                address = f"{_id},{ward_name},{district_name},{province_name}"
                #print(address)
                list_address.append(address)
            except KeyError:
                # If 'Name' key is missing in ward, skip this ward
                print(f"Missing 'Name' for a ward in district {district_name}, province {province_name}")
                continue  # Skip this ward and move to the next one
print(len(list_address))
# Save the list to a text file
with open("addresses.txt", "w", encoding="utf8") as f:
    for address in list_address:
        f.write(address + "\n")