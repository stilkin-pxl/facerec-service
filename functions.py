import base64
import io
import uuid

import face_recognition
from flask import jsonify

import constants as const
import storage


# -- FUNCTIONS -- #


def process_request(post_req):
    route = str(post_req.url_rule)
    json_body = post_req.get_json()

    if const.KEY_IMG not in json_body:
        return jsonify({const.ERROR_MSG: 'Incomplete request body'})

    img_str = json_body[const.KEY_IMG]
    try:
        img_bytes = base64.b64decode(str(img_str))
        io_stream = io.BytesIO(img_bytes)

        img_arr = face_recognition.load_image_file(io_stream)
        encodings = face_recognition.face_encodings(img_arr)
        face_count = len(encodings)

        if face_count < 1:
            return jsonify({const.ERROR_MSG: 'Face not found'})
        elif face_count > 1:
            return jsonify({const.ERROR_MSG: 'Too many faces in image'})
        else:
            if const.ROUTE_PREDICT is route:
                return predict(encodings)
            else:
                return add_face(encodings)
    except Exception as e:
        print('ERROR: ' + str(e))
        return jsonify({const.ERROR_MSG: str(e)})


def add_face(encodings):
    try:
        encoding = encodings[0].tolist()
        identifier = str(uuid.uuid4()).encode('utf-8')
        return storage.store_encoding(identifier, encoding)
    except Exception as e:
        print('ERROR: ' + str(e))
        return jsonify({const.ONST_ERROR: str(e)})


def predict(encodings):
    try:
        unknown_face_encoding = encodings[0]
        known_encodings = storage.load_encodings()  # load encodings from file (/ db?)

        known_face_encodings = list(known_encodings.values())
        known_face_labels = list(known_encodings.keys())
        print('checking ' + str(len(known_face_labels)) + ' known faces')  # debug

        results = face_recognition.compare_faces(known_face_encodings, unknown_face_encoding)
        ids = []
        for idx in range(len(results)):
            if results[idx]:
                label = known_face_labels[idx].replace(const.ENC_FILE, '')
                ids.append({const.KEY_ID: label})

        return jsonify(ids)
    except Exception as e:
        print('ERROR: ' + str(e))
        return jsonify({const.ERROR_MSG: str(e)})


def remove(post_req):
    json_body = post_req.get_json()

    if const.KEY_ID not in json_body:
        return jsonify({const.ERROR_MSG: 'Incomplete request body'})

    identifier = json_body[const.KEY_ID]

    try:
        return storage.remove_encoding(identifier)
    except Exception as e:
        print('ERROR: ' + str(e))
        return jsonify({const.ERROR_MSG: str(e)})
