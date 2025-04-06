from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from flask import request
from app.services import facade

api = Namespace('amenities', description='Amenity operations')

# Define the amenity model using Flask-RESTX's model feature
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})

@api.route('/')
class AmenityList(Resource):
    @jwt_required()
    @api.expect(amenity_model, validate=True)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    def post(self):
        """Register a new amenity"""
        if not facade.is_admin():
            return {"error": "Admin privileges required"}, 403
        amenity_data = api.payload
        try:
            new_amenity = facade.create_amenity(amenity_data)
            return {
                'id': new_amenity.id,
                'name': new_amenity.name
            }, 201
        except ValueError as e:
            return {'message': str(e)}, 400

    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """Retrieve the list of all amenities"""
        amenities = facade.get_all_amenities()
        return [
            {
                'id': a.id,
                'name': a.name
            }
            for a in amenities
        ], 200


@api.route('/<amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get amenity details by ID"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return {
            'id': amenity.id,
            'name': amenity.name
        }, 200

    @jwt_required()
    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    def put(self, amenity_id):
        """Update an amenity's information"""
        if not facade.is_admin():
            return {"error": "Admin privileges required"}, 403
        amenity_data = api.payload
        try:
            updated_amenity = facade.update_amenity(
                amenity_id, amenity_data)
            if not updated_amenity:
                return {'error': 'Amenity not found'}, 404
            return {
                'id': updated_amenity.id,
                'name': updated_amenity.name
            }, 200
        except ValueError as e:
            return {'message': str(e)}, 400
