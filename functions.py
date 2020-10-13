import uuid

import face_recognition

import constants as const
import storage


# -- FUNCTIONS -- #


def add_face(io_stream):
    try:
        encodings = get_encodings(io_stream)
        face_count = len(encodings)

        if face_count == 1:
            encoding = encodings[0].tolist()
            identifier = str(uuid.uuid4()).encode('utf-8')
            return storage.store_encoding(identifier, encoding)
        else:
            return check_face_count(face_count)
    except Exception as e:
        print('ERROR: ' + str(e))
        return {const.ERROR_MSG: str(e)}


def predict(io_stream):
    try:
        encodings = get_encodings(io_stream)
        face_count = len(encodings)

        if face_count == 1:
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

            return ids
        else:
            return check_face_count(face_count)
    except Exception as e:
        print('ERROR: ' + str(e))
        return {const.ERROR_MSG: str(e)}


def remove(identifier):
    try:
        return storage.remove_encoding(identifier)
    except Exception as e:
        print('ERROR: ' + str(e))
        return {const.ERROR_MSG: str(e)}


# -- UTILITY METHODS -- #

def get_encodings(io_stream):
    img_arr = face_recognition.load_image_file(io_stream)
    return face_recognition.face_encodings(img_arr)


def check_face_count(face_count):
    if face_count < 1:
        return {const.ERROR_MSG: 'Face not found'}
    elif face_count > 1:
        return {const.ERROR_MSG: 'Too many faces in image'}
    else:
        return {}
