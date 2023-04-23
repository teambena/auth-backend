import os
import mimetypes
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import StopValidation
from app import app
from sqlalchemy import text
from .uploader import Uploader
from wtforms.validators import ValidationError


class PasswordUtils:

    @staticmethod
    def hash_password(password_text):
        return generate_password_hash(password_text)

    @staticmethod
    def check_password(password_hash, password_text):
        try:
            return check_password_hash(password_hash, password_text)
        except:
            return False


class FileUtils:

    @staticmethod
    def move_uploaded_files(files, fieldname):
        file_info = {
            "filepath": "",
            "filesize": "",
            "filename": "",
            "filetype": "",
            "fileext": ""
        }
        if files:
            uploader = Uploader(files, fieldname)
            uploaded_files = uploader.move_uploaded_files()
            first_file = uploaded_files.split(",")[0]
            file = os.path.join(app.config['APP_ROOT'], first_file)

            file_info["filepath"] = uploaded_files

            if os.path.exists(file):
                file_info["filesize"] = os.path.getsize(file)
                file_info["filename"] = os.path.basename(file)
                file_info["fileext"] = os.path.splitext(file)[1][1:].strip().lower()
                mime = mimetypes.guess_type(file)

                if mime:
                    file_info["filetype"] = mime[0]

        return file_info


class ValidationUtils:

    @staticmethod
    def is_unique(model, field, fieldvalue, tablekey=None, recid=None):
        query = model.query
        field_filter = text(f'{field} = :fieldvalue').params(fieldvalue=fieldvalue)
        record = query.filter(field_filter).first()
        if record:
            record = record._asdict()
            if (tablekey is None or str(recid) != str(record[tablekey])):
                return True
        return False


class OptionalButNotEmpty(object):
    field_flags = ('optional',)

    def __call__(self, form, field):
        if not field.raw_data:
            raise StopValidation()


class Unique(object):
    def __init__(self, model, field, id=None, message=None):
        self.model = model
        self.field = field
        if not message:
            message = u'Already exists'
        self.message = message

    def __call__(self, form, field):
        record = self.model.query.filter(self.field == field.data).first()
        pk = None
        if '__pk__' in form and '__recid__' in form:
            pk = form.__pk__
            recid = form.__recid__
        if record and (pk is None or recid != record[pk]):
            raise ValidationError(self.message)