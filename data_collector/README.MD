# DATA COLLECTOR 

L'objectif ici est d'automatiser la récupération des données des bornes de recharge pour véhicules électriques disponibles via l'API Open Data Paris. Les données téléchargées sont sauvegardées localement pour une utilisation ultérieure.



"source data_collector/conf/collector.conf"

Cette ligne de code charge les paramètres de configuration définis dans le fichier collector.conf, qui est stocké dans le dossier data_collector/conf.
Les paramètres de configuration incluent des variables comme TARGET_PATH qui spécifie où les données téléchargées seront enregistrées.


Avant d’exécuter le script, configurez les paramètres dans le fichier collector.conf situé dans data_collector/conf. Les paramètres incluent :

TARGET_PATH : Le chemin où les données téléchargées seront enregistrées.


Pour lancer le processus de récupération des données, utilisez :
bash data_collector/bin/get_data.sh



