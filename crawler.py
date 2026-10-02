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
    # Top Tier LatAm Markets (Mexico, Brazil, Colombia, Argentina, Chile)
    'site:linkedin.com/in/ ("Partner" OR "General Partner" OR "Director" OR "Investor") ("venture capital" OR "family office" OR "VC") ("Brazil" OR "Mexico" OR "Colombia" OR "Argentina" OR "Chile") ("madrid" OR "london")',
    'site:linkedin.com/in/ ("Head of Investments" OR "Investment Manager") ("family office" OR "venture capital") ("Brasil" OR "México" OR "Colombia" OR "Argentina" OR "Chile") ("madrid" OR "london" OR "europe")',
    
    # Regional & Secondary LatAm Markets (Peru, Uruguay, Miami/LatAm Hubs, Iberoamerica)
    'site:linkedin.com/in/ ("Partner" OR "Investor" OR "Managing Director") ("venture capital" OR "family office") ("Peru" OR "Uruguay" OR "Ecuador" OR "Iberoamerica" OR "South America") ("madrid" OR "london")',
    'site:linkedin.com/in/ ("Socio" OR "Director de Inversiones") ("fondo de inversión" OR "family office") ("México" OR "Brasil" OR "Colombia" OR "Hispanoamérica") ("madrid" OR "españa")',
    
    # Spanish Capital & Dual-HQ Cross-Border Focus
    'site:linkedin.com/in/ ("VC" OR "venture capital" OR "angel investor") ("cross-border" OR "Spain-LatAm" OR "Iberoamerica") ("madrid" OR "london" OR "europe")',
    'site:linkedin.com/company/ ("venture capital" OR "family office") ("Brazil" OR "Mexico" OR "Colombia" OR "Argentina" OR "LatAm") ("madrid" OR "london")',

    # Platform & Directory Searches (Updated)
    'site:openvc.app ("Brazil" OR "Mexico" OR "Colombia" OR "Chile" OR "LatAm") ("madrid" OR "london" OR "europe")',
    'site:dealroom.co "invests in" ("Brazil" OR "Mexico" OR "Colombia" OR "Latin America") ("spain" OR "uk" OR "madrid" OR "london")',
    'site:wellfound.com/u/ ("investor" OR "partner") ("Brazil" OR "Mexico" OR "Colombia" OR "LatAm") ("madrid" OR "london")',
    
    # Web & Document Mining
    'filetype:pdf ("venture capital" OR "family office") ("Brazil" OR "Mexico" OR "Colombia" OR "LatAm") ("madrid" OR "london") ("portfolio" OR "thesis")',
    '("fondo de inversión" OR "family office") ("madrid" OR "españa") ("México" OR "Colombia" OR "Brasil" OR "América Latina") "venture capital"'
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
                            "madrid", "spain", "españa", "london", "uk", "united kingdom", "europe", "europa"
                        ])
                        
                        # Expanded LatAm & Country Focus Terms
                        has_latam_focus = any(term in text_to_check for term in [
                            # Regional
                            "latam", "latin america", "américa latina", "spanish america", "south america", "iberoamerica", "hispanoamérica",
                            # Specific Major Countries
                            "brazil", "brasil", "mexico", "méxico", "colombia", "argentina", "chile", "peru", "perú", "uruguay"
                        ])
                        
                        if has_target_location and has_latam_focus:
                            sheet.append_row([title, link, snippet, query])
                            existing_links.add(link)
                            print(f"Verified & Logged: {link}")

            except Exception as e:
                print(f"Error executing query: {e}")

if __name__ == "__main__":
    main()
