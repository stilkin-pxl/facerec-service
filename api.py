# https://github.com/ageitgey/face_recognition/blob/master/examples/web_service_example.py
# https://flask.palletsprojects.com/en/1.1.x/quickstart/

import base64
import face_recognition
import io
import json
import numpy as np
import os
from PIL import Image
from flask import Flask, jsonify, request, redirect, send_from_directory

# constants
CONST_ERROR = 'error'
KEY_PERSON = 'person_id'
KEY_IMG = 'image'
ENC_FOLDER = 'encodings'
ENC_FILE = '.enc'

app = Flask(__name__)


### ROUTES ###

@app.route('/')
def index_route():
    return jsonify({'warning': 'not a valid route'})


@app.route('/favicon.ico')
def favicon_route():
    return send_from_directory(
        app.root_path,
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon')


@app.route('/api/add_face', methods=['POST'])
def add_face_route():
    print('adding face')  # debug
    json_body = request.get_json()
    if KEY_PERSON in json_body and KEY_IMG in json_body:
        person_id = json_body[KEY_PERSON]
        img_str = json_body[KEY_IMG]
        return add_face(person_id, img_str)
    else:
        return jsonify({CONST_ERROR: 'Incomplete request body'})


@app.route('/api/predict', methods=['POST'])
def predict_route():
    print('predicting face')  # debug
    json_body = request.get_json()
    if KEY_IMG in json_body:
        img_str = json_body[KEY_IMG]
        return predict(img_str)
    else:
        return jsonify({CONST_ERROR: 'Incomplete request body'})


### METHODS ###

def add_face(person_id, img_str):
    try:
        img_bytes = base64.b64decode(str(img_str))
        img = Image.open(io.BytesIO(img_bytes))
        img = img.convert('RGB')
        img_arr = np.array(img)

        encodings = face_recognition.face_encodings(img_arr)
        face_count = len(encodings)

        if face_count < 1:
            return jsonify({CONST_ERROR: 'Face not found'})
        elif face_count > 1:
            return jsonify({CONST_ERROR: 'Too many faces in image'})
        else:
            encoding = encodings[0].tolist()
            id_str = (str(person_id)).encode('utf-8')
            file_name = base64.urlsafe_b64encode(id_str).decode('ascii')
            enc_file = os.path.join(ENC_FOLDER, file_name + '.enc')
            fio = open(enc_file, "w")
            fio.write(json.dumps(encoding))
            fio.close()
            print('encoding_id: ' + file_name)  # debug
            return jsonify({'encoding_id': file_name})
    except Exception as e:
        print('ERROR: ' + str(e))
        return jsonify({CONST_ERROR: str(e)})


def predict(img_str):
    try:
        img_bytes = base64.b64decode(str(img_str))
        img = Image.open(io.BytesIO(img_bytes))
        img = img.convert('RGB')
        img_arr = np.array(img)

        encodings = face_recognition.face_encodings(img_arr)
        face_count = len(encodings)

        if face_count < 1:
            return jsonify({CONST_ERROR: 'Face not found'})
        elif face_count > 1:
            return jsonify({CONST_ERROR: 'Too many faces in image'})
        else:
            unknown_face_encoding = encodings[0]
            # load encodings from file (/ db?)
            known_encodings = load_encodings(ENC_FOLDER)
            known_face_encodings = list(known_encodings.values())
            known_face_labels = list(known_encodings.keys())
            print('checking ' + str(len(known_face_labels)) + ' known faces')  # debug

            results = face_recognition.compare_faces(known_face_encodings, unknown_face_encoding)
            ids = []
            for idx in range(len(results)):
                if results[idx]:
                    label = known_face_labels[idx].replace(ENC_FILE, '')
                    person_id = base64.urlsafe_b64decode(label).decode('ascii')
                    ids.append({'person_id': person_id, 'encoding_id': label})

            return jsonify(ids)

    except Exception as e:
        print('ERROR: ' + str(e))
        return jsonify({CONST_ERROR: str(e)})


def load_encodings(encoding_path):
    encodings = {}

    enc_files = get_filelist(encoding_path, [ENC_FILE])

    for filename in enc_files:
        f = open(filename, "r")
        contents = f.read()
        f.close()

        encoding = json.loads(contents)  # convert from string to array
        encoding = np.array(encoding)  # convert to numpy array

        short_name = os.path.basename(filename)  # remove extension?
        encodings[short_name] = encoding

    return encodings


def get_filelist(path, extensions):
    filenames = []

    for root, dirs, files in os.walk(path):
        dirs.sort()
        files.sort()
        for file in files:
            filename = os.path.join(root, file)

            # check if file is right type
            f_name, f_extension = os.path.splitext(filename)
            if f_extension not in extensions:
                continue

            filenames.append(filename)

    return filenames


### ENTRY POINT ###

if __name__ == '__main__':
    if not os.path.exists(ENC_FOLDER):  # fix missing folders
        os.makedirs(ENC_FOLDER)
    app.run(host='0.0.0.0', debug=False)
