from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import facade
from config import DevelopmentConfig

api = Namespace('users', description='User operations')

# Model for user registration
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='User first name'),
    'last_name': fields.String(required=True, description='User last name'),
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'admin_secret': fields.String(required=False, description='Secret to create an admin account')
})


@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered or invalid input data')
    def post(self):
        """
        Self-registration: Create a new user.
        """
        user_data = api.payload
        admin_secret = user_data.pop('admin_secret', None)
        if admin_secret and admin_secret == DevelopmentConfig.ADMIN_SECRET:
            user_data['is_admin'] = True
        else:
            user_data['is_admin'] = False

        try:
            new_user = facade.create_user(user_data)
            return {
                'id': new_user.id,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'email': new_user.email,
                'is_admin': new_user.is_admin
            }, 201
        except Exception as e:
            return {'error': str(e)}, 400

    @api.response(200, 'List of users retrieved successfully')
    @jwt_required()
    def get(self):
        """
        Retrieve the list of all users.
        """
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        users = facade.get_all_users()
        return users, 200


@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """
        Retrieve user details by ID.
        """
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_admin': user.is_admin
        }, 200

    @api.expect(user_model)
    @api.response(200, 'User updated successfully')
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, user_id):
        """
        Update an user's own details.
        """
        current_user = get_jwt_identity()
        if current_user['id'] != user_id and not current_user.get('is_admin', False):
            return {'message': 'Unauthorized action'}, 403

        user_data = api.payload
        user_data.pop('admin_secret', None)
        try:
            updated_user = facade.update_user(user_id, user_data)
            if not updated_user:
                return {'error': 'User not found'}, 404
            return {
                'id': updated_user.id,
                'first_name': updated_user.first_name,
                'last_name': updated_user.last_name,
                'email': updated_user.email
            }, 200
        except Exception as e:
            return {'error': str(e)}, 400

    @api.response(200, 'User deleted successfully')
    @api.response(404, 'User not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def delete(self, user_id):
        """
        Delete an user account.
        """
        current_user = get_jwt_identity()
        if current_user['id'] != user_id and not current_user.get('is_admin', False):
            return {'message': 'Unauthorized action'}, 403

        try:
            deleted_user = facade.delete_user(user_id)
            if not deleted_user:
                return {'error': 'User not found'}, 404
            return {'message': 'User deleted successfully'}, 200
        except Exception as e:
            return {'error': f'Error deleting user: {str(e)}'}, 500
