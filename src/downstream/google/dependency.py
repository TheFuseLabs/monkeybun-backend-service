from src.downstream.google.google_places_client import GooglePlacesClient

google_places_client = GooglePlacesClient()


def get_google_places_client() -> GooglePlacesClient:
    return google_places_client

