from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.branding import get_bot_support_username
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
                "chat_id": doctor.get("user_id"),
                "text": "Please click the button to connect your Google ID.",
                "reply_markup": {
                    "keyboard": [
                        [
                            {
                                "title": "Connect Google ID",
                                "url": f"{get_google_auth_url(doctor.get('user_id'))}",
                            }
                        ]
                    ],
                    "type": "inline",
                },
            }
        )
        dispatcher.utter_message(
            text=f"Please contact {get_bot_support_username()} if you are unable to link your Google ID.\n\nClick /menu to go to the main menu."
        )
        return []
