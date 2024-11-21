"""
Extrait la route à partir d'un point de départ et d'un point d'arrivée
avec osrm.org
"""

import json
import subprocess

# coord de depart (latitude, longitude)
start_coords = (48.853573, 2.363958)
# coord d'arrivée (latitude, longitude)
end_coords = (48.84189, 2.333149)

# commande bash
command = (
    f"curl -X GET http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]}"
    f";{end_coords[1]},{end_coords[0]}?overview=false "
    "-H 'accept: */*' > data/route_data.json"
)
# shell=True pour exécuter la commande complète
subprocess.run(command, shell=True)

# fichier json
with open('data/route_data.json', 'r') as file:
    data = json.load(file)

print(json.dumps(data, indent=2))





