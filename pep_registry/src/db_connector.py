import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Récupération de l'URL de connexion depuis l'environnement
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Cannot connect to database.")

# 2. Création du moteur de connexion
# Le paramètre connect_args force l'utilisation de SSL pour la connexion à Supabase
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    connect_args={"sslmode": "require"}  # <--- AJOUTEZ CETTE LIGNE
)

# 3. Création de la session de base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base pour les modèles de données
Base = declarative_base()

# 5. CLASSE MANQUANTE (ajoutée pour satisfaire l'importation dans main.py)
# Nous allons la rendre simple, car la logique de connexion est déjà dans les fonctions ci-dessus.
class DBConnector:
    """
    Classe factice pour satisfaire l'importation dans main.py.
    La logique de connexion est gérée par SessionLocal et get_db.
    """
    def __init__(self):
        pass
        # ... à la fin de pep_registry/src/db_connector.py

# Assurez-vous que tous les modèles sont liés au moteur de base de données
# Ceci est crucial pour que SQLAlchemy sache où trouver les tables.
# NOTE: Cette ligne doit être exécutée APRÈS la définition de tous vos modèles (Base.metadata)
Base.metadata.create_all(bind=engine)


# Fonction utilitaire pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Note: Si votre main.py utilise Base ou SessionLocal directement, vous n'avez pas besoin de cette classe.
# Mais pour l'instant, nous la rétablissons pour que l'importation fonctionne.

