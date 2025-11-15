#!/bin/bash

# Se déplacer dans le répertoire de travail
cd /app

# Exécuter le script ETL avec le bon PYTHONPATH
PYTHONPATH=. /usr/local/bin/python src/etl/pep_etl.py
