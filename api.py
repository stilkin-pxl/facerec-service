# https://github.com/ageitgey/face_recognition/blob/master/examples/web_service_example.py
# https://flask.palletsprojects.com/en/1.1.x/quickstart/

import base64
import io
import os

from flask import Flask, jsonify, request, send_from_directory

import constants as const
import functions as func

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


@app.route(const.ROUTE_ADD, methods=['POST'])
def add_face_route():
    print('adding face')  # debug
    json_body = request.get_json()

    if const.KEY_IMG not in json_body:
        return jsonify({const.KEY_ERROR: 'Incomplete request body'})

    io_stream = string_to_stream(json_body[const.KEY_IMG])

    return jsonify(func.add_face(io_stream))


@app.route(const.ROUTE_PREDICT, methods=['POST'])
def predict_route():
    print('predicting face')  # debug
    json_body = request.get_json()

    if const.KEY_IMG not in json_body:
        return jsonify({const.KEY_ERROR: 'Incomplete request body'})

    io_stream = string_to_stream(json_body[const.KEY_IMG])
    return jsonify(func.predict(io_stream))


@app.route(const.ROUTE_REMOVE, methods=['POST'])
def remove_route():
    print('removing face')  # debug
    json_body = request.get_json()

    if const.KEY_ID not in json_body:
        return jsonify({const.KEY_ERROR: 'Incomplete request body'})

    identifier = json_body[const.KEY_ID]
    return jsonify(func.remove(identifier))


# -- UTILITY METHODS -- #

def string_to_stream(img_str):
    img_bytes = base64.b64decode(str(img_str))
    return io.BytesIO(img_bytes)


# -- ENTRY POINT -- #


if __name__ == '__main__':
    if not os.path.exists(const.ENC_FOLDER):  # fix missing folders
        os.makedirs(const.ENC_FOLDER)
    app.run(host='0.0.0.0', debug=True)
    # app.run(host='0.0.0.0', ssl_context='adhoc', port='443', debug=False) # for https
