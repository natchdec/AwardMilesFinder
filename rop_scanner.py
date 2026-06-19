import os
import json
import logging
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def check_rop_availability(origin, destination, departure_date, cabin_class):
    """
    Queries the ROP backend API for award flight availability.
    """
    
    from datetime import datetime
    
    # -------------------------------------------------------------------------
    # 1. UPDATE THIS URL
    # Replace with the actual endpoint URL from your intercepted cURL request.
    # -------------------------------------------------------------------------
    api_url = "https://www.thaiairways.com/airaward-flights/get-flight-info"
    
    # -------------------------------------------------------------------------
    # 2. UPDATE HEADERS
    # Map the headers from your intercepted cURL. 
    # Use the environment variables for authentication tokens/cookies.
    # -------------------------------------------------------------------------
    cookie_str = os.getenv("ROP_COOKIE", "")
    bearer_token = os.getenv("ROP_BEARER_TOKEN", "")
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        # Inject authentication dynamically:
        "Cookie": cookie_str,
        "Authorization": bearer_token if bearer_token else "",
        "access-control-expose-headers": "accessToken",
        "hostname": "https://www.thaiairways.com",
        "origin": "https://www.thaiairways.com",
        "referer": "https://www.thaiairways.com/en-th/redemption/select-flight",
        "source": "website"
    }
    
    # Clean up empty auth headers if they are not used
    if not headers["Authorization"]:
        del headers["Authorization"]
    if not headers["Cookie"]:
        del headers["Cookie"]

    # -------------------------------------------------------------------------
    # 3. UPDATE PAYLOAD
    # Map the JSON payload structure from your intercepted cURL.
    # Parameterize the origin, destination, date, and cabin_class.
    # -------------------------------------------------------------------------
    try:
        formatted_date = datetime.strptime(departure_date, "%Y-%m-%d").strftime("%d%m%y")
    except ValueError:
        formatted_date = departure_date # fallback
        
    payload = {
        "flightInfo": {
            "departure": origin,
            "arrival": destination,
            "departureDate": formatted_date
        },
        "tripType": "R"
    }
    
    try:
        logger.info(f"Checking availability: {origin} to {destination} on {departure_date} ({cabin_class})")
        response = requests.post(api_url, headers=headers, json=payload, timeout=15)
        
        # Handle Session Expiry (401 Unauthorized / 403 Forbidden)
        if response.status_code in (401, 403):
            logger.error("Session Expired: Please perform a manual login via browser and update the authentication values in the .env file.")
            return None
            
        response.raise_for_status()
        data = response.json()
        
        # -------------------------------------------------------------------------
        # 4. UPDATE RESPONSE PARSING
        # Update the keys below based on the actual JSON structure returned by the API.
        # -------------------------------------------------------------------------
        flights = []
        
        # Example parsing logic - ADJUST THIS to match actual response
        # Assume response looks like: {"data": {"flights": [{"flightNumber": "TG920", "departureTime": "23:45", "cabin": "Business", "status": "Available"}]}}
        raw_flights = data.get("data", {}).get("flights", [])
        
        if not raw_flights:
            logger.info("No flights found or unexpected response structure.")
            logger.debug(f"Raw response: {json.dumps(data, indent=2)}")
            return flights
            
        for flight in raw_flights:
            f_num = flight.get("flightNumber", "Unknown")
            d_time = flight.get("departureTime", "Unknown")
            c_class = flight.get("cabin", cabin_class)
            availability = flight.get("status", "Unknown")
            
            flights.append({
                "Flight Number": f_num,
                "Departure Time": d_time,
                "Cabin Class": c_class,
                "Status": availability
            })
            
            logger.info(f"Flight {f_num} | Dep: {d_time} | Cabin: {c_class} | Status: {availability}")
            
        return flights

    except requests.exceptions.RequestException as e:
        logger.error(f"API Request failed: {e}")
        return None

if __name__ == "__main__":
    # Example Usage
    ORIGIN = "BKK"
    DESTINATION = "FRA"
    DEPARTURE_DATE = "2026-08-15"
    CABIN_CLASS = "Business"  # Might need to use specific codes like 'C', 'J', etc. depending on API
    
    check_rop_availability(ORIGIN, DESTINATION, DEPARTURE_DATE, CABIN_CLASS)
