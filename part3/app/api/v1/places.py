from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import facade
import uuid

api = Namespace('places', description='Place operations')

# Define the models
amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First Name of the owner'),
    'last_name': fields.String(description='Last Name of the owner'),
    'email': fields.String(description='Email of the owner'),
})

review_model = api.model('PlaceReview', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
    'user_id': fields.String(description='ID of the user')
})

place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place')
})


@api.route('/')
class PlaceList(Resource):
    @api.expect(place_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """Register a new place (authenticated users only)"""
        current_user_id = get_jwt_identity()
        place_data = api.payload
        place_data['owner_id'] = current_user_id  # force the owner to be the authenticated user

        try:
            place_obj = facade.create_place(place_data)
            return {
                "Place id": place_obj.id,
                "title": place_obj.title,
                "description": place_obj.description,
                "price": place_obj.price,
                "latitude": place_obj.latitude,
                "longitude": place_obj.longitude,
                "owner_id": place_obj.owner.id,
            }, 201
        except ValueError as e:
            return {"message": str(e)}, 400

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve all places (public)"""
        places = facade.get_all_places()
        return [
            {
                "Place id": p.id,
                "title": p.title,
                "description": p.description,
                "price": p.price,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "owner_id": p.owner.id
            }
            for p in places
        ], 200

@api.route('/<string:place_id>')
class PlaceUpdate(Resource):
    @jwt_required()
    def put(self, place_id):
        claims = get_jwt()
        current_user_id = claims.get("id")
        is_admin_user = claims.get("is_admin", False)

        place = place_repository.get(place_id)
        if not place:
            return {"error": "Place not found"}, 404
        if not is_admin_user and place.owner_id != current_user_id:
            return {"error": "Unauthorized"}, 403

        data = request.get_json()
        updated = place_repository.update(place_id, data)
        return {"message": "Place updated", "place": updated.to_dict()}

@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Retrieve a place's details by ID"""
        try:
            place_obj = facade.get_place(place_id)
            return {
                "Place id": place_obj.id,
                "title": place_obj.title,
                "description": place_obj.description,
                "price": place_obj.price,
                "latitude": place_obj.latitude,
                "longitude": place_obj.longitude,
                "owner": {
                    "id": place_obj.owner.id,
                    "first_name": place_obj.owner.first_name,
                    "last_name": place_obj.owner.last_name,
                    "email": place_obj.owner.email
                },
            }, 200
        except ValueError:
            return {"message": "Place not found"}, 404

    @api.expect(place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Forbidden: not owner')
    @jwt_required()
    def put(self, place_id):
        """Update a place (owner only)"""
        current_user_id = get_jwt_identity()
        place_data = api.payload

        try:
            existing_place = facade.get_place(place_id)
            if not existing_place:
                return {"message": "Place not found"}, 404

            if existing_place.owner.id != current_user_id:
                return {"message": "You are not the owner of this place."}, 403

            updated_place = facade.update_place(place_id, place_data)
            return {
                "Place id": updated_place.id,
                "title": updated_place.title,
                "description": updated_place.description,
                "price": updated_place.price,
                "latitude": updated_place.latitude,
                "longitude": updated_place.longitude,
                "owner_id": updated_place.owner.id,
            }, 200
        except ValueError as e:
            return {"message": str(e)}, 400

    @api.response(200, 'Place deleted successfully')
    @api.response(404, 'Place not found')
    @api.response(403, 'Forbidden: not owner')
    @jwt_required()
    def delete(self, place_id):
        """Delete a place (owner only)"""
        current_user_id = get_jwt_identity()
        try:
            existing_place = facade.get_place(place_id)
            if not existing_place:
                return {"message": "Place not found"}, 404

            if existing_place.owner.id != current_user_id:
                return {"message": "You are not the owner of this place."}, 403

            facade.delete_place(place_id)
            return {"message": "Place deleted successfully"}, 200
        except Exception as e:
            return {"message": str(e)}, 400
