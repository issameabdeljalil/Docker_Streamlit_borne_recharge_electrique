"""
Projet Linux
M2 MoSEF

app.py
"""
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static, st_folium
import seaborn as sns
import matplotlib.pyplot as plt
import folium

from mapping_utils import mapping, coord_arrondissements


import requests
import polyline

def get_route(start_coords, end_coords):
    """
    Appelle l'API OSRM pour calculer l'itinéraire entre deux points.
    """
    url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=polyline"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        route = data['routes'][0]
        polyline_points = route['geometry']  # Points encodés de la polyline
        decoded_points = polyline.decode(polyline_points)  # Décoder les points
        return decoded_points, route['distance'], route['duration']
    else:
        st.error("Impossible de calculer l'itinéraire.")
        return [], None, None


def prepare_data(df):
    """
    Prépare les données : extrait latitude et longitude à partir de coordonneesxy.
    """
    if 'coordonneesxy' in df.columns:
        # Séparation de la colonne 'coordonneesxy' en 'latitude' et 'longitude'
        df[['latitude', 'longitude']] = df['coordonneesxy'].str.split(',', expand=True)
        
        # Convertir en type float
        df['latitude'] = df['latitude'].astype(float)
        df['longitude'] = df['longitude'].astype(float)
    else:
        raise ValueError("La colonne 'coordonneesxy' est absente des données.")
    return df


def page_accueil(df):
    """
    page d'accueil
    """
    st.title('Visualisation des bornes de recharge pour véhicules électriques à Paris')

    st.markdown("""
    <div style="text-align: justify;">
    Ceci est une application de visualisation des bornes de recharge à Paris. 
    Les données incluent des informations sur l'emplacement, le statut et d'autres détails des bornes de recharge. 
    Vous pouvez explorer la carte ci-dessous pour voir la distribution des bornes de recharge dans différents arrondissements de Paris.
    </div>
    """, unsafe_allow_html=True)

    st.image("https://mobiwisy.fr/wp-content/uploads/Borne-recharge-Belib-Paris-e1669651299275-1068x702.jpg.webp", caption="Station Belib’")
    st.markdown("""
            <div style="text-align: justify;">
            Belib’ est le réseau public parisien de bornes de recharge pour véhicules électriques, opéré par Total Marketing France (TMF). Il est déployé depuis mars 2021 et comprend environ 430 stations, soit plus de 2000 bornes de recharge. 
            Des bornes de recharge rapide sont aussi déployées dans certains parcs concédés.
            Le réseau Belib' vous permet de recharger à tout moment votre véhicule électrique ou hybride rechargeable (2 roues motorisés compris). Les temps de recharge varient en fonction de la puissance sélectionnée. Si votre véhicule électrique le permet, la puissance maximale fournie par la borne sera de 22 kW. 
            Toutes les bornes Belib' disposent de prises T2, T3, domestique, Combo et CHAdeMo.

            Pour tout savoir et bénéficier du service, inscrivez-vous sur le [site belib.paris](https://belib.paris).
            </div>
            """, unsafe_allow_html=True)

    # carte de Paris en intégralité

    map = mapping(df)
    folium_static(map)


def page_recherche(df):
    """
    Page de recherche de bornes
    """
    # Sélection de l'arrondissement
    arrondissement = st.selectbox(
        label='Sélectionner un arrondissement',
        options=sorted(df['arrondissement'].unique())
    )
    df_arrondissement = df[df['arrondissement'] == arrondissement]

    st.markdown(f"## Points de recharge dans le {arrondissement}")
    map_arrondissement = mapping(df_arrondissement, centrage=coord_arrondissements(arrondissement), zoom=14)
    
    # Coordonnées de départ de l'utilisateur
    st.markdown("### Entrez vos coordonnées (latitude, longitude) :")
    user_lat = st.number_input("Latitude", value=48.8566, format="%.6f")
    user_lon = st.number_input("Longitude", value=2.3522, format="%.6f")

    # Calculer la borne la plus proche
    if st.button("Trouver la borne la plus proche"):
        df_arrondissement['distance'] = df_arrondissement.apply(
            lambda row: ((user_lat - row['latitude'])**2 + (user_lon - row['longitude'])**2)**0.5, axis=1
        )
        closest_borne = df_arrondissement.loc[df_arrondissement['distance'].idxmin()]
        
        # Calcul de l'itinéraire
        start_coords = (user_lat, user_lon)
        end_coords = (closest_borne['latitude'], closest_borne['longitude'])
        route_coords, route_distance, route_duration = get_route(start_coords, end_coords)
        
        # Ajout de l'itinéraire à la carte
        if route_coords:
            folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.7).add_to(map_arrondissement)
            folium.Marker(
                location=start_coords,
                popup="Point de départ",
                icon=folium.Icon(color="green")
            ).add_to(map_arrondissement)
            folium.Marker(
                location=end_coords,
                popup=f"{closest_borne['nom_station']}<br>Distance: {route_distance/1000:.2f} km<br>Durée: {route_duration/60:.2f} min",
                icon=folium.Icon(color="red")
            ).add_to(map_arrondissement)
        
        st.markdown(f"### Borne la plus proche : {closest_borne['nom_station']}")
        st.markdown(f"Adresse : {closest_borne['adresse_station']}")
        st.markdown(f"Distance estimée : {route_distance / 1000:.2f} km")
        st.markdown(f"Durée estimée : {route_duration / 60:.2f} minutes")

    # Affichage de la carte
    folium_static(map_arrondissement)


def page_data_analyse(df):
    """
    page data analyse
    """
    # Charger les données
    st.title("Points de Recharge pour Véhicules Électriques à Paris")
    st.write("Recherchez et explorez les points de recharge pour véhicules électriques dans Paris.")


    # Extraire latitude et longitude de la colonne coordonneesxy si elle existe

    # Graphique 1 : Répartition des Points de Recharge par Arrondissement
    st.subheader("Répartition des Points de Recharge par Arrondissement")
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.countplot(data=df, x="arrondissement", palette="viridis", order=df["arrondissement"].value_counts().index, ax=ax1)
    ax1.set_title("Nombre de Points de Recharge par Arrondissement")
    ax1.set_xlabel("Arrondissement")
    ax1.set_ylabel("Nombre de Points")
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
    st.pyplot(fig1)

    # Graphique 2 : Types de Prises Disponibles
    st.subheader("Types de Prises Disponibles")
    prise_cols = ["prise_type_ef", "prise_type_2", "prise_type_combo_ccs", "prise_type_chademo"]
    prises = df[prise_cols].sum().sort_values(ascending=False)
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    sns.barplot(x=prises.values, y=prises.index, palette="coolwarm", ax=ax2)
    ax2.set_title("Nombre de Points de Recharge par Type de Prise")
    ax2.set_xlabel("Nombre de Prises")
    ax2.set_ylabel("Type de Prise")
    st.pyplot(fig2)

    # Vérifier les coordonnées extraites
    st.subheader("Aperçu des Données avec Coordonnées")
    st.write(df[['nom_station', 'adresse_station', 'latitude', 'longitude']].head())

    # Filtrage des données (exemple de filtre par arrondissement)
    st.sidebar.header("Filtres")
    arrondissement = st.sidebar.selectbox("Choisissez l'arrondissement", options=df["arrondissement"].unique())
    data_filtered = df[df["arrondissement"] == arrondissement]

    # Créer la carte Folium
    map_paris = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

    # Ajouter les points de recharge sur la carte
    for _, row in data_filtered.iterrows():
        popup_text = f"""
        <b>Station :</b> {row['nom_station']}<br>
        <b>Adresse :</b> {row['adresse_station']}<br>
        <b>Type de Prises :</b> {", ".join([t for t in ['prise_type_ef', 'prise_type_2'] if row[t]])}<br>
        <b>Capacité :</b> {row['nbre_pdc']} points<br>
        <b>Accessibilité PMR :</b> {row['accessibilite_pmr']}<br>
        <b>Condition d'accès :</b> {row['condition_acces']}<br>
        <b>Tarification :</b> {row['tarification']}<br>
        """
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup_text,
            tooltip=row['nom_station'],
            icon=folium.Icon(color="blue" if row["puissance_nominale"] >= 7 else "green")
        ).add_to(map_paris)

    # Afficher la carte dans Streamlit
    st.subheader("Carte des Points de Recharge")
    st_folium(map_paris, width=700, height=500)

if __name__ == '__main__':
    # Charger les données
    df = pd.read_csv('data/raw_data.csv', sep=';')
    
    # Préparer les données
    df = prepare_data(df)

    # Barre latérale pour la navigation
    page = st.sidebar.selectbox("Navigation", ["Présentation", "Data analyse", "Recherche de bornes"])

    if page == "Présentation":
        page_accueil(df)
    elif page == "Data analyse":
        page_data_analyse(df)
    elif page == "Recherche de bornes":
        page_recherche(df)

        


