# facerec-service
A simple face recognition web service in Python

This Python script produces a REST API in Flask to expose a face recognition web service.
The script uses https://github.com/ageitgey/face_recognition in the background, so this will be installed as well.

### installation instructions
* install **cmake** (required for *face_recognition* library): `sudo apt install cmake` 
* install python dependencies: `pip install -r requirements.txt`

## usage instructions
* run script with `python3 api.py`

This will expose two **POST** routes both expecting JSON bodies:
* */api/add_face*
* */api/predict*

### add_face
**Request body**:  
(the image should be base64 encoded)
```json
{
	"image": "A96SaAKHH8Ukc16XJe4p5w=="
}
```

**Response body success**: you get a unique identifier for the image you added
```json
{
	"identifier": "MzM1MmM1MDctODM0OC00NDk3LTg5ZWMtOWVlMTFkNzk0MDEx"
}
```

### predict
**Request body**:  
(the image should be base64 encoded)
```json
{
	"image": "A96SaAKHH8Ukc16XJe4p5w=="
}
```

**Response body success**: you will get a list with all matching identifiers
```json
[{
	"identifier": "MmQyYzdhY2UtYzExMC00NjI3LWJkNDQtODQ4OTNiNjgyOTBi"
}, {
	"identifier": "MzM1MmM1MDctODM0OC00NDk3LTg5ZWMtOWVlMTFkNzk0MDEx"
}]
```

### errors
**Response body error**:
```json
{
	"error": "Face not found"
}
```
Possible errors:
* Face not found
* Too many faces in image
* (other, less specific errors)
