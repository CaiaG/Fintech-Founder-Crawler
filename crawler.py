import os
import json
import gspread
from serpapi import GoogleSearch
from oauth2client.service_account import ServiceAccountCredentials

def main():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_json = json.loads(os.environ['GCP_CREDENTIALS'])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    
    sheet = client.open("Fintech Founders NYC").sheet1
    existing_links = set(sheet.col_values(2))
    print(f"Loaded {len(existing_links)} existing profiles from Google Sheet.")

    api_key = os.environ.get('SERPAPI_API_KEY')
    if not api_key:
        print("CRITICAL ERROR: Missing SERPAPI_API_KEY environment variable.")
        return

    search_queries = [
        'site:linkedin.com/in/ founder fintech payments latam new york',
        'site:linkedin.com/in/ co-founder fintech payments africa new york',
        'site:linkedin.com/in/ CEO compliance KYB emerging markets new york',
        'site:linkedin.com/in/ founding team cross-border fintech latam africa new york'
    ]

    print("Starting SerpApi crawler...")

    for query in search_queries:
        print(f"\n--- Executing query: {query} ---")
        
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "num": 10
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            items = results.get("organic_results", [])

            if not items:
                print("No results found.")
                continue

            for item in items:
                link = item.get('link', '')
                title = item.get('title', '')
                snippet = item.get('snippet', '')

                if "linkedin.com/in/" in link:
                    if link in existing_links:
                        continue

                    text_to_check = (title + " " + snippet).lower()
                    has_ny = any(term in text_to_check for term in [
                        "new york", "greater new york", "nyc", "new york city"
                    ])
                    
                    if has_ny:
                        sheet.append_row([title, link, snippet, query])
                        existing_links.add(link)
                        print(f"Verified & Logged: {link}")

        except Exception as e:
            print(f"Error executing query: {e}")

if __name__ == "__main__":
    main()
