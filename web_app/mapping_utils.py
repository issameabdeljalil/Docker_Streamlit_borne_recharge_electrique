"""
Projet Linux
M2 MoSEF

mapping_utils.py
"""
import folium

def mapping(df, centrage=[48.8566, 2.3522], zoom = 12):
    """
    créateur d'une carte folium (leaflet) des bornes Belib
    map centrée sur le centre de Paris par défaut
    """
    map = folium.Map(location=centrage, zoom_start=zoom)

    # ajout cercles pour chaque borne de recharge
    for _, row in df.iterrows():
        lat, long = row["coordonneesxy"].split(", ")  # coordonnées latitude, longitude
        adresse = row["adresse_station"]
        statut = row["statut_pdc"]
        nom = row["nom_station"]
        
        
        folium.CircleMarker(
            location=[float(lat), float(long)],
            radius=5,
            color="black",
            fill=True,
            fill_color="green" if statut == "En service" else "red",
            fill_opacity=0.6,
            popup=f"<b>Adresse :</b> {adresse}<br><b>Statut :</b> {statut}",
            tooltip=nom
        ).add_to(map)

    return map

def coord_arrondissements(arrondissement:str) -> list:
    """
    coordonnées du centre approximatif de chaque arrondissement
    """
    coords = {
        '05e Arrondissement': [48.8443, 2.3499],
        '06e Arrondissement': [48.8505, 2.3327],
        '07e Arrondissement': [48.8561, 2.3127],
        '08e Arrondissement': [48.8722, 2.3163],
        '09e Arrondissement': [48.8765, 2.3386],
        '10e Arrondissement': [48.8745, 2.3596],
        '11e Arrondissement': [48.8579, 2.3799],
        '12e Arrondissement': [48.8359, 2.4143],
        '13e Arrondissement': [48.8292, 2.3553],
        '14e Arrondissement': [48.8317, 2.3237],
        '15e Arrondissement': [48.8390, 2.2923],
        '16e Arrondissement': [48.8642, 2.2707],
        '17e Arrondissement': [48.8855, 2.3168],
        '18e Arrondissement': [48.8925, 2.3442],
        '19e Arrondissement': [48.8842, 2.3824],
        '20e Arrondissement': [48.8647, 2.3984],
        'Paris centre': [48.8606, 2.3425]
    }
    return coords[arrondissement]