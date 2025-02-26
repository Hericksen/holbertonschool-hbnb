from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('places', description='Opérations sur les lieux')

# Modèle pour afficher une amenity (si nécessaire)
amenity_model = api.model('Amenity', {
    'id': fields.String(description='ID de l\'équipement'),
    'name': fields.String(description='Nom de l\'équipement')
})

# Modèle pour afficher un owner (utilisateur)
user_model = api.model('User', {
    'id': fields.String(description='ID de l\'utilisateur'),
    'first_name': fields.String(description='Prénom'),
    'last_name': fields.String(description='Nom'),
    'email': fields.String(description='Email')
})

# Adding the review model
review_model = api.model('PlaceReview', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
    'user_id': fields.String(description='ID of the user')
})

# Modèle pour la validation des données d'un lieu
place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'owner': fields.Nested(user_model, description='Owner of the place'),
    'amenities': fields.List(fields.Nested(amenity_model), description='List of amenities'),
    'reviews': fields.List(fields.Nested(review_model), description='List of reviews')
})

@api.route('/')
class PlaceList(Resource):
    @api.expect(place_model, validate=True)
    @api.response(201, 'Lieu créé avec succès')
    @api.response(400, 'Données invalides')
    def post(self):
        """Enregistrer un nouveau lieu"""
        place_data = api.payload
        try:
            place = facade.create_place(place_data)
            return place.to_dict(), 201
        except ValueError as e:
            return {"message": str(e)}, 400

    @api.response(200, 'Liste des lieux récupérée avec succès')
    def get(self):
        """Récupérer la liste de tous les lieux"""
        places = facade.get_all_places()
        return [p.to_dict() for p in places], 200

@api.route('/<string:place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Détails du lieu récupérés avec succès')
    @api.response(404, 'Lieu non trouvé')
    def get(self, place_id):
        """Récupérer les détails d'un lieu par son ID, incluant propriétaire et équipements"""
        place = facade.get_place(place_id)
        if not place:
            return {"message": "Lieu non trouvé"}, 404
        return place.to_dict(), 200

    @api.expect(place_model, validate=True)
    @api.response(200, 'Lieu mis à jour avec succès')
    @api.response(404, 'Lieu non trouvé')
    @api.response(400, 'Données invalides')
    def put(self, place_id):
        """Mettre à jour les informations d'un lieu"""
        place_data = api.payload
        try:
            updated_place = facade.update_place(place_id, place_data)
            if not updated_place:
                return {"message": "Lieu non trouvé"}, 404
            return updated_place.to_dict(), 200
        except ValueError as e:
            return {"message": str(e)}, 400
