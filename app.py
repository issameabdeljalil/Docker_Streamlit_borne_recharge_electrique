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


def prepare_data(df):
    """Prépare les données : extraire latitude et longitude de 'coordonneesxy' si elles existent."""
    if 'coordonneesxy' in df.columns:
        df[['latitude', 'longitude']] = df['coordonneesxy'].str.split(',', expand=True)
        df['latitude'] = df['latitude'].astype(float)
        df['longitude'] = df['longitude'].astype(float)
    else:
        st.error("La colonne 'coordonneesxy' est absente des données.")
    return df

# Configurer la page
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/ea/Logo_application_ePower_Paris.png", width=200)

# Ajouter un logo et un titre dans la barre latérale

st.sidebar.title("ePower Paris")
st.sidebar.markdown("Explorez les bornes de recharge électriques à Paris 🚗⚡")


def page_accueil(df):
    """
<<<<<<< HEAD
    Page d'accueil
    """
    # Ajouter le titre et le texte de présentation
    st.title('ePower Paris')
    st.markdown("""
    <div style="text-align: justify;">
    Bienvenue dans <b>ePower Paris</b>, une application dédiée à la visualisation des bornes de recharge pour véhicules électriques à Paris. 
    Les données disponibles fournissent des informations détaillées sur l'emplacement, le statut, ainsi que d'autres caractéristiques des bornes de recharge.
    Explorez la carte interactive ci-dessous pour découvrir la répartition des bornes dans les différents arrondissements parisiens et planifiez vos trajets en conséquence.
    </div>
    """, unsafe_allow_html=True)

    # Ajouter un espace avant l'image
    st.markdown("<br>", unsafe_allow_html=True)

    # Ajouter une image illustrative
    st.image("https://www.automobile-propre.com/wp-content/uploads/2011/10/autolib.jpg", caption="Station Belib’")

    # Ajouter une description supplémentaire
    st.markdown("""
            <div style="text-align: justify;">
            Belib’ est le réseau public parisien de bornes de recharge pour véhicules électriques, opéré par Total Marketing France (TMF). 
            Il est déployé depuis mars 2021 et comprend environ 430 stations, soit plus de 2000 bornes de recharge. 
            Des bornes de recharge rapide sont aussi déployées dans certains parcs concédés. Pour tout savoir et bénéficier du service, inscrivez-vous sur le 
            [site belib.paris](https://belib.paris).
            </div>
            """, unsafe_allow_html=True)

    # Ajouter un séparateur
    st.markdown("---")
=======
    Page d'accueil avec la carte de Paris.
    """
    st.title('Visualisation des bornes de recharge à Paris')

    st.markdown("""
    <div style="text-align: justify;">
    Application de visualisation des bornes de recharge à Paris. Vous pouvez explorer la carte ci-dessous pour voir la distribution des bornes.
    </div>
    """, unsafe_allow_html=True)

    st.image("https://mobiwisy.fr/wp-content/uploads/Borne-recharge-Belib-Paris-e1669651299275-1068x702.jpg.webp", caption="Station Belib’")
>>>>>>> e614677bc246cebbd8bdf1e2f3320db02b0aafae

    # Carte de Paris en intégralité
    map = mapping(df)
    st.subheader("Carte des Points de Recharge à Paris")
    folium_static(map)

<<<<<<< HEAD
def page_recherche(df):
    """
    Page de recherche de bornes
    """
    # Filtrer par arrondissement
    st.subheader("Rechercher des Bornes de Recharge")
    arrondissement = st.selectbox(
        label='Sélectionnez un arrondissement',
        options=sorted(df['arrondissement'].unique())
    )

    df_arrondissement = df[df['arrondissement'] == arrondissement]

    # Carte des bornes filtrées
    st.markdown(f"## Points de recharge dans le {arrondissement}")
    map_arrondissement = mapping(df_arrondissement, centrage=coord_arrondissements(arrondissement), zoom=14)
    folium_static(map_arrondissement)

    # Détails des bornes
    st.markdown(f"## Détails des bornes de recharge dans le {arrondissement}")
    st.dataframe(df_arrondissement[['nom_station', 'adresse_station', 'statut_pdc', 'puissance_nominale']].reset_index(drop=True))
=======
>>>>>>> e614677bc246cebbd8bdf1e2f3320db02b0aafae

def page_data_analyse(df):
    """
    Page d'analyse des données
    """
    st.title("Data Analyse")
    st.write("Explorez les points de recharge à Paris.")

    st.subheader("Répartition des points de recharge par arrondissement")
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.countplot(data=df, x="arrondissement", palette="viridis", order=df["arrondissement"].value_counts().index, ax=ax1)
    ax1.set_title("Nombre de Points de Recharge par Arrondissement")
    ax1.set_xlabel("Arrondissement")
    ax1.set_ylabel("Nombre de Points")
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
    st.pyplot(fig1)

    st.subheader("Types de prises disponibles")
    prise_cols = ["prise_type_ef", "prise_type_2", "prise_type_combo_ccs", "prise_type_chademo"]
    prises = df[prise_cols].sum().sort_values(ascending=False)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.barplot(x=prises.values, y=prises.index, palette="coolwarm", ax=ax2)
    ax2.set_title("Nombre de points de recharge par type de prise")
    ax2.set_xlabel("Nombre de prises")
    ax2.set_ylabel("Type de prise")
    st.pyplot(fig2)

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
    st.title("Trouver la borne la plus proche et un itinéraire en saisissant une adresse")

    user_coords = None

    address = st.text_input("Entrez une adresse pour définir votre localisation :")

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
    df = pd.read_csv('data/raw_data.csv', sep=';')
    df = prepare_data(df)
    page = st.sidebar.selectbox("Navigation", ["Présentation", "Data analyse", "Recherche de bornes par adresse"])

    if page == "Présentation":
        page_accueil(df)
    elif page == "Data analyse":
<<<<<<< HEAD
        page_data_analyse(df)    
    elif page == "Recherche de bornes":
        page_recherche(df)
=======
        page_data_analyse(df)
    elif page == "Recherche de bornes par adresse":
        page_recherche_adresse(df)
>>>>>>> e614677bc246cebbd8bdf1e2f3320db02b0aafae
