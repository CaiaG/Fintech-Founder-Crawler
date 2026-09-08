import os
import json
import time
import gspread
from googlesearch import search
from oauth2client.service_account import ServiceAccountCredentials

def main():
    # 1. Authenticate with Google Sheets using the Secret stored in GitHub
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_json = json.loads(os.environ['GCP_CREDENTIALS'])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    
    # Replace with your actual Google Sheet name
    sheet = client.open("Fintech Founders NYC").sheet1

    # 2. Define the exact search parameters
    # This query discovers founders (Step 1) and filters by NYC location (Step 2) simultaneously.
    search_queries = [
        'site:linkedin.com/in/ ("Founder" OR "Co-Founder") "Fintech" ("Seed" OR "Series A") ("Africa" OR "Nigeria" OR "Kenya") ("New York" OR "Greater New York City Area")',
        'site:linkedin.com/in/ ("Founder" OR "Co-Founder") "Fintech" ("Seed" OR "Series A") ("Southeast Asia" OR "Indonesia" OR "Singapore") ("New York" OR "Greater New York City Area")',
        'site:linkedin.com/in/ ("Founder" OR "Co-Founder") "Fintech" ("Seed" OR "Series A") ("LATAM" OR "Brazil" OR "Mexico") ("New York" OR "Greater New York City Area")',
        'site:linkedin.com/in/ ("Founder" OR "Co-Founder") "Fintech" ("Seed" OR "Series A") "India" ("New York" OR "Greater New York City Area")'
    ]

    print("Starting crawler...")

    # 3. Execute searches and log directly to Google Sheets
    for query in search_queries:
        print(f"Executing query: {query}")
        
        # Adding pause to prevent GitHub Action IP from being rate-limited by Google
        time.sleep(5) 
        
        try:
            # Fetch top 10 results per region query
            for url in search(query, num_results=10, sleep_interval=2):
                if "linkedin.com/in/" in url:
                    # Log the URL and the query used to find them
                    sheet.append_row([url, query])
                    print(f"Found and logged: {url}")
        except Exception as e:
            print(f"Error during search: {e}")

if __name__ == "__main__":
    main()
