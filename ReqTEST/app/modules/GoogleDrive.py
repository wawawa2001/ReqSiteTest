from flask import send_file
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2.service_account import Credentials
import os
from app import Config

class GoogleDriveClass:
    def __init__(self):
        # 認証情報から service オブジェクトを作成
        creds = Credentials.from_service_account_file(
            Config.GOOGLE_DRIVE_CREDENTIALS_PATH,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        self.service = build('drive', 'v3', credentials=creds)
        self.basepath = os.getcwd()  # 現在の作業ディレクトリを基準パスに設定

    def upload(self, filename=None):
        print("==========")
        print(filename)
        """
        指定したファイルを Google Drive にアップロードする。
        :param filename: アップロードするファイル名
        :return: 成功時は True、失敗時は False
        """
        if not filename:
            print("No filename provided")
            return False

        try:
            # ファイルパスを生成
            file_path = os.path.join(Config.MOVIE_FOLDER, "original", filename)
            if not os.path.exists(file_path):
                print(f"File {file_path} does not exist.")
                return False

            # メタデータとアップロード準備
            file_metadata = {
                'name': filename,
                'parents': [Config.GOOGLE_DRIVE_FOLDER_ID]
                }
            media = MediaFileUpload(file_path, resumable=True)

            # Google Drive にアップロード
            print(f"Uploading file: {file_path}")
            response = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            # 成功時のログ
            print(f"Upload successful. File ID: {response.get('id')}")
            os.remove(file_path)  # 元のファイルを削除
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error uploading file: {e}")
            return False

    def download(self, filename):
        """
        指定したファイル名のファイルを Google Drive からダウンロードする。
        :param filename: ダウンロードするファイル名
        :return: 成功時は True、失敗時は False
        """
        if not filename:
            print("No filename provided")
            return False

        try:
            # Google Drive 内でファイルを検索
            print(f"Searching for file: {filename} in Google Drive folder ID: {Config.GOOGLE_DRIVE_FOLDER_ID}")
            query = f"name='{filename}' and '{Config.GOOGLE_DRIVE_FOLDER_ID}' in parents and trashed=false"
            response = self.service.files().list(q=query, spaces='drive', fields='files(id, name)', pageSize=1).execute()
            files = response.get('files', [])

            if not files:
                print(f"File {filename} not found in the specified Google Drive folder.")
                return False

            file_id = files[0]['id']  # ファイル ID を取得
            print(f"File found: {filename} (ID: {file_id})")

            # 保存先を決定（アップロードと同じフォルダ）
            save_to = os.path.join(Config.MOVIE_FOLDER, "original", filename)
            os.makedirs(os.path.dirname(save_to), exist_ok=True)  # ディレクトリがない場合は作成

            print(f"Downloading file to: {save_to}")

            # ダウンロード処理
            request = self.service.files().get_media(fileId=file_id)
            with open(save_to, 'wb') as file:
                downloader = MediaIoBaseDownload(file, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Download progress: {int(status.progress() * 100)}%")

            print("Download completed successfully.")
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error downloading file: {e}")
            return False
