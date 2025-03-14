from flask_restx import Namespace, Resource
from flask_jwt_extended import (jwt_required, get_jwt_identity)

api = Namespace('protected', description='Protected operations')


@api.route('')
class Protected(Resource):
    @jwt_required()
    def get(self):
        """A protected endpoint that requires a valid JWT token"""
        current_user = get_jwt_identity()
        return {'message': f'Hello, user {current_user["id"]}'}, 200
