import uuid

import firebase_admin
from firebase_admin import App, credentials
from firebase_admin.credentials import Certificate
from google.cloud import firestore
from google.cloud.firestore import Client

from config import FIRESTORE_PROJECT_ID, GOOGLE_CREDS
from utils.logger import logger


class FirebaseService:
    creds: Certificate
    app: App
    db: Client

    def __init__(self):
        # Application Default credentials are automatically created.
        self.creds = credentials.Certificate(GOOGLE_CREDS)
        self.app = firebase_admin.initialize_app()
        self.db = firestore.Client(project=FIRESTORE_PROJECT_ID)
        self.logger = logger

    async def create_db_event(
        self,
        author_name: str,
        name: str,
        start_time: str,
        end_time: str,
        accepted_users: set[str] = set(),
        maybe_users: set[str] = set(),
        declined_users: set[str] = set(),
        collection_name: str = "Events",
    ) -> str | None:
        event_id = str(uuid.uuid4())
        data_to_set = {
            "event_id": event_id,
            "author_name": author_name,
            "name": name,
            "start_time": start_time,
            "end_time": end_time,
            "accepted_users": list(accepted_users),
            "maybe_users": list(maybe_users),
            "declined_users": list(declined_users),
        }
        try:
            doc_ref = self.db.collection(collection_name).document(event_id)
            doc_ref.set(data_to_set)
            self.logger.info(f"Data set in document {doc_ref.id}")
            return event_id
        except Exception as e:
            self.logger.exception(f"Error creating event: {e}")

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
            self.logger.info("Event Data retrieved Successfully")
            return event_data
        except Exception as e:
            self.logger.exception(f"Error retrieving event: {e}")

    async def get_events_by_guild(
        self,
        guild,
    ):
        pass

    # Maybe I should separate this out into separate functios?
    async def update_event_by_id(
        self,
        event_id,
        name: str = None,
        start_time: str = None,
        end_time: str = None,
        accepted_users: set[str] = None,
        maybe_users: set[str] = None,
        declined_users: set[str] = None,
        collection_name: str = "Events",
    ) -> None:
        try:
            doc_ref = self.db.collection(collection_name).document(event_id)

            if name is not None:
                doc_ref.update({"name": name})

            if start_time is not None:
                doc_ref.update({"start_time": start_time})

            if end_time is not None:
                doc_ref.update({"end_time": end_time})

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
        except Exception as e:
            self.logger.exception(f"Error while updating document: {e}")

    async def delete_event_by_id(
        self,
        event_id: str,
        collection_name: str = "Events",
    ) -> None:
        try:
            doc_ref = self.db.collection(collection_name).document(event_id)
            doc_ref.delete()
        except Exception as e:
            self.logger.exception(f"Error while deleting document: {e}")


service = FirebaseService()
