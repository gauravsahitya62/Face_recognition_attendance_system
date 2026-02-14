"""Face recognition utilities for attendance marking."""
import os
import numpy as np
import face_recognition
from PIL import Image
import io


def get_face_encoding_from_image(image_path):
    """Load image and return face encoding. Returns None if no face found."""
    if not os.path.exists(image_path):
        return None
    img = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(img)
    return encodings[0] if encodings else None


def get_face_encoding_from_bytes(image_bytes):
    """Convert image bytes to face encoding. Returns None if no face found."""
    img = Image.open(io.BytesIO(image_bytes))
    img_array = np.array(img)
    if len(img_array.shape) == 2:
        img_array = np.stack([img_array] * 3, axis=-1)
    elif img_array.shape[2] == 4:
        img_array = img_array[:, :, :3]
    encodings = face_recognition.face_encodings(img_array)
    return encodings[0] if encodings else None


def verify_face(captured_image_bytes, known_encoding, tolerance=0.55):
    """
    Compare captured webcam image with known face encoding.
    Returns True if match, False otherwise.
    tolerance: higher = more lenient (default 0.6 in library, we use 0.55 for slightly stricter)
    """
    if known_encoding is None:
        return False
    captured_encoding = get_face_encoding_from_bytes(captured_image_bytes)
    if captured_encoding is None:
        return False
    distance = face_recognition.face_distance([known_encoding], captured_encoding)[0]
    return distance <= tolerance
