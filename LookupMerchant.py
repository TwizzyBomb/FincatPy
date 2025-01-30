import re
import requests
import urllib.parse
import os
from dotenv import load_dotenv



def encode_url(base_url, params):
    # Encode the parameters (placeid and apikey)
    encoded_params = urllib.parse.urlencode(params)
    # Combine base URL with the encoded parameters
    encoded_url = f"{base_url}?{encoded_params}"
    return encoded_url

def extract_transaction_details(transaction_string):
    pattern = r"(?P<type>PURCHASE AUTHORIZED|POS|CHARGE)\s+ON\s+(?P<date>\d{2}/\d{2})\s+(?P<processor>\w+)\s+\*(?P<merchant>[A-Za-z0-9 &]+)\s+(?P<location>[A-Za-z ]+)\s+(?P<mid>S\d+)\s+CARD\s+(?P<card>\d{4})"
    match = re.search(pattern, transaction_string)
    return match.groupdict() if match else None

def identify_payment_processor(processor_code):
    processors = {
        "SQ": "Square",
        "PAYPAL": "PayPal",
        "STRIPE": "Stripe",
        "CLOVER": "Clover",
        "AMZN": "Amazon",
        "ZELLE": "Zelle",
        "VENMO": "Venmo"
    }
    return processors.get(processor_code, "Unknown Processor")

def lookup_merchant_info(place_id, api_key):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?placeid={place_id}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    return data["result"]["name"] if data.get("result") else "Merchant Not Found"

def get_place_id(api_key, place_name, location):
    # Construct the Text Search API URL
    base_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"

    url = encode_url(base_url, {"input": place_name + " " + location, "inputtype":"textquery", "fields":"name,place_id", "key":api_key})

    # Send the GET request to the Google Places API
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()

        # Check if any results are returned
        if data.get('candidates'):
            # Extract place_id from the first result
            place_id = data['candidates'][0].get('place_id')
            place_name = data['candidates'][0].get('name')
            return place_id, place_name
        else:
            print("No results found for the place.")
            return None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def get_mcc_category(mcc_code):
    mcc_codes = {
        "5812": "Restaurants",
        "5411": "Grocery Stores",
        "5732": "Electronics",
        "7997": "Clubs & Memberships",
    }
    return mcc_codes.get(mcc_code, "Unknown Category")

def extract_business_with_google_places_api(transaction_string, api_key):
    # use regex to extract the business portion of the expenditure string
    details = extract_transaction_details(transaction_string)
    if not details:
        print("Transaction details could not be extracted.")
        return
    
    # use the google place details api to obtain their place ID for use in the place details api
    details["placeId"], details["merchant_info"] = get_place_id(api_key, details["merchant"], details["location"])

    # details["processor_name"] = identify_payment_processor(details["processor"])
    if details["placeId"] and not details["merchant_info"]:
      details["merchant_info"] = lookup_merchant_info(details["placeId"], api_key)
    details["mcc_category"] = get_mcc_category("5812")  # Example MCC code
    
    print(details)
    return details["merchant_info"]

def main():
    load_dotenv()
    GPT_API_KEY = os.getenv("OAI_GPT_API_KEY")
    GOOG_MAPS_API_KEY = os.getenv("GOOG_MAPS_API_KEY")
    
    transaction_string = "PURCHASE AUTHORIZED ON 01/01 SQ *PROOF WINE & S Denver CO S384033859155009 CARD 4987"
    
    merchant_info = extract_business_with_google_places_api(transaction_string, GOOG_MAPS_API_KEY)
    print(f"Merchant info:{merchant_info}")

if __name__ == "__main__":
    main()
