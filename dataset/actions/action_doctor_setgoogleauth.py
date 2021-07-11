import logging
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import get_admin_group_id
from actions.utils.doctor import (
    get_doctor_for_user_id,
    update_doctor,
)
from actions.utils.entity import get_entity

logger = logging.getLogger(__name__)


class ActionDoctorSetGoogleAuth(Action):
    def name(self) -> Text:
        return "action_doctor_setgoogleauth"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get("entities", [])

        credentials: Dict = get_entity(
            entities, "credentials", {"access_token": "dummyaccesstoken"}
        )

        user_id = tracker.sender_id
        doctor = get_doctor_for_user_id(user_id)
        if doctor:
            doctor["credentials"] = credentials

            update_doctor(doctor)

            dispatcher.utter_message(
                json_message={
                    "chat_id": get_admin_group_id(),
                    "text": f"{doctor['name']} with ID #{doctor['_id']}, Google account with email {doctor['email']} has been linked.",
                }
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": doctor["user_id"],
                    "text": f'Your Google account with email {doctor["email"]} has been linked.',
                }
            )
        else:
            logger.error("action_doctor_setgoogleauth doctor not found for user_id")

        return []
