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
        '("Seaya" OR "Mundi Ventures" OR "Wayra" OR "Kibo Ventures") ("Partner" OR "Investor" OR "Director") "Madrid" linkedin',
        '("SoftBank" OR "Headline" OR "General Atlantic" OR "Actis") ("LatAm" OR "Latin America") "London" linkedin',
        
        '"venture capital" "Latin America" ("Madrid" OR "Spain") site:techcrunch.com OR site:latamlist.com',
        '"venture capital" "LatAm" ("London" OR "UK") site:contxto.com OR site:latamlist.com',
        '"family office" ("Latin America" OR "LatAm") ("Madrid" OR "London") "invested" OR "round"',
        
        'site:openvc.app ("Latin America" OR "LatAm") ("Madrid" OR "London")',
        'site:dealroom.co "invests in" ("Latin America" OR "LatAm") ("Madrid" OR "London")',
        'site:crunchbase.com/organization ("venture capital" OR "family office") ("Madrid" OR "London") "Latin America"'
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
                        has_target_location = any(term in text_to_check for term in [
                            "madrid", "spain", "españa", "london", "uk", "united kingdom"
                        ])
                        
                        has_latam_focus = any(term in text_to_check for term in [
                            "latam", "latin america", "américa latina", "brazil", "brasil", "mexico", "méxico", 
                            "colombia", "chile", "argentina", "peru", "uruguay"
                        ])
                        
                        has_investment_role = any(term in text_to_check for term in [
                            "venture capital", "vc", "family office", "angel investor", "general partner", 
                            "managing director", "investment director", "seed fund", "partner", "investor"
                        ])
                        
                        is_unwanted = any(term in text_to_check for term in [
                            "npl", "distressed", "real estate", "inmobiliario", "debt", "restructuring", 
                            "esg", "sustainability", "consulting", "wealth management", "services", "legal", 
                            "advisory", "concierge", "tax advisory", "private clients", "spear's 500"
                        ])
                        
                        if has_target_location and has_latam_focus and has_investment_role and not is_unwanted:
                            if link not in existing_links:
                                sheet.append_row([title, link, snippet, query])
                                existing_links.add(link)
                                print(f"Verified & Logged: {link}")

            except Exception as e:
                print(f"Error executing query: {e}")

if __name__ == "__main__":
    main()
