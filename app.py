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
from mapping_utils import mapping
from geopy.distance import geodesic
from Adresse_get_routes import geocode_address_with_api_gouv, correct_address_with_api_gouv, find_nearest_borne, get_route

def prepare_data(df):
    """Prépare les données : extraire latitude et longitude de 'coordonneesxy' si elles existent."""
    if 'coordonneesxy' in df.columns:
        df[['latitude', 'longitude']] = df['coordonneesxy'].str.split(',', expand=True)
        df['latitude'] = df['latitude'].astype(float)
        df['longitude'] = df['longitude'].astype(float)
    else:
        st.error("La colonne 'coordonneesxy' est absente des données.")
    return df

def page_accueil(df):
    """
    Page d'accueil avec la carte de Paris.
    """
    st.title('Visualisation des bornes de recharge à Paris')

    st.markdown("""
    <div style="text-align: justify;">
    Application de visualisation des bornes de recharge à Paris. Vous pouvez explorer la carte ci-dessous pour voir la distribution des bornes.
    </div>
    """, unsafe_allow_html=True)

    st.image("https://mobiwisy.fr/wp-content/uploads/Borne-recharge-Belib-Paris-e1669651299275-1068x702.jpg.webp", caption="Station Belib’")

    map = mapping(df)
    folium_static(map)

def page_data_analyse(df):
    """
    Page d'analyse des données.
    """
    st.title("Points de Recharge pour Véhicules Électriques à Paris")
    st.write("Explorez les points de recharge à Paris.")

    st.subheader("Répartition des Points de Recharge par Arrondissement")
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.countplot(data=df, x="arrondissement", palette="viridis", order=df["arrondissement"].value_counts().index, ax=ax1)
    ax1.set_title("Nombre de Points de Recharge par Arrondissement")
    ax1.set_xlabel("Arrondissement")
    ax1.set_ylabel("Nombre de Points")
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
    st.pyplot(fig1)

    st.subheader("Types de Prises Disponibles")
    prise_cols = ["prise_type_ef", "prise_type_2", "prise_type_combo_ccs", "prise_type_chademo"]
    prises = df[prise_cols].sum().sort_values(ascending=False)
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    sns.barplot(x=prises.values, y=prises.index, palette="coolwarm", ax=ax2)
    ax2.set_title("Nombre de Points de Recharge par Type de Prise")
    ax2.set_xlabel("Nombre de Prises")
    ax2.set_ylabel("Type de Prise")
    st.pyplot(fig2)

    st.subheader("Aperçu des Données avec Coordonnées")
    st.write(df[['nom_station', 'adresse_station', 'latitude', 'longitude']].head())

    st.sidebar.header("Filtres")
    arrondissement = st.sidebar.selectbox("Choisissez l'arrondissement", options=df["arrondissement"].unique())
    data_filtered = df[df["arrondissement"] == arrondissement]

    map_paris = folium.Map(location=[48.8566, 2.3522], zoom_start=12)
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

    st.subheader("Carte des Points de Recharge")
    st_folium(map_paris, width=700, height=500)

def page_recherche(df):
    """Recherche de bornes à partir d'une adresse ou d'un clic sur la carte."""
    st.title("Trouver la borne la plus proche et itinéraire")
    
    mode = st.radio("Choisissez comment définir votre localisation", ["Saisir une adresse", "Cliquez sur la carte"])

    user_coords = None
    location = None  

    if mode == "Saisir une adresse":
        address = st.text_input("Entrez une adresse :")

        if address:
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

    elif mode == "Cliquez sur la carte":
        paris_map = folium.Map(location=[48.8566, 2.3522], zoom_start=12)
        location = st_folium(paris_map, width=700, height=500, returned_objects=["last_clicked"])

        if location and "last_clicked" in location:
            user_coords = (location["last_clicked"]["lat"], location["last_clicked"]["lng"])
            st.write(f"Coordonnées sélectionnées : Latitude = {user_coords[0]}, Longitude = {user_coords[1]}")
        else:
            st.write("Cliquez sur la carte pour sélectionner une localisation.")
    
    if user_coords:
        nearest_borne = find_nearest_borne(df, user_coords)

        if nearest_borne is not None:
            st.success(f"La borne la plus proche est à {nearest_borne['adresse_station']}.")
            st.write(f"Distance : {geodesic(user_coords, (nearest_borne['latitude'], nearest_borne['longitude'])).meters:.2f} mètres.")

            route_points, route_distance, route_duration = get_route(
                start_coords=user_coords,
                end_coords=(nearest_borne['latitude'], nearest_borne['longitude'])
            )

            if route_points:
                st.write(f"Distance totale : {route_distance / 1000:.2f} km")
                st.write(f"Durée estimée : {route_duration / 60:.2f} minutes")
                map_ = folium.Map(location=user_coords, zoom_start=15)
                folium.Marker(location=user_coords, popup="Vous êtes ici", icon=folium.Icon(color="red", icon="info-sign")).add_to(map_)
                folium.Marker(location=[nearest_borne['latitude'], nearest_borne['longitude']], popup=f"Borne : {nearest_borne['nom_station']}", icon=folium.Icon(color="green", icon="bolt")).add_to(map_)
                folium.PolyLine(route_points, color="blue", weight=5, opacity=0.8, tooltip="Itinéraire").add_to(map_)
                folium_static(map_)
            else:
                st.error("Impossible de tracer l'itinéraire.")
        else:
            st.error("Aucune borne de recharge trouvée.")
    else:
        st.write("Veuillez entrer une adresse ou cliquer sur la carte pour définir une localisation.")





if __name__ == '__main__':
    df = pd.read_csv('data/raw_data.csv', sep=';')
    df = prepare_data(df)
    page = st.sidebar.selectbox("Navigation", ["Présentation", "Data analyse", "Recherche de bornes"])

    if page == "Présentation":
        page_accueil(df)
    elif page == "Data analyse":
        page_data_analyse(df)
    elif page == "Recherche de bornes":
        page_recherche(df)
