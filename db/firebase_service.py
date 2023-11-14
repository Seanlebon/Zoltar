import firebase_admin
from firebase_admin import App, credentials, firestore
from firebase_admin.credentials import Certificate

from config import GOOGLE_CREDS


class FirebaseService:
    creds: Certificate
    app: App

    def __init__(self):
        # Application Default credentials are automatically created.
        self.creds = credentials.Certificate(GOOGLE_CREDS)
        self.app = firebase_admin.initialize_app()
        self.db = firestore.client()
