# Importer les bibliothèques nécessaires
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import seaborn as sns

# Charger les données
st.title("Points de Recharge pour Véhicules Électriques à Paris")
st.write("Recherchez et explorez les points de recharge pour véhicules électriques dans Paris.")

# Remplacer ce code par le chemin de votre fichier CSV
data = pd.read_csv("C:\\Users\\lamou\\Downloads\\M2_MOSEF_S1\\Linux\\Projet_linux\\app_api_paris\\data\\raw_data.csv", sep=';')

# Extraire latitude et longitude de la colonne coordonneesxy si elle existe
if 'coordonneesxy' in data.columns:
    # Séparation de la colonne 'coordonneesxy' en 'latitude' et 'longitude'
    data[['latitude', 'longitude']] = data['coordonneesxy'].str.split(',', expand=True)
    
    # Convertir en type float
    data['latitude'] = data['latitude'].astype(float)
    data['longitude'] = data['longitude'].astype(float)

    # Graphique 1 : Répartition des Points de Recharge par Arrondissement
    st.subheader("Répartition des Points de Recharge par Arrondissement")
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.countplot(data=data, x="arrondissement", palette="viridis", order=data["arrondissement"].value_counts().index, ax=ax1)
    ax1.set_title("Nombre de Points de Recharge par Arrondissement")
    ax1.set_xlabel("Arrondissement")
    ax1.set_ylabel("Nombre de Points")
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
    st.pyplot(fig1)

    # Graphique 2 : Types de Prises Disponibles
    st.subheader("Types de Prises Disponibles")
    prise_cols = ["prise_type_ef", "prise_type_2", "prise_type_combo_ccs", "prise_type_chademo"]
    prises = data[prise_cols].sum().sort_values(ascending=False)
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    sns.barplot(x=prises.values, y=prises.index, palette="coolwarm", ax=ax2)
    ax2.set_title("Nombre de Points de Recharge par Type de Prise")
    ax2.set_xlabel("Nombre de Prises")
    ax2.set_ylabel("Type de Prise")
    st.pyplot(fig2)



else:
    st.error("Le fichier CSV doit contenir une colonne 'coordonneesxy' avec les coordonnées.")

# Vérifier les coordonnées extraites
st.subheader("Aperçu des Données avec Coordonnées")
st.write(data[['nom_station', 'adresse_station', 'latitude', 'longitude']].head())

# Filtrage des données (exemple de filtre par arrondissement)
st.sidebar.header("Filtres")
arrondissement = st.sidebar.selectbox("Choisissez l'arrondissement", options=data["arrondissement"].unique())
data_filtered = data[data["arrondissement"] == arrondissement]

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
