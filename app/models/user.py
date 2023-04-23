from app import db
from wtforms import Form, StringField
from wtforms.validators import *


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)
    username = db.Column("username", db.String)
    password = db.Column("password", db.String)
    firstname = db.Column("firstname", db.String)
    lastname = db.Column("lastname", db.String)
    profile_image = db.Column("profile_image", db.String)

    def get_id(self):
        return str(self.id)

    def get_name(self):
        return str(self.username)

    def get_photo(self):
        return self.profile_image

    def _asdict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'profile_image': self.profile_image
        }


class PasswordForm(Form):
    confirm_password = StringField('Confirm password', [InputRequired()])
    password = StringField('New Password', [InputRequired(), EqualTo('confirm_password', message='Passwords confirmation does not match')])


class ChangePasswordForm(Form):
    oldpassword = StringField('Old password', [InputRequired()])
    confirmpassword = StringField('Confirm password', [InputRequired()])
    newpassword = StringField('New Password', [InputRequired(), EqualTo('confirmpassword', message='Passwords confirmation does not match')])


class UserRegisterForm(Form):
    username = StringField('Username', [InputRequired()])
    firstname = StringField('Firstname', [InputRequired()])
    lastname = StringField('Lastname', [])
    password = StringField('Password', [InputRequired()])
    confirm_password = StringField('Confirm password', [InputRequired(), EqualTo('password', message='Passwords confirmation does not match')])
    profile_image = StringField('Profile Image', [InputRequired()])


class UserAccountEditForm(Form):
    firstname = StringField('Firstname', [InputRequired()])
    lastname = StringField('Lastname', [])
    profile_image = StringField('Profile Image', [InputRequired()])
