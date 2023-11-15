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
        author_name: str,
        name: str,
        start_date: str,
        end_date: str,
        accepted_users: set[str] = set(),
        maybe_users: set[str] = set(),
        declined_users: set[str] = set(),
        collection_name: str = "Events",
    ) -> str:
        event_id = str(uuid.uuid4())
        data_to_set = {
            "event_id": event_id,
            "author_name": author_name,
            "name": name,
            "start_date": start_date,
            "end_date": end_date,
            "accepted_users": list(accepted_users),
            "maybe_users": list(maybe_users),
            "declined_users": list(declined_users),
        }
        doc_ref = self.db.collection(collection_name).document(event_id)
        doc_ref.set(data_to_set)
        print(f"Data set in document {doc_ref.id}")
        return event_id

    # Maybe I should separate this out into separate functios?
    async def update_event_by_id(
        self,
        event_id,
        name: str = None,
        start_date: str = None,
        end_date: str = None,
        accepted_users: set[str] = None,
        maybe_users: set[str] = None,
        declined_users: set[str] = None,
        collection_name: str = "Events",
    ) -> None:
        doc_ref = self.db.collection(collection_name).document(event_id)

        if name is not None:
            doc_ref.update({"name": name})

        if start_date is not None:
            doc_ref.update({"start_date": start_date})

        if end_date is not None:
            doc_ref.update({"end_date": end_date})

        if (
            accepted_users is not None
            and maybe_users is not None
            and declined_users is not None
        ):
            doc_ref.update(
                {
                    "accepted_users": list(accepted_users),
                    "maybe_users": list(maybe_users),
                    "declined_users": list(declined_users),
                }
            )
        return

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
            event_data["accepted_users"] = set(event_data.get("accepted_users", []))
            event_data["maybe_users"] = set(event_data.get("maybe_users", []))
            event_data["declined_users"] = set(event_data.get("declined_users", []))
            print("Event Data retrieved Successfully")
            return event_data
        except NotFound:
            print("Document does not exist.")
            return


service = FirebaseService()
