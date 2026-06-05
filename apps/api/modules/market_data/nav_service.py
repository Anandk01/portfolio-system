import requests
from typing import Optional, Dict
import re

class NAVService:
    """
    Service to fetch Mutual Fund NAVs for Indian markets.
    """
    def __init__(self):
        self.api_base = "https://api.mfapi.in/mf"
        self.cache: Dict[str, float] = {}

    def get_nav_by_isin(self, isin: str) -> Optional[float]:
        """
        Fetch Latest NAV using ISIN via search.
        """
        if isin in self.cache:
            return self.cache[isin]

        try:
            # Search for the ISIN to get the scheme code
            search_url = f"{self.api_base}/search?q={isin}"
            response = requests.get(search_url, timeout=10)
            data = response.json()

            if not data or len(data) == 0:
                print(f"Warning: No MF found for ISIN {isin}")
                return None

            scheme_code = data[0].get("schemeCode")
            if not scheme_code:
                return None

            # Fetch NAV for the scheme code
            nav_url = f"{self.api_base}/{scheme_code}"
            nav_response = requests.get(nav_url, timeout=10)
            nav_data = nav_response.json()

            if "data" in nav_data and len(nav_data["data"]) > 0:
                latest_nav = float(nav_data["data"][0]["nav"])
                self.cache[isin] = latest_nav
                return latest_nav

        except Exception as e:
            print(f"Error fetching NAV for {isin}: {e}")
        
        return None

    def get_nav_by_name(self, name: str) -> Optional[float]:
        """
        Fetch Latest NAV by searching for the fund name.
        """
        try:
            # Clean name for better search
            clean_name = re.sub(r'[^a-zA-Z0-9 ]', ' ', name).strip()
            search_url = f"{self.api_base}/search?q={clean_name}"
            response = requests.get(search_url, timeout=10)
            data = response.json()

            if not data or len(data) == 0:
                return None

            # Take the first exact or best match
            scheme_code = data[0].get("schemeCode")
            nav_url = f"{self.api_base}/{scheme_code}"
            nav_response = requests.get(nav_url, timeout=10)
            nav_data = nav_response.json()

            if "data" in nav_data and len(nav_data["data"]) > 0:
                return float(nav_data["data"][0]["nav"])
        except Exception as e:
            print(f"Error fetching NAV by name {name}: {e}")
        
        return None

nav_service = NAVService()
