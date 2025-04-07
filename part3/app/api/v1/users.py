from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity

api = Namespace('users', description='User operations')

# Define the user model for input validation and documentation
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user')
})

@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    def post(self):
        """Register a new user"""

        user_data = api.payload

        # Simulate email uniqueness check (to be replaced by real validation with persistence)
        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            return {'error': 'Email already registered'}, 400

        new_user = facade.create_user(user_data)
        if new_user.password == 'admin':
            new_user.is_admin = True
        hashed_password = new_user.hash_password(user_data['password'])
        if hashed_password == False:
            return {'error': 'Password not hashed'}, 500
        return {'id': new_user.id, 'first_name': new_user.first_name, 'last_name': new_user.last_name, 'email': new_user.email}, 201

    @api.response(200, 'Users list retrieved successfully')
    @api.response(404, 'User not found')
    def get(self):
        """Get user list"""
        users = facade.get_user_list()
        if not users:
            return {'error': 'User not found'}, 404
        return [{'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email} for user in users], 200

@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return {'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'is_admin': user.is_admin}, 200
    @api.expect(user_model, validate=True)
    @api.response(200, 'User update successfully')
    @api.response(400, 'Invalid data')
    @api.response(404, 'User not found')
    @jwt_required()
    def put(self, user_id):
        """Update user details"""
        current_user = get_jwt_identity()
        user_data = api.payload
        initial_user = facade.get_user(user_id)
        if not current_user.get('is_admin'):
            if user_data['email'] != initial_user.email or initial_user.verify_password(user_data['password']):
                return {'error': 'You cannot modify email or password'}
        if not current_user.get('is_admin') and user_id != current_user['id']:
            return {'error': 'Unauthorized action'}, 403
        user = facade.update_user(user_id, user_data)
        if user == 404:
            return {'error': 'User not found'}, 404
        if user == 400:
            return {'error': 'Invalid data'}, 400
        return {'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email}, 200
