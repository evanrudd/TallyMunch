import json
import requests

# Function to search for food and drink insights for a restaurant ID
def get_food_and_drink_options(business_id):
    # Define Yelp API endpoint for food and drinks insights
    endpoint = f'https://api.yelp.com/v3/businesses/{business_id}/insights/food_and_drinks'
    
    # Make a request to the Yelp API
    response = requests.get(endpoint, headers=headers)
    
    # Check if request was successful
    if response.status_code == 200:
        # Extract food and drink options from the response
        data = response.json()
        food_options = data.get('food_and_drinks', [])
        return food_options
    else:
        print(f"Error fetching data for restaurant with ID: {business_id}")
        return []

# Open yelp_result.txt file
with open('yelp_result.txt', 'r') as file:
    # Load JSON data
    data = json.load(file)
    
    # Extract restaurant IDs
    restaurant_ids = [business['id'] for business in data['businesses']]

# Define Yelp API Key and Headers
API_KEY = 'LRxqpc-PQzEld4r8aXa0ecMkfdyHQRllGJfBbBx8J4hShPCdnV8ydKWZYJJHhVV9PPx1_1tSV-Y1LKqHCryt1PaNhOHJrFdCHmhfiJN4akHDt7f9NPFpJD0s8ibWZXYx'
headers = {'Authorization': f'Bearer {API_KEY}'}

# Open food_result.txt file for writing
with open('food_result.txt', 'w') as file:
    # Iterate over each restaurant ID
    for business_id in restaurant_ids:
        # Write restaurant ID to file
        file.write(f"Restaurant ID: {business_id}\n")
        
        # Search for food and drink options for the restaurant
        food_options = get_food_and_drink_options(business_id)
        
        # Write restaurant alias and food options to file
        for business in data['businesses']:
            if business['id'] == business_id:
                alias = business['alias']
                file.write(f"Restaurant Alias: {alias}\n")
                break
        
        if food_options:
            # Write food options to file
            file.write("Food and Drink Options:\n")
            for option in food_options:
                file.write(f"- {option}\n")
        else:
            file.write("No food and drink options available\n")
        
        # Add a separator between restaurants
        file.write("\n-----------------\n\n")

print("Food and drink options have been written to food_result.txt file.")