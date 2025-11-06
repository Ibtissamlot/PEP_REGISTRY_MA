import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Récupération de l'URL de connexion depuis l'environnement
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    # Erreur critique si la variable n'est pas définie
    raise ValueError("DATABASE_URL environment variable is not set. Cannot connect to database.")

# 2. Création du moteur de connexion
# Le paramètre pool_pre_ping=True aide à gérer les connexions inactives
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True
)

# 3. Création de la session de base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base pour les modèles de données (si vous utilisez SQLAlchemy ORM)
Base = declarative_base()

# Fonction utilitaire pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Note: Vous devrez peut-être ajuster ce code si votre fichier original contenait
# d'autres fonctions ou classes spécifiques à votre projet.
