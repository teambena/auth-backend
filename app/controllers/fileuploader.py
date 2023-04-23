import os
from flask import Blueprint, request, jsonify, make_response
from app import app
from ..helpers.uploader import Uploader
File_Uploader_blueprint = Blueprint('File_Uploader_blueprint', __name__)


@File_Uploader_blueprint.route('/upload/<fieldname>', methods=['POST'])
def upload(fieldname=None):
    try:
        if 'file' not in request.files:
            return jsonify('No file selected.'), 400
        if fieldname not in app.config["UPLOAD_SETTINGS"]:
            return jsonify('No upload setting for the field'), 400
        files = request.files.getlist('file')

        uploader = Uploader(files, fieldname)

        uploaded_file_paths = uploader.upload()
        return make_response(uploaded_file_paths)
    except Exception as ex:
        return jsonify(str(ex)), 500

@File_Uploader_blueprint.route('/remove_temp_file', methods=['POST'])
def remove_temp_file():
    try:
        file = request.body['temp_file']
        if file:
            app_root = app.config['APP_ROOT']
            app_static_dir = app.config['APP_STATIC']
            filename = os.path.basename(file)
            temp_dir = os.path.join(*[app_static_dir, app.config["UPLOAD_TEMP_DIR"]])
            full_name = os.path.join(app_root, temp_dir, filename)
            if os.path.exists(full_name):
                os.remove(full_name)
                return jsonify("File Deleted")
        return jsonify("Invalid temp file")
    except Exception as ex:
        return jsonify(str(ex)), 500