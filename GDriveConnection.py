import base64
import io
import json

import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload


class GDriveConnection:
    SCOPES = ['https://www.googleapis.com/auth/drive']
    service = None
    files = None
    gspread_service = None

    def __init__(self, json_content=None, json_filename=None):
        """
        Init the connection with the json or the json file
        :param json_content: json content directly
        :param json_filename: json filename
        """
        if json_content is not None:
            credentials = service_account.Credentials.from_service_account_info(json_content, scopes=self.SCOPES)
        elif json_filename is not None:
            credentials = service_account.Credentials.from_service_account_file(json_filename, scopes=self.SCOPES)
        else:
            raise AttributeError("Need to have json_cred or json_file_name")

        self.service = build('drive', 'v3', credentials=credentials)

        self.gspread_service = gspread.authorize(credentials)

        # Call the Drive v3 API
        results = self.service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        self.files = results.get('files', [])
        if len(self.files) > 0:
            print("GDrive connected")
        else:
            raise ConnectionError("Error with GDrive connection. Please check your json file.")

    def get_byte_file(self, name):
        """
        Load a GDrive byte file
        :param name: name of the file in GDrive
        :return: the bytefile decoded (as string)
        """
        file_id = self.get_id(name)
        if file_id is None:
            return None, None

        request = self.service.files().get_media(fileId=file_id)
        file_handle = io.BytesIO()
        downloader = MediaIoBaseDownload(file_handle, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        filevalue = file_handle.getvalue()
        if not isinstance(filevalue, str):
            filevalue = base64.b64decode(filevalue)
        return file_id, filevalue

    def get_sheet_file(self, name):
        """
        Load a GDrive sheet file using a external library
        :param name: name of the file
        :return: the sheet in a list format
        """
        return self.gspread_service.open(name).sheet1.get_all_records()

    def save_byte_file(self, content, file_id, filename="results"):
        """
        Save byte file in Gdrive.
        :param content: the content of the file (string)
        :param file_id: the file id if file exist
        :param filename: the filename if fileid does not exist
        """
        mime_type = "text/json"
        data = io.BytesIO(base64.b64encode(json.dumps(content).encode()))
        media = MediaIoBaseUpload(data, mimetype=mime_type)
        if file_id is not None:
            self.service.files().update(
                body={'mimeType': mime_type},
                fileId=file_id,
                media_mime_type=mime_type,
                media_body=media).execute()
        else:
            file_metadata = {
                "name": filename,
                "mimeType": mime_type,
            }
            file = self.service.files().create(body=file_metadata,
                                               media_body=media,
                                               fields="id, name").execute()
            print("Uploaded File '{}' with ID: {}".format(file.get("name"), file.get("id")))

    def get_id(self, name):
        """
        get the id given a name of a Gdrive file
        :param name: the name searched
        :return: the id as a string, or None if no match
        """
        matches = [file['id'] for file in self.files if file['name'] == name]
        if len(matches) > 0:
            return matches[0]
        else:
            return None
