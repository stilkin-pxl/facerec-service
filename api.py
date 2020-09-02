# https://github.com/ageitgey/face_recognition/blob/master/examples/web_service_example.py
# https://flask.palletsprojects.com/en/1.1.x/quickstart/

import os
from flask import Flask, jsonify, request, redirect, send_from_directory
import base64
from PIL import Image
import io
import numpy as np
import face_recognition
import json

# constants
CONST_ERROR = 'error'
KEY_PERSON = 'person_id'
KEY_IMG = 'image'
ENC_FOLDER = 'encodings'

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'warning': 'not a valid route'})

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        app.root_path,
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon')

@app.route('/api/add_face', methods=['GET', 'POST'])
def add_message():
    json_body = request.get_json()
    if KEY_PERSON in json_body and KEY_IMG in json_body:
        person_id = json_body[KEY_PERSON]
        print('person_id: ' + str(person_id)) # debug
        img_str = json_body[KEY_IMG]
        return add_face(person_id, img_str)
    else:
        return jsonify({CONST_ERROR: 'Incomplete request body'})

def add_face(person_id, img_str):
    try:
        img_bytes = base64.b64decode(str(img_str))
        img = Image.open(io.BytesIO(img_bytes))
        img = img.convert('RGB')
        img_arr = np.array(img)

        encodings = face_recognition.face_encodings(img_arr)
        face_count = len(encodings)
        print(str(face_count) + ' faces found')

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
            return jsonify({'encoding_id': file_name})
    except Exception as e:
        print('ERROR: ' + str(e))
        return jsonify({CONST_ERROR: str(e)})

if __name__ == '__main__':
    if not os.path.exists(ENC_FOLDER):  # fix missing folders
        os.makedirs(ENC_FOLDER)
    app.run(host= '0.0.0.0',debug=True)