import base64
import json
import os

import numpy as np

import constants as const


# -- IO METHODS -- #


def store_encoding(identifier, encoding):
    file_name = base64.urlsafe_b64encode(identifier).decode('ascii')
    enc_file = os.path.join(const.ENC_FOLDER, file_name + '.enc')
    fio = open(enc_file, "w")
    fio.write(json.dumps(encoding))
    fio.close()
    print('encoding_id: ' + file_name)  # debug
    return {const.KEY_ID: file_name}


def load_encodings():
    # find all encoding files
    enc_files = []
    for root, dirs, files in os.walk(const.ENC_FOLDER):
        dirs.sort()
        files.sort()
        for file in files:
            filename = os.path.join(root, file)

            # check if file is right type
            f_name, f_extension = os.path.splitext(filename)
            if f_extension != const.ENC_FILE:
                continue

            enc_files.append(filename)

    # read all encodings from them
    encodings = {}
    for filename in enc_files:
        f = open(filename, "r")
        contents = f.read()
        f.close()

        encoding = json.loads(contents)  # convert from string to array
        encoding = np.array(encoding)  # convert to numpy array

        short_name = os.path.basename(filename)  # remove extension?
        encodings[short_name] = encoding

    return encodings


def remove_encoding(identifier):
    enc_file = os.path.join(const.ENC_FOLDER, identifier + '.enc')
    if os.path.exists(enc_file):
        os.remove(enc_file)
        return {const.KEY_ID: identifier}  # ok
    else:
        return {const.ERROR_MSG: 'File not found'}
