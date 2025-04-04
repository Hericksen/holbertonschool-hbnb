from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('users', description='User operations')

# Define the user model for input validation and documentation
user_model = api.model('User', {
    'first_name': fields.String(required=True,
                                description='First name of the user'),
    'last_name': fields.String(required=True,
                               description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True,
                              description='Password of the user')
})


@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new user"""
        user_data = api.payload

        # Simulate email uniqueness check (to be replaced by real validation
        #  with persistence)
        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            return {'error': 'Email already registered'}, 400

        new_user = facade.create_user(user_data)
        return {
            'id': new_user.id,
            'message': 'User successfully registered'
        }, 201


@api.route('/<string:user_id>')
class UserResource(Resource):
    @api.response(404, 'User not found')
    @api.response(200, 'User details retrieved successfully')
    def get(self, user_id):
        """Fetch the details of a user using their ID"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        }, 200
        
    @api.expect(user_model)
    @api.response(200, 'User details updated successfully')
    @api.response(400, 'Invalid input data')
    def put(self, user_id):
        """Modify a user’s details based on their ID"""
        user_data = request.get_json()

        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        # Hash the password if provided
        if 'password' in user_data:
            password = user_data.pop('password')  # Remove password from user data
            user_data['password'] = facade.hash_password(password)  # Hash the password

        updated_user = facade.update_user(user_id, user_data)
        if not updated_user:
            return {'error': 'User update failed'}, 500

        return {
            'id': updated_user.id,
            'first_name': updated_user.first_name,
            'last_name': updated_user.last_name,
            'email': updated_user.email
        }, 200
