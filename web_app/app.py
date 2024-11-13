"""
Projet Linux
M2 MoSEF

app.py
"""
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static

from mapping_utils import mapping, coord_arrondissements

# Chargement des données
df = pd.read_csv('data/raw_data.csv', sep=';')

# Titre de l'application
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


# Paris en intégralité =============================================================================================== 

map = mapping(df)
folium_static(map)

# Selection d'un arrondissement ====================================================================================== 

arrondissement = st.selectbox(
    label='Selectionner un arrondissement',
    options=sorted(df['arrondissement'].unique())
)

df_arrondissement = df[df['arrondissement'] == arrondissement]

st.markdown(f"## Points de recharge dans le {arrondissement}")
map_arrondissement = mapping(df_arrondissement, centrage = coord_arrondissements(arrondissement), zoom = 14)
folium_static(map_arrondissement)

# informations sur les bornes de l'arrondissement sélectionné
st.markdown(f"## Détails des bornes de recharge dans le {arrondissement}")
st.dataframe(df_arrondissement[['nom_station', 'adresse_station', 'statut_pdc', 'puissance_nominale']].reset_index(drop=True))
