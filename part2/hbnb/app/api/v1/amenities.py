from flask_restx import Namespace, Resource, fields
from flask import request
from app.services import facade
from app.models.place import Place

api = Namespace('amenities', description='Amenity operations')

# Define the amenity model for input validation and documentation
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})

@api.route('/')
class AmenityList(Resource):

    @api.expect(amenity_model)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new amenity"""
        data = request.json
        name = data.get('name')
        if not name:
            return {'message': 'Invalid input data, name is required'}, 400
        amenity = facade.create_amenity({"name": name})
        return {'id': amenity.id, 'name': amenity.name}, 201

    @api.doc(description="Retrieve a list of all amenities. No parameters needed.")
    @api.response(200, 'List of amenities retrieved successfully')
    @api.response(404, 'No amenities found')
    def get(self):
        """Retrieve a list of all amenities"""
        amenities = facade.get_all_amenities()
        if not amenities:
            return {'message': 'No amenities found'}, 404  # Retourne une erreur 404 si la liste est vide
        return [{'id': getattr(amenity, 'id', None), 'name': getattr(amenity, 'name', None)} for amenity in amenities], 200


@api.route('/<int:amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get amenity details by ID"""
        amenity = facade.get_amenity(amenity_id)  # Correction ici
        if not amenity:
            return {'message': 'Amenity not found'}, 404
        return {'id': amenity.id, 'name': amenity.name}, 200

    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    def put(self, amenity_id):
        """Update an amenity's information"""
        data = request.json
        name = data.get('name')
        if not name:
            return {'message': 'Invalid input data, name is required'}, 400

        # Utilisation de l'ID comme UUID (chaîne)
        updated_amenity = facade.update_amenity(amenity_id, name)
        if not updated_amenity:
            return {'message': 'Amenity not found'}, 404
        return {'id': updated_amenity['id'], 'name': updated_amenity['name']}, 200
