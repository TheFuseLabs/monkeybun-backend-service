from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException

from src.common.config import settings
from src.common.logger import logger


class GooglePlacesClient:
    def __init__(self):
        self.api_key = settings.GOOGLE_PLACES_API_KEY
        self.base_url = "https://places.googleapis.com/v1"

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "id,displayName,formattedAddress,location,addressComponents,plusCode",
        }

    def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        try:
            url = f"{self.base_url}/places/{place_id}"
            headers = self._get_headers()

            with httpx.Client() as client:
                response = client.get(url, headers=headers, timeout=10.0)

                if response.status_code == 404:
                    return None

                if response.status_code != 200:
                    logger.error(
                        f"Google Places API error: {response.status_code} - {response.text}"
                    )
                    raise HTTPException(
                        status_code=500, detail="Failed to fetch place details"
                    )

                return response.json()

        except httpx.RequestError as e:
            logger.error(f"Google Places API request error: {e}")
            raise HTTPException(
                status_code=500, detail="Google Places API unavailable"
            )
        except Exception as e:
            logger.error(f"Unexpected error in get_place_details: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to fetch place details"
            )

    def search_places(self, query: str) -> Optional[Dict[str, Any]]:
        try:
            url = f"{self.base_url}/places:searchText"
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.addressComponents",
            }

            payload = {"textQuery": query}

            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=payload, timeout=10.0)

                if response.status_code != 200:
                    logger.error(
                        f"Google Places API error: {response.status_code} - {response.text}"
                    )
                    raise HTTPException(
                        status_code=500, detail="Failed to search places"
                    )

                return response.json()

        except httpx.RequestError as e:
            logger.error(f"Google Places API request error: {e}")
            raise HTTPException(
                status_code=500, detail="Google Places API unavailable"
            )
        except Exception as e:
            logger.error(f"Unexpected error in search_places: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to search places"
            )

    def validate_and_enrich_location(
        self, place_id: str, location_text: Optional[str] = None
    ) -> Dict[str, Any]:
        place_data = self.get_place_details(place_id)

        if not place_data:
            raise HTTPException(
                status_code=404, detail="Place not found or invalid place ID"
            )

        location = place_data.get("location", {})
        address_components = place_data.get("addressComponents", [])

        city = None
        country = None

        for component in address_components:
            component_types = component.get("types", [])
            long_text = component.get("longText", "")

            if "locality" in component_types or "administrative_area_level_2" in component_types:
                if not city:
                    city = long_text
            if "country" in component_types:
                country = long_text

        display_name = place_data.get("displayName", {})
        display_text = display_name.get("text", "") if isinstance(display_name, dict) else ""

        enriched_data = {
            "google_place_id": place_id,
            "latitude": location.get("latitude"),
            "longitude": location.get("longitude"),
            "formatted_address": place_data.get("formattedAddress", ""),
            "city": city,
            "country": country,
            "location_text": location_text or display_text,
        }

        return enriched_data

