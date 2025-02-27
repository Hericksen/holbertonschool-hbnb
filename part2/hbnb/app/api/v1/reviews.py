# api/v1/reviews.py
from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade

# Initialisation de la façade
facade = HBnBFacade()

api_reviews = Namespace('reviews', description='Operations related to reviews')

# Définir le modèle de la critique
review_model = api_reviews.model('Review', {
    'text': fields.String(required=True, description='Review text'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})

@api_reviews.route('/')
class ReviewList(Resource):
    @api_reviews.expect(review_model)
    @api_reviews.response(201, 'Review successfully created')
    @api_reviews.response(400, 'Invalid input data')
    def post(self):
        """Register a new review"""
        try:
            review_data = api_reviews.payload
            new_review = facade.create_review(review_data)
            return new_review, 201
        except ValueError as e:
            return {"message": str(e)}, 400

    @api_reviews.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """Retrieve all reviews"""
        reviews = facade.get_all_reviews()
        return reviews, 200


@api_reviews.route('/<review_id>')
class ReviewResource(Resource):
    @api_reviews.response(200, 'Review details retrieved successfully')
    @api_reviews.response(404, 'Review not found')
    def get(self, review_id):
        """Get review details by ID"""
        try:
            review = facade.get_review(review_id)
            return review, 200
        except ValueError as e:
            return {"message": str(e)}, 404

    @api_reviews.expect(review_model)
    @api_reviews.response(200, 'Review updated successfully')
    @api_reviews.response(404, 'Review not found')
    @api_reviews.response(400, 'Invalid input data')
    def put(self, review_id):
        """Update a review's information"""
        try:
            review_data = api_reviews.payload
            updated_review = facade.update_review(review_id, review_data)
            return {"message": "Review updated successfully"}, 200
        except ValueError as e:
            return {"message": str(e)}, 400

    @api_reviews.response(200, 'Review deleted successfully')
    @api_reviews.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete a review"""
        try:
            message = facade.delete_review(review_id)
            return message, 200
        except ValueError as e:
            return {"message": str(e)}, 404


@api_reviews.route('/places/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api_reviews.response(200, 'List of reviews for the place retrieved successfully')
    @api_reviews.response(404, 'Place not found')
    def get(self, place_id):
        """Get all reviews for a specific place"""
        try:
            reviews = facade.get_reviews_by_place(place_id)
            return reviews, 200
        except ValueError as e:
            return {"message": str(e)}, 404
