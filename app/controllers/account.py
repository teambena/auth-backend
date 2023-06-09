from flask import Blueprint
from app import jsonify, request, jwt_required, current_user
from ..helpers.http_errors import InternalServerError, BadRequest, ResourceNotFound
from ..helpers.utils import FileUtils, PasswordUtils
from ..models.user import *


Account_blueprint = Blueprint('account', __name__)


@Account_blueprint.route('/')
@Account_blueprint.route('/index')
@jwt_required()
def view():
    try:
        rec_id = current_user.id
        query = User.query.filter(User.id == rec_id)
        query = query.with_entities(
            User.id,
            User.username,
            User.firstname,
            User.lastname
        )
        
        record = query.first()
        if not record: return ResourceNotFound()
         
        record = record._asdict()
        
        return jsonify(record)
    except Exception as ex:
        return InternalServerError(ex)


@Account_blueprint.route('/edit', methods=['GET', 'POST'])
@jwt_required()
def edit():
    try:
        rec_id = current_user.id
        record = User.query.filter(User.id == rec_id).first()
        if not record: return ResourceNotFound()
        
        if request.method == 'POST':
            modeldata = request.body
            
            # move uploaded file from temp directory to destination directory
            if "profile_image" in modeldata:
                file_info = FileUtils.move_uploaded_files(modeldata['profile_image'], "profile_image")
                modeldata['profile_image'] = file_info['filepath']
            
            errors = []
            form = UserAccountEditForm(modeldata, obj=record)
            
            if not form.validate():
                errors.append(form.errors)
            
            if errors:
                return BadRequest(errors)
            
            # save User record
            form.populate_obj(record)
            db.session.commit()
         
        record = record._asdict()
        return jsonify(record)
    except Exception as ex:
        return InternalServerError(ex)


@Account_blueprint.route('/currentuserdata')
@jwt_required()
def currentuserdata():
    user = current_user._asdict()
    del user['password']
    return jsonify(user)

@Account_blueprint.route('/resetpassword', methods=['POST'])
@jwt_required()
def resetpassword():
    try:
        rec_id = current_user.id
        record = User.query.filter(User.id == rec_id).first()
        if not record:
            return ResourceNotFound()

        modeldata = request.body

        errors = []
        form = PasswordForm(modeldata)

        if not form.validate():
            errors.append(form.errors)

        if errors:
            return BadRequest(errors)

        password = modeldata['password']
        password_history = record.password_history if record.password_history else []

        if PasswordUtils.check_password_history(password, password_history, 5):
            return BadRequest("New password must not be the same as the last 5 passwords used.")

        # Save the new password and update the password history
        record.password = PasswordUtils.hash_password(password)
        new_password_history = password_history.copy()
        new_password_history.append(PasswordUtils.hash_password(password))  # Store the hashed password in the history
        new_password_history = new_password_history[-5:]
        record.password_history = new_password_history

        db.session.commit()

        return jsonify({"message": "Password reset successfully."})
    except Exception as ex:
        return InternalServerError(ex)