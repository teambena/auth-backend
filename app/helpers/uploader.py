import os
import time
import uuid
from app import config
from PIL import Image
from flask import request

app_root = config.APP_ROOT
assets_dir = config.ASSETS_DIR
app_static_dir = config.APP_STATIC


class Uploader:
    upload_setting = dict()
    upload_dir = None
    temp_dir = None
    uploaded_files = None
    field = None

    def __init__(self, files, field):
        self.field = field

        if field not in config.UPLOAD_SETTINGS:
            raise Exception(f'Upload settings not found for {field}')

        self.upload_setting = config.UPLOAD_SETTINGS[field]

        self.uploaded_files = files
        self.upload_dir = self.upload_setting.get('upload_dir', '')
        self.temp_dir = os.path.join(assets_dir, config.UPLOAD_TEMP_DIR)

    def upload(self):
        upload_setting = self.upload_setting
        uploaded_files = self.uploaded_files

        max_files = upload_setting['limit']
        if len(uploaded_files) > max_files:
            raise Exception(f'Maximum of {max_files} files is allowed')

        allowed_exts = str(upload_setting['extensions']).replace(' ', '').split(',')

        if 'max_file_size' in upload_setting:
            max_file_size = float(upload_setting['max_file_size']) * 1024 * 1024
            config.MAX_CONTENT_LENGTH = max_file_size

        filename_prefix = upload_setting.get('filename_prefix', '')

        self.make_dir(self.temp_dir)  # create directory if not exist

        uploaded_file_paths = []
        index = 0

        for file in uploaded_files:
            index += 1
            if file.filename == '':
                raise Exception('Invalid file name')

            file_ext = file.filename.rsplit('.', 1)[1].lower()
            if not file_ext in allowed_exts:
                raise Exception('file extension not allowed')

            filename = self.get_filename(file, index)
            new_filename = filename_prefix + filename + '.' + file_ext

            file_path = os.path.join(self.temp_dir, new_filename)

            file_full_path = os.path.join(app_root, file_path)  # need full path to save file
            file.save(file_full_path)

            file_path = file_path.replace('\\', '/')
            uploaded_file_paths.append(file_path)
        return ",".join(uploaded_file_paths)

    # move uploaded files from temp directory to another directory
    def move_uploaded_files(self):
        arr_files = self.uploaded_files.split(",")
        uploaded_files = []
        for file in arr_files:
            moved_file = self.move_file(file)
            uploaded_files.append(moved_file)
        return ','.join(uploaded_files)

    # move file from temp directory to upload directory
    def move_file(self, file):
        tmp_file = os.path.join(app_root, file)
        if os.path.exists(tmp_file):
            filename = os.path.basename(file)
            new_file = os.path.join(app_root, assets_dir, self.upload_dir, filename)
            os.rename(tmp_file, new_file)

            if self.is_image(new_file):
                self.resize_image(new_file)

            new_file_path = os.path.join(assets_dir, self.upload_dir, filename)  # get relative file path
            new_file_path = new_file_path.replace('\\', '/')
            return_full_path = self.upload_setting.get('return_full_path', False)

            if return_full_path:
                new_file_path = request.host_url + new_file_path  # return the aboslute url of the uploaded file

            return new_file_path
        return file

    # get file name use to save the uploaded files
    def get_filename(self, file, index):
        filename_type = self.upload_setting.get('filename_type', "random")
        filename = ""
        if filename_type == 'date':
            filename = time.strftime("%Y-%m-%d-%H-%M-%S") + "-" + str(index)
        elif filename_type == 'timestamp':
            filename = str(int(time.time())) + "-" + str(index)
        elif filename_type == 'original':
            filename = os.path.splitext(file.filename)[0]
        elif filename_type == 'filecount':
            cwd = os.path.join(app_root, self.upload_dir)
            filename = str(len(os.listdir(cwd)) + 1)
        else:
            filename = str(uuid.uuid4())
        return filename

    # create new directory if not exist
    def make_dir(self, dir_name):
        full_dir = os.path.join(app_root, dir_name)
        if not os.path.exists(full_dir):
            os.makedirs(full_dir)

    # check if file is an image
    def is_image(self, file_path):
        img_extensions = ["png", "jpg", "jpeg", "jpg", "gif"]
        file_ext = file_path.rsplit('.', 1)[1].lower()
        if file_ext in img_extensions:
            return True
        return False

    # resize and save images using different sizes
    def resize_image(self, img_path):
        resize_settings = self.upload_setting.get('image_resize', [])  # get image resize settings from config
        for setting in resize_settings:
            thumb_name = setting["name"]
            image = Image.open(img_path)
            original_width, original_height = image.size
            width = setting["width"] or original_width
            height = setting["height"] or original_height
            mode = setting["mode"]
            if mode == "contain":
                if original_width < width:
                    width = original_width
                if original_height < height:
                    height = original_height
                image.thumbnail((width, height))
            else:
                image = image.resize((width, height))
            thumb_dir = os.path.join(app_root, assets_dir, self.upload_dir, thumb_name)
            self.make_dir(thumb_dir)  # create directory if not exist
            file_name = os.path.basename(img_path)
            thumb_file_name = os.path.join(thumb_dir, file_name)
            image.save(thumb_file_name)
