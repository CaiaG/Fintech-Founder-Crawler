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

    if not api_key or not cx_id:
        print("CRITICAL ERROR: Missing GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_CX environment variables.")
        return

    # target queries under Google's 32-word limit
    search_queries = [
        'site:linkedin.com/in/ founder fintech payments latam new york',
        'site:linkedin.com/in/ co-founder fintech payments africa new york',
        'site:linkedin.com/in/ CEO compliance KYB emerging markets new york',
        'site:linkedin.com/in/ founding team cross-border fintech latam africa new york'
    ]

    print("Starting API crawler...")

    for query in search_queries:
        print(f"\n--- Executing query: {query} ---")
        
        for start_index in range(1, 101, 10):
            endpoint = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': cx_id,
                'q': query,
                'num': 10,
                'start': start_index
            }

            try:
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

            except Exception as e:
                print(f"Error executing API request: {e}")
                break

            time.sleep(1)

if __name__ == "__main__":
    main()
