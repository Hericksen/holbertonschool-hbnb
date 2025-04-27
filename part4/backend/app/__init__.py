from flask import Flask, render_template, send_from_directory
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

bcrypt = Bcrypt()
jwt = JWTManager()
db = SQLAlchemy()

def create_app(config_class="config.DevelopmentConfig"):
    app = Flask(__name__,
                template_folder='../../front/templates',
                static_folder='../../front/style')
    authorizations = {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    }
    api = Api(app, version='1.0',
            title='HBnB API',
            description='HBnB Application API',
            authorizations=authorizations,
            security='Bearer')
    app.config.from_object(config_class)
    app.config['SECRET_KEY'] = 'your_secret_key'
    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)
    CORS(app,resources={r"/api/*": {"origins": "http://localhost:5500"}})

    from app.api.v1.users import api as users_ns
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.reviews import api as reviews_ns
    from app.api.v1.auth import api as auth_ns
    from app.api.v1.admin import api as admin_ns

    #Register the users namespace
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(admin_ns, path='/api/v1/admin')
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/<path:filename>')
    def serve_file(filename):
        if filename.endswith('.html'):
            return render_template(filename)
        return send_from_directory(app.static_folder, filename)
    
    return app
