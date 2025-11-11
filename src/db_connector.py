import psycopg2
from psycopg2 import extras
from src.config import DB_CONFIG

class DBConnector:
    """Gère la connexion et les opérations de base de données."""
    
    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(cursor_factory=extras.RealDictCursor)
            return self
        except psycopg2.OperationalError as e:
            print(f"Erreur de connexion à la base de données: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()

    def execute(self, query, params=None, fetch=False):
        """Exécute une requête SQL."""
        self.cursor.execute(query, params)
        if fetch:
            return self.cursor.fetchall()
        return None
