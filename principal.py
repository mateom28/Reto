from __future__ import print_function
import httplib2
import os, io
import auth

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
from werkzeug.utils import secure_filename
from flask import Flask, request, url_for, redirect, render_template, session
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


app = Flask(__name__)

SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'credentials.json'
APPLICATION_NAME = 'Drive API Python Quickstart'
authInst = auth.auth(SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME)
credentials = authInst.getCredentials()

http = credentials.authorize(httplib2.Http())
drive_service = discovery.build('drive', 'v3', http=http)


def moverArchivo(file_id):
    folder_id = '1M86vcbwKG-70oh4LpuTGDSWPy9nTBvWa'
    file = drive_service.files().get(fileId=file_id,
                                    fields='parents').execute()
    previous_parents = ",".join(file.get('parents'))
    file = drive_service.files().update(fileId=file_id,
                                        addParents=folder_id,
                                        removeParents=previous_parents,
                                        fields='id, parents').execute()

@app.route('/')
def principal():
    return render_template("formulario.html")


def subirArchivo(filename,filepath,mimetype):
    file_metadata = {'name': filename}
    media = MediaFileUpload(filepath,
                            mimetype=mimetype)
    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    print('File ID: %s' % file.get('id'))
    moverArchivo(file.get('id'))
    return render_template("formulario.html")

@app.route('/carpeta/<name>')
def crearCarpeta(name):
    file_metadata = {
    'name': name,
    'mimeType': 'application/vnd.google-apps.folder'
    }
    file = drive_service.files().create(body=file_metadata,
                                        fields='id').execute()
    print ('Folder ID: %s' % file.get('id'))
    moverArchivo(file.get('id'))
    return render_template("formulario.html")

def buscarArchivo(size,query):
    results = drive_service.files().list(
    pageSize=size,fields="nextPageToken, files(id, name)",q=query).execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(item)
            print('{0} ({1})'.format(item['name'], item['id']))


@app.route('/carpeta',methods = ['POST'])
def carpeta():
   if request.method == 'POST':
        f = request.form['carpeta']
        return redirect(url_for('crearCarpeta', name = f))

@app.route('/upload', methods = ['POST'])
def archivos():
    if request.method == 'POST':
        f = request.files['file']
        mime = f.content_type
        fname = secure_filename(f.filename)
        subirArchivo(fname, fname, mime)
        return redirect(url_for('principal'))
        

if __name__ == "__main__":
    app.run(debug=True)