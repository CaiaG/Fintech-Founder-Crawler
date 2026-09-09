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
    'site:linkedin.com/in/ ("founder" OR "co-founder" OR "CEO") ("fintech" OR "payments" OR "cross-border") ("latam" OR "latin america" OR "africa") ("new york" OR "greater new york city area")',
    'site:linkedin.com/in/ ("founder" OR "co-founder" OR "CEO") ("fintech" OR "payments" OR "cross-border") ("se asia" OR "southeast asia" OR "india") ("new york" OR "greater new york city area")',
    'site:linkedin.com/in/ ("founder" OR "co-founder" OR "CEO") ("KYB" OR "compliance") ("latam" OR "africa" OR "india" OR "se asia" OR "emerging markets") ("new york" OR "greater new york city area")',
    'site:linkedin.com/in/ ("Founding GTM" OR "Founding Team") ("fintech" OR "payments" OR "cross-border" OR "compliance") ("latam" OR "africa" OR "india" OR "se asia" OR "emerging markets") ("new york" OR "greater new york city area")',
    'site:linkedin.com/in/ ("founder" OR "co-founder" OR "CEO") ("embedded finance" OR "lending" OR "remittances" OR "neobank" OR "b2b payments") ("latam" OR "africa" OR "india" OR "se asia") ("new york" OR "greater new york city area")',
    'site:linkedin.com/in/ ("founder" OR "co-founder") ("YC" OR "Y Combinator" OR "Techstars") ("fintech" OR "payments") ("latam" OR "africa" OR "india" OR "southeast asia") ("new york" OR "nyc")',
    'site:linkedin.com/in/ ("founder" OR "co-founder") "fintech" ("latam" OR "africa" OR "india" OR "southeast asia") ("manhattan" OR "brooklyn" OR "nyc metro")',
    'site:wellfound.com/u/ ("founder" OR "CEO") ("fintech" OR "payments") ("latam" OR "africa" OR "india" OR "southeast asia") "New York"'
    ]

    print("Starting SerpApi crawler...")

    for query in search_queries:
        print(f"\n--- Executing query: {query} ---")
    
        for page in range(3):
            start_index = page * 10
            print(f"Checking page {page + 1} (start={start_index})...")
            
            params = {
                "engine": "google",
                "q": query,
                "api_key": api_key,
                "num": 10,
                "start": start_index
            }
    
            try:
                search = GoogleSearch(params)
                results = search.get_dict()
                items = results.get("organic_results", [])
    
                if not items:
                    print("No results found on this page. Moving to next query.")
                    break
    
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
