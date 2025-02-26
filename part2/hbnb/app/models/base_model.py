import uuid
from datetime import datetime


class BaseModel:
    """Classe de base pour gérer l'identifiant unique et les timestamps."""

    def __init__(self):
        self.id = str(uuid.uuid4())  # Génère un UUID unique
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self):
        """Met à jour la date de modification."""
        self.updated_at = datetime.now()

    def update(self, data):
        """Mise à jour des attributs à partir d’un dictionnaire."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()  # Mise à jour du timestamp
