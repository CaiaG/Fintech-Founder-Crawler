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

    spreadsheet = client.open("Fintech Founders NYC")
    sheet = spreadsheet.get_worksheet(1)
    
    existing_links = set(sheet.col_values(2))
    print(f"Loaded {len(existing_links)} existing profiles from Google Sheet.")

    api_key = os.environ.get('SERPAPI_API_KEY')
    if not api_key:
        print("CRITICAL ERROR: Missing SERPAPI_API_KEY environment variable.")
        return

search_queries = [
    '"fintech" "venture capital" ("Madrid" OR "London") "Latin America" site:techcrunch.com OR site:latamlist.com',
    '"insurtech" OR "paytech" OR "embedded finance" ("Madrid" OR "London") "LatAm" site:contxto.com',
    
    'site:mundiventures.com "fintech" OR "latam fund"',
    'site:seaya.vc "fintech" OR "cathay latam"',
    
    'site:openvc.app "fintech" ("Latin America" OR "LatAm") ("Madrid" OR "London")',
    'site:dealroom.co "fintech" "invests in" ("Latin America" OR "LatAm") ("Spain" OR "UK")'
]



if has_target_location and has_latam_focus and has_fintech_focus and not is_unwanted:
    sheet.append_row([title, link, snippet, query])
    print(f"Logged Fintech Match: {link}")
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

                        has_fintech_focus = any(term in text_to_check for term in [
                            "fintech", "financial technology", "insurtech", "paytech", "payments", 
                            "banking", "lending", "embedded finance", "open banking", "crypto", "neobank"
                        ])
                        
                        is_unwanted = any(term in text_to_check for term in [
                            "real estate", "npl", "distressed", "esg", "sustainability", "consulting", 
                            "wealth management", "services", "legal", "cfo", "outsourced", "advisory"
                        ])
                        
                        if has_target_location and has_latam_focus and has_fintech_focus and not is_unwanted:
                            sheet.append_row([title, link, snippet, query])
                            print(f"Logged Fintech Match: {link}")
            except Exception as e:
                print(f"Error executing query: {e}")

if __name__ == "__main__":
    main()
