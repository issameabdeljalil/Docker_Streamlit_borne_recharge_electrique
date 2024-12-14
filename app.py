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
from geopy.distance import geodesic
from adresse_get_routes import geocode_address_with_api_gouv, correct_address_with_api_gouv, find_nearest_borne, get_route
from geopy.geocoders import Nominatim
import geocoder
from PIL import Image

def prepare_data(df):
    """Prépare les données : extraire latitude et longitude de 'coordonneesxy' si elles existent."""
    if 'coordonneesxy' in df.columns:
        try:
            df[['latitude', 'longitude']] = df['coordonneesxy'].str.split(',', expand=True)
            df['latitude'] = df['latitude'].astype(float)
            df['longitude'] = df['longitude'].astype(float)
        except Exception as e:
            st.error(f"Erreur lors de la préparation des données : {e}")
    else:
        st.error("La colonne 'coordonneesxy' est absente des données.")
    return df

def get_detailed_address(lat, lon):
    """Retourne une adresse détaillée basée sur des coordonnées latitude/longitude."""
    geolocator = Nominatim(user_agent="e_power_paris")
    try:
        location = geolocator.reverse((lat, lon), exactly_one=True)
        if location and location.address:
            return location.address
    except Exception as e:
        st.warning(f"Impossible de récupérer une adresse détaillée : {e}")
    return None

def page_accueil(df):
    """
    Page d'accueil avec la carte de Paris.
    """
    st.markdown("""
    <div style="text-align: center;">
    <h1>🚗 <strong>Bienvenue sur e-Power Paris</strong> ⚡</h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: justify;">
    Ceci est une application de visualisation des bornes de recharge à Paris. 
    Les données incluent des informations sur l'emplacement, le statut et d'autres détails sur les bornes de recharge. 
    Vous pouvez explorer la carte ci-dessous pour voir la distribution des bornes de recharge dans les différents arrondissements de Paris.
    </div>
    """, unsafe_allow_html=True)

    # logos
    
    try:
        img = Image.open("data/belib.jpg")  #  image belib locale
        st.image(img, caption="Station Belib’", width=600)
    except FileNotFoundError:
        st.error("L'image 'belib.jpg' est introuvable. Vérifiez le chemin.")
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'image : {e}")

    # carte des stations disponibles

    map = mapping(df)
    st.subheader("Carte des Points de Recharge à Paris")
    folium_static(map)

def page_data_analyse(df):
    """
    Page d'analyse des données
    """
    st.title("Analyse des données")
    st.write("Explorez les points de recharge à Paris.")

    # barplot 1

    try:
        st.subheader("Répartition des points de recharge par arrondissement")
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        sns.countplot(data=df, x="arrondissement", palette="viridis", order=df["arrondissement"].value_counts().index, ax=ax1)
        ax1.set_title("Nombre de Points de Recharge par Arrondissement")
        ax1.set_xlabel("Arrondissement")
        ax1.set_ylabel("Nombre de Points")
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
        st.pyplot(fig1)
    except Exception as e:
        st.error(f"Erreur lors de la visualisation des données : {e}")

    # barplot 2

    try:
        st.subheader("Types de prises disponibles")
        prise_cols = ["prise_type_ef", "prise_type_2", "prise_type_combo_ccs", "prise_type_chademo"]
        prises = df[prise_cols].sum().sort_values(ascending=False)
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        sns.barplot(x=prises.values, y=prises.index, palette="coolwarm", ax=ax2)
        ax2.set_title("Nombre de points de recharge par type de prise")
        ax2.set_xlabel("Nombre de prises")
        ax2.set_ylabel("Type de prise")
        st.pyplot(fig2)
    except Exception as e:
        st.error(f"Erreur lors de l'analyse des types de prises : {e}")

    # carte avec selection des arrondissements

    arrondissement = st.sidebar.selectbox("Choisissez l'arrondissement", options=df["arrondissement"].unique())
    data_filtered = df[df["arrondissement"] == arrondissement]

    map_paris = folium.Map(location=coord_arrondissements(arrondissement), zoom_start=13)
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

    st.subheader("Carte des stations situées dans le " + arrondissement)
    st_folium(map_paris, width=700, height=500)

    st.subheader("Stations situées dans le " + arrondissement)
    
    data_filtered = data_filtered.rename(columns={
        'nom_station': 'Nom de la station',
        'adresse_station': 'Adresse de la station',
        'latitude': 'Latitude',
        'longitude': 'Longitude'
    })

    colonnes = ['Nom de la station', 'Adresse de la station', 'Latitude', 'Longitude']
    st.write(data_filtered[colonnes].reset_index(drop=True))

def page_recherche_adresse(df):
    """Recherche de bornes à partir d'une adresse"""
    st.title("Recherche de borne et itinéraire")

    user_coords = None
    detected_address = None

    col1, col2 = st.columns(2)
    with col1:
        address = st.text_input("Entrez une adresse pour définir votre localisation :", value=detected_address if detected_address else "")
    with col2:
        if st.button("Utiliser ma position actuelle"):
            try:
                g = geocoder.ip('me')  # Détection basée sur l'adresse IP
                if g.latlng:
                    user_coords = tuple(g.latlng)
                    st.success(f"Position actuelle détectée : Latitude = {user_coords[0]}, Longitude = {user_coords[1]}")

                    detailed_address = get_detailed_address(user_coords[0], user_coords[1])
                    if detailed_address:
                        detected_address = detailed_address
                        st.info(f"Adresse détectée : {detailed_address}")
                        address = detected_address
                    else:
                        st.warning("Impossible de récupérer une adresse exacte pour votre position actuelle.")
                else:
                    st.error("Impossible de détecter votre position actuelle. Vérifiez votre connexion internet.")
            except Exception as e:
                st.error(f"Erreur lors de la détection de la position actuelle : {e}")

    if address and not user_coords:
        corrected_address = correct_address_with_api_gouv(address)
        if corrected_address:
            st.write(f"Correction suggérée : {corrected_address}")
            use_corrected = st.radio("Voulez-vous utiliser l'adresse corrigée ?", options=["Oui", "Non"])
            if use_corrected == "Oui":
                address = corrected_address

        user_lat, user_lon = geocode_address_with_api_gouv(address)
        if user_lat and user_lon:
            user_coords = (user_lat, user_lon)
            st.write(f"Adresse géocodée : Latitude = {user_lat}, Longitude = {user_lon}")
    
    if user_coords:
        nearest_borne = find_nearest_borne(df, user_coords)

        if nearest_borne is not None:
            st.success(f"La borne la plus proche est située au {nearest_borne['adresse_station']}.")
            st.write(f"Distance directe : {geodesic(user_coords, (nearest_borne['latitude'], nearest_borne['longitude'])).meters:.2f} mètres.")

            route_points, route_distance, route_duration = get_route(
                start_coords=user_coords,
                end_coords=(nearest_borne['latitude'], nearest_borne['longitude'])
            )

            if route_points:
                st.write(f"Distance totale du parcours : {route_distance / 1000:.2f} km")
                heures = int(route_duration // (60*60))
                minutes = int((route_duration % (60*60)) / 60)
                if heures == 0:
                    st.write(f"Durée estimée : {minutes} minutes")
                else:
                    st.write(f"Durée estimée : {heures} heures et {minutes} minutes")
                map_ = folium.Map(location=user_coords, zoom_start=15)
                folium.Marker(location=user_coords, popup="Vous êtes ici", icon=folium.Icon(color="red", icon="info-sign")).add_to(map_)
                folium.Marker(location=[nearest_borne['latitude'], nearest_borne['longitude']], popup=f"Borne : {nearest_borne['nom_station']}", icon=folium.Icon(color="green", icon="bolt")).add_to(map_)
                folium.PolyLine(route_points, color="blue", weight=5, opacity=0.8, tooltip="Itinéraire").add_to(map_)
                folium_static(map_)
            else:
                st.error("Impossible de tracer l'itinéraire.")
        else:
            st.error("Aucune borne de recharge trouvée.")

if __name__ == '__main__':
    st.set_page_config(layout="wide")  # Configuration pour un layout large

    try:
        df = pd.read_csv('data/raw_data.csv', sep=';')
        df = prepare_data(df)
    except FileNotFoundError:
        st.error("Le fichier 'raw_data.csv' est introuvable.")
        df = pd.DataFrame()  # Créer un DataFrame vide pour éviter les erreurs

    with st.sidebar:
        try:
            img = Image.open("data/RESIZE.png")
            img_resized = img.resize((100, 100))
            st.image(img_resized)
        except FileNotFoundError:
            st.error("Le fichier logo est introuvable.")
        except Exception as e:
            st.error(f"Erreur lors du traitement du logo : {e}")
    
    page = st.sidebar.radio("Navigation", ["Présentation", "Data Analyse", "Recherche d'adresse"])

    if page == "Présentation":
        page_accueil(df)
    elif page == "Data Analyse":
        page_data_analyse(df)
    elif page == "Recherche d'adresse":
        page_recherche_adresse(df)
