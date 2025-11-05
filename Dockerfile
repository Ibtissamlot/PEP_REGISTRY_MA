# Utiliser une image Python officielle comme base
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt et installer les dépendances
# Note: Les dépendances PNL doivent être installées ici
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installer le modèle spaCy français
RUN python -m spacy download fr_core_news_sm

# Copier le reste du code de l'application
COPY pep_registry /app/pep_registry

# Définition du répertoire de travail pour que Python puisse trouver les modules
WORKDIR /app/pep_registry

# Exposer le port de l'API
EXPOSE 8000

# Commande par défaut pour lancer l'API
# Utiliser Gunicorn avec Uvicorn workers pour la production
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
