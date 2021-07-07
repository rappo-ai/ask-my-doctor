from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.doctor import get_doctor_for_user_id
from actions.utils.meet import get_google_auth_url


class ActionCommandSetGoogleID(Action):
    def name(self) -> Text:
        return "action_command_setgoogleid"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        doctor = get_doctor_for_user_id(tracker.sender_id)
        if not doctor:
            return []
        dispatcher.utter_message(
            json_message={
                "chat_id": doctor["user_id"],
                "text": (
                    f"Please click this link to connect your Google ID -> {get_google_auth_url(doctor['user_id'])}.\n"
                ),
            }
        )
        return []
