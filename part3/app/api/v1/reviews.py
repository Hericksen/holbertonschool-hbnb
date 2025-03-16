from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import facade

api = Namespace('reviews', description='Review operations')

review_model = api.model('Review', {
    'text': fields.String(required=True, description='Review text'),
    'rating': fields.Integer(required=True, description='Rating for the place (1-5)'),
    'place_id': fields.String(required=True, description='ID of the place')
})


@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """
        Create a new review.
        """
        current_user = get_jwt_identity()
        data = request.json
        data['user_id'] = current_user["id"]

        try:
            review_obj = facade.create_review(data)
            return {
                "id": review_obj.id,
                "text": review_obj.text,
                "rating": review_obj.rating,
                "user_id": review_obj.user.id,
                "place_id": review_obj.place.id
            }, 201
        except Exception as e:
            return {'message': str(e)}, 400

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """
        Retrieve a list of all reviews.
        """
        reviews = facade.get_all_reviews()
        return [
            {
                "id": r.id,
                "text": r.text,
                "rating": r.rating,
                "user_id": r.user.id,
                "place_id": r.place.id
            }
            for r in reviews
        ], 200


@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """
        Retrieve review details by ID.
        """
        review_obj = facade.get_review(review_id)
        if review_obj:
            return {
                "id": review_obj.id,
                "text": review_obj.text,
                "rating": review_obj.rating,
                "user_id": review_obj.user.id,
                "place_id": review_obj.place.id
            }, 200
        return {'message': 'Review not found'}, 404

    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def put(self, review_id):
        """
        Update a review's information.
        """
        current_user = get_jwt_identity()
        review_obj = facade.get_review(review_id)
        if not review_obj:
            return {'message': 'Review not found'}, 404

        is_admin = current_user.get('is_admin', False)
        if not (is_admin or review_obj.user.id == current_user["id"]):
            return {'message': 'Unauthorized action'}, 403

        data = request.json
        try:
            review_obj = facade.update_review(review_id, data)
            if review_obj:
                return {
                    "id": review_obj.id,
                    "text": review_obj.text,
                    "rating": review_obj.rating,
                    "user_id": review_obj.user.id,
                    "place_id": review_obj.place.id
                }, 200
            else:
                return {'message': 'Review not found'}, 404
        except Exception as e:
            return {'message': str(e)}, 400

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def delete(self, review_id):
        """
        Delete a review.
        """
        current_user = get_jwt_identity()
        review_obj = facade.get_review(review_id)
        if not review_obj:
            return {'message': 'Review not found'}, 404

        is_admin = current_user.get('is_admin', False)
        if not (is_admin or review_obj.user.id == current_user["id"]):
            return {'message': 'Unauthorized action'}, 403

        review_obj = facade.delete_review(review_id)
        if review_obj:
            return {'message': 'Review deleted successfully'}, 200
        return {'message': 'Review not found'}, 404
