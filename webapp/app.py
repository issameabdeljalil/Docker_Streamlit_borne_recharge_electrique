"""
Projet Linux
M2 MoSEF

app.py
"""
import folium
import pandas as pd

df = pd.read_csv('data/raw_data.csv', sep=';')

# map centrée sur Paris
map = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

# marqueurs pour chaque point de recharge
for _, row in df.iterrows():

    lat, long = row["coordonneesxy"].split(", ") # coordonnées latitude, longitude
    adresse = row["adresse_station"]
    statut = row["statut_pdc"]
    nom = row["nom_station"]
    
    # ajout cercles sur la carte
    folium.CircleMarker(
        location=[float(lat), float(long)],
        radius=5,
        color="green" if statut == "En service" else "red",
        fill=True,
        fill_color="green" if statut == "En service" else "red",
        fill_opacity=0.6,
        popup=f"<b>Adresse :</b> {adresse}<br><b>Statut :</b> {statut}",
        tooltip=nom
    ).add_to(map)

# sauvagarde de la carte des points de recharge
map.save("maps/map_points_recharge.html")