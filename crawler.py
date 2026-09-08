import os
import json
import time
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def main():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_json = json.loads(os.environ['GCP_CREDENTIALS'])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    
    sheet = client.open("Fintech Founders NYC").sheet1

    api_key = os.environ.get('GOOGLE_SEARCH_API_KEY')
    cx_id = os.environ.get('GOOGLE_SEARCH_CX')

    search_queries = [

        'site:linkedin.com/in/ ("founder" OR "co-founder" OR "CEO") ("fintech" OR "payments" OR "cross-border") ("latam" OR "latin america") ("new york" OR "greater new york city area")',
        'site:linkedin.com/in/ ("founder" OR "co-founder" OR "CEO") ("fintech" OR "payments" OR "cross-border") ("africa" OR "emerging markets") ("new york" OR "greater new york city area")',
        'site:linkedin.com/in/ ("founder" OR "co-founder" OR "CEO") ("KYB" OR "compliance") ("latam" OR "latin america" OR "africa" OR "emerging markets") ("new york" OR "greater new york city area")',
        'site:linkedin.com/in/ ("Founding GTM" OR "Founding Team") ("fintech" OR "payments" OR "cross-border" OR "KYB" OR "compliance") ("latam" OR "africa" OR "emerging markets") "new york"'
    ]

    print("Starting crawler...")

    for query in search_queries:
        print(f"\n--- Executing query: {query} ---")
        
        # Paginate 10 pages (10 results per page = 100 results per query)
        for start_index in range(1, 101, 10):
            endpoint = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': cx_id,
                'q': query,
                'num': 10,
                'start': start_index  
            }

            response = requests.get(endpoint, params=params)
            if response.status_code != 200:
                print(f"API Error ({response.status_code}): {response.text}")
                break

            data = response.json()
            items = data.get('items', [])

            if not items:
                print(f"No more results found for this query at start index {start_index}.")
                break

            for item in items:
                link = item.get('link', '')
                title = item.get('title', '')
                snippet = item.get('snippet', '')

                if "linkedin.com/in/" in link:
                    sheet.append_row([title, link, snippet, query])
                    print(f"Logged: {link}")

            
            time.sleep(1)

if __name__ == "__main__":
    main()
