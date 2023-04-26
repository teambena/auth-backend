from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from .helpers import jsonmultidict as json2dict
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, current_user

app = Flask(__name__)
       
app.config.from_pyfile('config.py')
app.url_map.strict_slashes = False
CORS(app)

db = SQLAlchemy(app)

from .helpers.http_errors import InternalServerError, BadRequest, Unauthorized

def resolve_request_body():
    # Before every request, resolve `request.body` from `request.get_json()`
    if request.method == 'POST' or request.method == 'PUT':
        body = request.get_json()
        if body:
            if isinstance(body, list):
                allpost = []
                for post in body:
                    allpost.append(json2dict.get_json_multidict(post))
                request.body = allpost
            else:
                request.body = json2dict.get_json_multidict(body)
        else:
            request.body = json2dict.get_json_multidict(request.form)

app.before_request(resolve_request_body)

jwt = JWTManager(app)
from .models.user import User


@jwt.user_lookup_loader
def get_current_user(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    user = User.query.filter(User.id == identity).first()
    return user

@jwt.unauthorized_loader
def unauthorized_handler(error):
    return Unauthorized(str(error))


@jwt.invalid_token_loader
def invalid_token_callback(token):
    return Unauthorized("Invalid Token")
from .controllers.fileuploader import File_Uploader_blueprint
from .controllers.auth import Auth_blueprint
from .controllers.account import Account_blueprint
# Page controller blueprint
app.register_blueprint(File_Uploader_blueprint, url_prefix = "/api/fileuploader")
app.register_blueprint(Auth_blueprint, url_prefix = "/api/auth")
app.register_blueprint(Account_blueprint, url_prefix = "/api/account")

with app.app_context():
    db.create_all()