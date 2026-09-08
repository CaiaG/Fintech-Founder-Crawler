import os
import json
import time
import gspread
from duckduckgo_search import DDGS
from oauth2client.service_account import ServiceAccountCredentials

def main():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_json = json.loads(os.environ['GCP_CREDENTIALS'])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    
    sheet = client.open("Fintech Founders NYC").sheet1

    # Load existing links to prevent duplicates
    existing_links = set(sheet.col_values(2))
    print(f"Loaded {len(existing_links)} existing profiles from Google Sheet.")

    #  Define clean targeted queries for DuckDuckGo
    search_queries = [
        'site:linkedin.com/in/ founder fintech payments latam new york',
        'site:linkedin.com/in/ co-founder fintech payments africa new york',
        'site:linkedin.com/in/ CEO compliance KYB emerging markets new york',
        'site:linkedin.com/in/ founding team cross-border fintech latam africa new york'
    ]

    print("Starting DuckDuckGo crawler...")

    with DDGS() as ddgs:
        for query in search_queries:
            print(f"\n--- Executing query: {query} ---")
            
            try:
                results = ddgs.text(query, max_results=30)
                
                for r in results:
                    link = r.get('href', '')
                    title = r.get('title', '')
                    snippet = r.get('body', '')

                    if "linkedin.com/in/" in link:
                        if link in existing_links:
                            print(f"Skipped (Already exists): {link}")
                            continue

                        text_to_check = (title + " " + snippet).lower()
                        has_ny = any(term in text_to_check for term in [
                            "new york", 
                            "greater new york", 
                            "nyc", 
                            "new york city"
                        ])
                        
                        if has_ny:
                            sheet.append_row([title, link, snippet, query])
                            existing_links.add(link)
                            print(f"Verified & Logged (New): {link}")
                        else:
                            print(f"Filtered out (Not NY): {link}")
                            
            except Exception as e:
                print(f"Error executing query: {e}")

            time.sleep(2)

if __name__ == "__main__":
    main()
