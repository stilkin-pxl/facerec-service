# https://github.com/ageitgey/face_recognition/blob/master/examples/web_service_example.py
# https://flask.palletsprojects.com/en/1.1.x/quickstart/

import base64
import io
import json
import os
import uuid

import face_recognition
import numpy as np
from PIL import Image
from flask import Flask, jsonify, request, send_from_directory

# constants
ENC_FOLDER = 'encodings'
ENC_FILE = '.enc'
CONST_ERROR = 'error'
KEY_IMG = 'image'
KEY_ID = 'identifier'
ROUTE_ADD = '/api/add_face'
ROUTE_PREDICT = '/api/predict'

app = Flask(__name__)


# -- ROUTES -- #


@app.route('/')
def index_route():
    return jsonify({'warning': 'not a valid route'})


@app.route('/favicon.ico')
def favicon_route():
    return send_from_directory(
        app.root_path,
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon')


@app.route(ROUTE_ADD, methods=['POST'])
def add_face_route():
    print('adding face')  # debug
    return process_request(request)


@app.route('/api/predict', methods=['POST'])
def predict_route():
    print('predicting face')  # debug
    return process_request(request)


@app.route('/api/remove', methods=['POST'])
def remove():
    print('removing face')  # debug
    return remove_face(request)


# -- FUNCTIONS -- #


def process_request(post_req):
    route = str(post_req.url_rule)
    json_body = post_req.get_json()

    if KEY_IMG not in json_body:
        return jsonify({CONST_ERROR: 'Incomplete request body'})

    img_str = json_body[KEY_IMG]
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
            if ROUTE_PREDICT is route:
                return predict(encodings)
            else:
                return add_face(encodings)
    except Exception as e:
        print('ERROR: ' + str(e))
        return jsonify({CONST_ERROR: str(e)})


def add_face(encodings):
    try:
        encoding = encodings[0].tolist()
        id_str = str(uuid.uuid4()).encode('utf-8')
        file_name = base64.urlsafe_b64encode(id_str).decode('ascii')
        enc_file = os.path.join(ENC_FOLDER, file_name + '.enc')
        fio = open(enc_file, "w")
        fio.write(json.dumps(encoding))
        fio.close()
        print('encoding_id: ' + file_name)  # debug
        return jsonify({KEY_ID: file_name})
    except Exception as e:
        print('ERROR: ' + str(e))
        return jsonify({CONST_ERROR: str(e)})


def predict(encodings):
    try:
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
                ids.append({KEY_ID: label})

        return jsonify(ids)
    except Exception as e:
        print('ERROR: ' + str(e))
        return jsonify({CONST_ERROR: str(e)})


def remove_face(post_req):
    json_body = post_req.get_json()

    if KEY_ID not in json_body:
        return jsonify({CONST_ERROR: 'Incomplete request body'})

    file_id = json_body[KEY_ID]

    try:
        enc_file = os.path.join(ENC_FOLDER, file_id + '.enc')
        if os.path.exists(enc_file):
            os.remove(enc_file)
            return jsonify({KEY_ID: file_id})  # ok
        else:
            return jsonify({CONST_ERROR: 'File not found'})
    except Exception as e:
        print('ERROR: ' + str(e))
        return jsonify({CONST_ERROR: str(e)})

# -- UTILITY METHODS -- #


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


# -- ENTRY POINT -- #

if __name__ == '__main__':
    if not os.path.exists(ENC_FOLDER):  # fix missing folders
        os.makedirs(ENC_FOLDER)
    app.run(host='0.0.0.0', debug=True)
    # app.run(host='0.0.0.0', ssl_context='adhoc', port='443', debug=False) # for https
