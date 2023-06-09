from flask import Blueprint
from datetime import timedelta
from app import config, jsonify, request
from ..helpers.http_errors import InternalServerError, BadRequest
from ..helpers.jsonmultidict import get_json_multidict
from ..helpers.utils import PasswordUtils, FileUtils, ValidationUtils
from flask_jwt_extended import create_access_token
from ..models.user import *


Auth_blueprint = Blueprint('index', __name__)


# create user auth token
def generate_user_token(user):
    user_id = user.id
    expires_in = config.JWT_DURATION
    expires = timedelta(minutes=expires_in) # jwt lifetime duration
    token = create_access_token(identity=user_id, expires_delta=expires)
    return token


# Return user login data
def get_user_login_data(user):
    token = generate_user_token(user)
    return dict(token=token)


# Authenticate and return user login data
@Auth_blueprint.route('/login', methods=['POST'])
def login():
    try:
        username = request.body['username']
        password = request.body['password']
        query = User.query
        query = query.filter(User.username == username)
        user = query.first()
        if not user:
            return BadRequest("Username or password not correct") # username incorrect
        
        if not PasswordUtils.check_password(user.password, password):
            return BadRequest("Username or password not correct") # password incorrect

        return jsonify(get_user_login_data(user))
    except Exception as ex:
        return InternalServerError(ex)


# Save new user record
@Auth_blueprint.route('/register', methods=['POST'])
def register():
    try:
        modeldata = get_json_multidict(request.body)

        # move uploaded file from temp directory to destination directory
        if "profile_image" in modeldata:
            file_info = FileUtils.move_uploaded_files(modeldata['profile_image'], "profile_image")
            modeldata['profile_image'] = file_info['filepath']

        form = UserRegisterForm(modeldata)
        errors = []  # form validation errors

        # validate register form data
        if not form.validate():
            errors.append(form.errors)

        if errors:
            return BadRequest(errors)

        record = User()
        form.populate_obj(record)
        hashed_password = PasswordUtils.hash_password(modeldata['password'])
        record.password = hashed_password
        record.password_history = [hashed_password]  # Store the hashed password in the password_history column

        # check if username record already exists in the database
        rec_value = str(modeldata['username'])
        rec_exist = ValidationUtils.is_unique(User, "username", rec_value)
        if rec_exist:
            return BadRequest(rec_value + " Already exist!")

        # save user records
        db.session.add(record)
        db.session.commit()
        db.session.flush()
        return jsonify(get_user_login_data(record))
    except Exception as ex:
        return InternalServerError(ex)