import uuid

import firebase_admin
from firebase_admin import App, credentials
from firebase_admin.credentials import Certificate
from google.cloud import firestore
from google.cloud.firestore import Client
from google.cloud.firestore_v1.base_query import FieldFilter

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
        guild_id: int,
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
            "guild_id": guild_id,
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
        self,
        event_id: str,
        collection_name: str = "Events",
    ) -> dict | None:
        try:
            doc_ref = self.db.collection(collection_name).document(event_id)
            doc_snapshot = doc_ref.get()
            event_data = doc_snapshot.to_dict()
            event_data["accepted_users"] = set(event_data.get("accepted_users", []))
            event_data["maybe_users"] = set(event_data.get("maybe_users", []))
            event_data["declined_users"] = set(event_data.get("declined_users", []))
            self.logger.info(f"Event {event_id} retrieved successfully!")
            return event_data
        except Exception as e:
            self.logger.exception(f"Error retrieving event: {e}")

    async def get_event_by_name(
        self,
        event_name: str,
        collection_name: str = "Events",
    ) -> dict | None:
        try:
            doc_ref = self.db.collection(collection_name)
            query = (
                doc_ref.where(filter=FieldFilter("name", "==", event_name))
                .limit(1)
                .stream()
            )
            for doc in query:
                event_data = doc.to_dict()
                event_data["accepted_users"] = set(event_data.get("accepted_users", []))
                event_data["maybe_users"] = set(event_data.get("maybe_users", []))
                event_data["declined_users"] = set(event_data.get("declined_users", []))
                self.logger.info(f"Event {event_name} retrieved successfully!")
                return event_data
            return None
        except Exception as e:
            self.logger.exception(f"Error retrieving event {event_name}: {e}")

    async def get_events_by_guild_id(
        self,
        guild_id: int,
        collection_name: str = "Events",
    ) -> list[dict] | None:
        events = []
        try:
            doc_ref = self.db.collection(collection_name)
            query = doc_ref.where(
                filter=FieldFilter("guild_id", "==", guild_id)
            ).stream()
            for doc in query:
                event_data = doc.to_dict()
                event_data["accepted_users"] = set(event_data.get("accepted_users", []))
                event_data["maybe_users"] = set(event_data.get("maybe_users", []))
                event_data["declined_users"] = set(event_data.get("declined_users", []))
                events.append(doc.to_dict())

            self.logger.info("Event Data retrieved from guild successfully")
            return events
        except Exception as e:
            self.logger.exception(f"Error retrieving events: {e}")

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
            self.logger.info(f"Event {event_id} deleted succesfully")
        except Exception as e:
            self.logger.exception(f"Error while deleting event {event_id}: {e}")

    async def delete_event_by_name(
        self,
        event_name: str,
        collection_name: str = "Events",
    ) -> bool | None:
        try:
            doc_ref = self.db.collection(collection_name)
            query = doc_ref.where(filter=FieldFilter("name", "==", event_name)).stream()
            docs = []
            # a bit hacky but works for now
            for doc in query:
                docs.append(doc)

            if not docs:
                return False

            for doc in docs:
                doc.reference.delete()
            self.logger.info(f"Event {event_name} deleted succesfully")
            return True
        except Exception as e:
            self.logger.exception(f"Error while deleting document {event_name}: {e}")
            return False


fb_service = FirebaseService()
