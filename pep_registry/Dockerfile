# Utiliser une image Python officielle comme base
FROM python:3.11-slim

# Installer les dépendances système nécessaires pour la compilation des packages Python
# Inclut les outils pour PostgreSQL (libpq-dev) et les outils de scraping (libxml2-dev, libxslt1-dev)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installer le modèle spaCy français
RUN python -m spacy download fr_core_news_sm

# Copier le reste du code de l'application
COPY . /app/pep_registry

# Définition du répertoire de travail pour que Python trouve les modules
WORKDIR /app/pep_registry

# Exposer le port de l'API
EXPOSE 8000

# Commande de démarrage de l'API (Utilisation de Gunicorn pour la production)
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "src.api.main:app", "-b", "0.0.0.0:8000"]
