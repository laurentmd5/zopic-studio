import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis

class FaceAnalyzer:
    def __init__(self):
        # Initialize InsightFace with Buffalo_L model (ResNet50)
        self.app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

    def extract_faces(self, image_bytes: bytes):
        """
        Extrait tous les visages d'une image (bytes)
        et renvoie une liste de vecteurs (embeddings) 512-d.
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        # Decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return []

        # Analyze faces
        faces = self.app.get(img)
        
        # Return a list of embeddings (numpy arrays)
        embeddings = [face.embedding.tolist() for face in faces]
        return embeddings

face_analyzer = FaceAnalyzer()
