import dropbox
from app import Config
import os
from app.settings import DRPBOX_TOKEN

# Dropboxクライアントを初期化
dbx = dropbox.Dropbox(DRPBOX_TOKEN)

basepath = os.path.join(Config.MOVIE_FOLDER)

class DropboxClass:
    def upload(filename=None):
        if filename:
            try:
                with open(os.path.join(basepath, "original", filename), 'rb') as file:
                    dbx.files_upload(file.read(), "/" + filename)
                return True
            except Exception:
                return False

    def download(filename=None):
        if filename:
            try:
                dbx.files_download_to_file(os.path.join(basepath, "original", filename), "/" + filename)
                return True
            except Exception:
                return False