import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
ASSETS_DIR = 'static'
APP_STATIC = os.path.join(APP_ROOT, ASSETS_DIR)


DEBUG = True
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'sqlite+pysqlite:///D:\\auth\\auth.sqlite'

CSRF_ENABLED = True

SECRET_KEY = 'f3fc57a6f1f3794bee1c52225afbb5bd'
SECURITY_PASSWORD_SALT = '4372a6a5500bd6821be582fe0bf7ed53'
SITE_NAME = 'auth' 
SITE_ADDR = 'http://localhost:8060'
FRONTEND_ADDR = 'http://localhost:8050'

# file upload directories 
UPLOAD_DIR = 'uploads/'
UPLOAD_TEMP_DIR = 'uploads/temp/'
MAX_CONTENT_LENGTH = 16777216

JWT_DURATION = 30  # OTP Duration in minutes

# Page upload settings
UPLOAD_SETTINGS = dict(
    
    profile_image=dict(
        filename_type="original",
        extensions="jpg,png,bmp,jpeg",
        limit=1,
        max_size=5,
        return_full_path=False,
        filename_prefix="",
        upload_dir="uploads/files",
        image_resize=[ 
            dict(name="small", width=100, height=100, mode="cover"), 
            dict(name="medium", width=480, height=480, mode="contain"), 
            dict(name="large", width=1024, height=760, mode="contain")
        ],

    ),

)