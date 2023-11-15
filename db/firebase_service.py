import uuid

import firebase_admin
from firebase_admin import App, credentials
from firebase_admin.credentials import Certificate
from google.api_core.client_options import ClientOptions
from google.cloud import firestore
from google.cloud.exceptions import NotFound
from google.cloud.firestore_v1.base_query import FieldFilter

from config import FIRESTORE_PROJECT_ID, GOOGLE_CREDS


class FirebaseService:
    creds: Certificate
    app: App

    def __init__(self):
        # Application Default credentials are automatically created.
        self.creds = credentials.Certificate(GOOGLE_CREDS)
        self.app = firebase_admin.initialize_app()
        self.db = firestore.Client(project=FIRESTORE_PROJECT_ID)

    async def create_db_event(
        self,
        creator_name: str,
        name: str,
        date: str,
        accepted_users: set[str] = set(),
        maybe_users: set[str] = set(),
        declined_users: set[str] = set(),
        collection_name: str = "Events",
    ):
        event_id = str(uuid.uuid4())
        data_to_set = {
            "event_id": event_id,
            "creator_name": creator_name,
            "name": name,
            "date": date,
            "accepted_users": list(accepted_users),
            "maybe_users": list(maybe_users),
            "declined_users": list(declined_users),
        }
        doc_ref = self.db.collection(collection_name).document(event_id)
        doc_ref.set(data_to_set)
        print(f"Data set in document {doc_ref.id}")

    async def get_user_by_id(
        self, user_id: str, collection_name: str = "Users"
    ) -> dict | None:
        doc_ref = self.db.collection(collection_name).document(user_id)
        try:
            doc_snapshot = doc_ref.get()
            user_data = doc_snapshot.to_dict()
            print("User Data retrieved Successfully")
        except NotFound:
            print("Document does not exist.")

        return user_data

    async def get_event_by_id(
        self, event_id: str, collection_name: str = "Events"
    ) -> dict | None:
        doc_ref = self.db.collection(collection_name).document(event_id)
        try:
            doc_snapshot = doc_ref.get()
            event_data = doc_snapshot.to_dict()
            print("Event Data retrieved Successfully")
        except NotFound:
            print("Document does not exist.")

        event_data["accepted_users"] = set(event_data.get("accepted_users", []))
        event_data["maybe_users"] = set(event_data.get("maybe_users", []))
        event_data["declined_users"] = set(event_data.get("declined_users", []))
        return event_data
