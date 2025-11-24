import sys
import os
# Ajouter le répertoire parent de 'etl' au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#!/bin/bash

# Se déplacer dans le répertoire de travail
cd /app

# Exécuter le script ETL avec le bon PYTHONPATH
PYTHONPATH=. /usr/local/bin/python src/etl/pep_etl.py
