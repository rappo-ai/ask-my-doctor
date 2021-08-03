from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.branding import get_bot_support_username


class ActionAskDoctorSignupGmailId(Action):
    def name(self) -> Text:
        return "action_ask_doctor_signup__gmail_id"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        text = (
            "What is your Gmail id?\n"
            + "\n"
            + f"We need a valid Gmail id to schedule appointments on your behalf. If you do not have a Gmail id, please visit https://www.gmail.com to create one. Contact {get_bot_support_username()} for more help.\n"
        )
        json_message = {"text": text, "disable_web_page_preview": True}
        dispatcher.utter_message(json_message=json_message)

        return []
