import uuid
from datetime import datetime

class BaseModel:
    def __init__(self):
        self.id = str(uuid.uuid4())  # UUID pour un identifiant unique
        self.created_at = datetime.now()
        self.updated_at = self.created_at

    def save(self):
        """Met à jour le timestamp updated_at lorsque l'objet est modifié"""
        self.updated_at = datetime.now()

    def update(self, data):
        """Met à jour les attributs de l'objet en fonction des nouvelles valeurs"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()  # Mise à jour du timestamp updated_at
