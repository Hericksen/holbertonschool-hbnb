class Storage:
    """Gestionnaire de stockage des objets en mémoire"""
    objects = {}  # Dictionnaire des objets {id: instance}

    @classmethod
    def add(cls, obj):
        """Ajoute un objet au stockage"""
        cls.objects[obj.id] = obj

    @classmethod
    def get(cls, obj_id):
        """Récupère un objet par son ID"""
        return cls.objects.get(obj_id, None)

    @classmethod
    def delete(cls, obj_id):
        """Supprime un objet du stockage"""
        if obj_id in cls.objects:
            del cls.objects[obj_id]

    @classmethod
    def all(cls):
        """Renvoie tous les objets stockés"""
        return cls.objects.values()
