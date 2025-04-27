from flask_restx import Namespace, Resource, fields
from flask import request
from app.services import facade

api = Namespace('reviews', description='Review operations')

review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})


@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    def post(self):
        """Register a new review"""
        try:
            data = request.json
            review_obj = facade.create_review(data)
            return {
                "Review id": str(review_obj.id),
                "text": review_obj.text,
                "rating": int(review_obj.rating),
                "user_id": str(review_obj.user.id),
                "place_id": str(review_obj.place.id)
            }, 201
        except Exception as e:
            return {'message': str(e)}, 400


    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """Retrieve a list of all reviews"""
        reviews = facade.get_all_reviews()
        return [
            {
                "Review id": str(r.id),
                "text": r.text,
                "rating": int(r.rating),
                "user_id": str(r.user.id),  # Correction ici
                "place_id": str(r.place.id)  # Correction ici
            }
            for r in reviews
        ], 200



@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    def put(self, review_id):
        """Update a review's information"""
        try:
            data = request.json
            review_obj = facade.update_review(review_id, data)
            if review_obj:
                return {"message": "Review updated successfully"}, 200
            else:
                return {'message': 'Review not found'}, 404
        except Exception as e:
            return {'message': str(e)}, 400



    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    def put(self, review_id):
        """Update a review's information"""
        try:
            data = request.json
            review_obj = facade.update_review(review_id, data)  # Met à jour la review
            if not review_obj:
                return {'message': 'Review not found'}, 404

            return {"message": "Review updated successfully"}, 200  # Bonne réponse

        except Exception as e:
            return {'message': str(e)}, 400


    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete a review"""
        review_obj = facade.get_review(review_id)  # Vérifier si la review existe
        if not review_obj:
            return {'message': 'Review not found'}, 404

        facade.delete_review(review_id)  # Supprimer la review
        return {'message': 'Review deleted successfully'}, 200


@api.route('/places/<place_id>/reviews')
class PlaceReviewList(Resource):
    def get(self, place_id):
        """Get all reviews for a specific place"""
        reviews = facade.get_reviews_by_place(place_id)

        return [
            {
                "Review id": str(r.id),
                "text": r.text,
                "rating": int(r.rating),
                "user_id": str(r.user.id),  # Correction ici
                "place_id": str(r.place.id)  # Correction ici
            }
            for r in reviews
        ], 200
