import requests
import streamlit as st
from geopy.distance import geodesic
import polyline

API_BASE_URL = "https://api-adresse.data.gouv.fr/search/?q={address}&limit=1"
OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving"

def fetch_address_data(address):
    """
    Appelle l'API Adresse du gouvernement pour obtenir les données géographiques d'une adresse.
    """
    url = API_BASE_URL.format(address=address)
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return None

def geocode_address_with_api_gouv(address):
    """
    Géocode une adresse en utilisant l'API du gouvernement et retourne les coordonnées (latitude, longitude).
    """
    data = fetch_address_data(address)
    if data and data.get("features"):
        coords = data["features"][0]["geometry"]["coordinates"]
        return float(coords[1]), float(coords[0])  # Retourne latitude, longitude
    else:
        st.error(f"Impossible de géocoder l'adresse : '{address}'.")
        return None, None

def correct_address_with_api_gouv(input_address):
    """
    Propose une correction d'adresse en utilisant l'API du gouvernement.
    """
    data = fetch_address_data(input_address)
    if data and data.get("features"):
        return data["features"][0]["properties"]["label"]
    return None

def find_nearest_borne(df, user_coords):
    """
    Trouve la borne la plus proche en fonction des coordonnées de l'utilisateur.
    """
    nearest_station = None
    min_distance = float("inf")
    
    for _, row in df.iterrows():
        station_coords = (row['latitude'], row['longitude'])
        distance = geodesic(user_coords, station_coords).meters
        if distance < min_distance:
            min_distance = distance
            nearest_station = row

    return nearest_station

def get_route(start_coords, end_coords):
    """
    Calcule l'itinéraire entre deux points en utilisant l'API OSRM.
    """
    url = f"{OSRM_BASE_URL}/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=polyline"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        route = data['routes'][0]
        polyline_points = route['geometry']
        decoded_points = polyline.decode(polyline_points)
        return decoded_points, route['distance'], route['duration']
    except requests.exceptions.RequestException:
        st.error("Erreur lors du calcul de l'itinéraire.")
        return [], None, None
