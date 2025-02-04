import csv
import re
import requests
import openai
import os
import LookupMerchant
from bs4 import BeautifulSoup
from dotenv import load_dotenv

def extract_useful_portion(transaction):
    # Extract substring between "AUTHORIZED ON <DATE>" and "CARD"
    match = re.search(r"AUTHORIZED ON \d{2}/\d{2} (.*?) CARD", transaction)
    if match:
        return match.group(1).strip()
    return transaction.strip()

def online_search_for_category(merchant_name):
    # Perform a quick online search to suggest a category
    try:
        search_url = f"https://www.google.com/search?q={merchant_name.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        snippet = soup.find('div', class_='BNeawe').text if soup.find('div', class_='BNeawe') else None
        return snippet.lower() if snippet else "unknown:uncategorized"
    except Exception as e:
        print(f"Error during online search: {e}")
        return "unknown:uncategorized"

def categorize(transaction, category_map):
    # use map first if applicable
    for key, category in category_map.items():
        if key.lower() in useful_portion.lower():
            return category
        
    # If no match found, attempt to use chat gpt to categorize spending
    gpt_category = online_search_for_category(useful_portion)
    return online_category if online_category else "unknown:uncategorized"

# Function to send the string to the ChatGPT API for categorization
def categorize_with_chatgpt(input_string, api_key):
    # Define the prompt that will guide the model to categorize the string
    prompt = f"""
    You are a helpful assistant that categorizes business names into predefined categories. 
    Please return the category and subcategory in the format: 'category:subcategory'.
    
    Example categories:
    - 'drugs:alcohol'
    - 'outings:restaurants'
    - 'merchandise:clothes'
    - 'outings:movies'
    - 'services:linked_in'
    - 'drugs:parafenelia'
    
    Please categorize the following business name:
    "{input_string}"
    """

    client = openai.OpenAI(api_key=api_key)
    
    # Make the request to ChatGPT's API
    response = client.chat.completions.create(
        model="gpt-4",  # or another suitable engine
        messages=[{
            "role": "system",
            "content": "You are a helpful assistant that categorizes business names into predefined categories. "
                       "Please return the category and subcategory in this format: 'category:sub_category'. Notice"
                       "the underscores used as spaces and no special characters."
                       "    Example categories:"
                       " - 'drugs:alcohol'"
                       " - 'outings:restaurants'"
                       " - 'merchandise:clothes'"
                       " - 'outings:movies'"
                       " - 'services:linked_in'"
                       " - 'drugs:parafenelia'"
        },
        {
            "role": "user",
            "content": f'Please categorize the following business name: "{input_string}"'
        }],
        max_tokens=60,  # Limit the response length
        n=1,  # Get only one response
        temperature=0.5,  # Control randomness
    )
    
    # Extract and return the generated response
    return response.choices[0].message.content.strip()

def main():
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OAI_GPT_API_KEY") # Constant needs to be named as such for argumentless openai constructor
    testrows = ['Movement RiNo', 'Sushi-Rama RiNo', 'Walmart', '', 'Thump Coffee', 'Music City Hot Chicken at TRVE Brewing', 'Great Clips', 'BOXCAR', None, "Allsup's Convenience Store", 'Big Boys Bar-B-Que', 'Maverik', 'Package Austin', 'The Insurance Store']

    # Use Chat GPT or another gpt to categorize
    input_string = "Music City Hot Chicken at TRVE Brewing"
    category = categorize_with_chatgpt(input_string, OPENAI_API_KEY)
    print(f"Categorized as: {category}")


if __name__ == "__main__":
    # input_file = "ExpenditureStringTest.csv"  # Input CSV file
    # output_file = "ExpenditureStringTestOut.csv"  # Output CSV file
    main()



    # # Step 1: Build the initial mapping dictionary
    # category_map = {}
    # unsorted_rows = []

    # with open(input_file, 'r') as infile:
    #     reader = csv.reader(infile)
    #     rows = list(reader)
    #     header = rows[0]  # Keep the header row

    #     for row in rows[1:]:
    #         category, transaction = row
    #         if category.strip():
    #             # useful_portion = extract_useful_portion(transaction)

    #             category_map[useful_portion.lower()] = category
    #         else:
    #             unsorted_rows.append(row)

    # # Step 2: Categorize unsorted rows
    # for row in unsorted_rows:
    #     transaction = row[1]
    #     row[0] = categorize(transaction, category_map)

    # # Step 3: Write the output to a new CSV file
    # with open(output_file, 'w', newline='') as outfile:
    #     writer = csv.writer(outfile)
    #     writer.writerow(header)
    #     writer.writerows(rows)