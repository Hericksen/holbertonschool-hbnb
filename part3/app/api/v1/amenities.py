from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import facade

api = Namespace('amenities', description='Amenity operations')

amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})

@api.route('/')
class AmenityList(Resource):
    @api.expect(amenity_model, validate=True)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """
        Create a new amenity.
        Any authenticated user can do this.
    """
        current_user = get_jwt_identity()
        user = facade.get_user(current_user['id'])
        if not user:
            return {'message': 'User not found'}, 400

        amenity_data = api.payload
        amenity_data["owner_id"] = user.id

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
        """
        Retrieve all amenities.
        This endpoint is open to everyone.
        """
        amenities = facade.get_all_amenities()
        return [
            {
                'id': a.id,
                'name': a.name
            }
            for a in amenities
        ], 200

@api.route('/<string:amenity_id>')
@api.param('amenity_id', 'The Amenity identifier')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """
        Get details of an amenity by its ID.
        Open to everyone.
        """
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return {
            'id': amenity.id,
            'name': amenity.name
        }, 200

    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def put(self, amenity_id):
        """
        Update an amenity's information.
        Any authenticated user can do this.
        """
        current_user = get_jwt_identity()
        user = facade.get_user(current_user['id'])
        if not user:
            return {'message': 'User not found'}, 400

        amenity_data = api.payload
        try:
            updated_amenity = facade.update_amenity(amenity_id, amenity_data)
            if not updated_amenity:
                return {'error': 'Amenity not found'}, 404
            return {
                'id': updated_amenity.id,
                'name': updated_amenity.name
            }, 200
        except ValueError as e:
            return {'message': str(e)}, 400

    @api.response(200, 'Amenity deleted successfully')
    @api.response(404, 'Amenity not found')
    @api.response(403, 'Admin access required')
    @jwt_required()
    def delete(self, amenity_id):
        """
        Delete an amenity by ID.
        The owner of the amenity or an admin can delete it.
        """
        current_user = get_jwt_identity()  # ex: {"id": "...", "is_admin": True/False}
        user = facade.get_user(current_user["id"])
        if not user:
            return {"error": "User not found"}, 400

        # Récupérer l'amenity pour vérifier le propriétaire
        amenity_obj = facade.get_amenity(amenity_id)
        if not amenity_obj:
            return {"error": "Amenity not found"}, 404

        # Vérifier si l'utilisateur est admin ou propriétaire de l'amenity
        # => Pour cela, Amenity doit avoir un champ amenity_obj.owner_id ou un attribut amenity_obj.owner
        if not (user.is_admin or amenity_obj.owner_id == user.id):
            return {"error": "Unauthorized action"}, 403

        success = facade.delete_amenity(amenity_id)
        if success:
            return {"message": "Amenity deleted successfully"}, 200
        else:
            return {"error": "Amenity not found"}, 404
