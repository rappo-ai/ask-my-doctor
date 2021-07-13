from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import get_specialities
from actions.utils.buttons import add_padding


class ActionAskDoctorSignupSpeciality(Action):
    def name(self) -> Text:
        return "action_ask_doctor_signup__speciality"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        text = f"Please select your speciality:"
        specialities = get_specialities()
        row_width = 2
        add_padding(specialities, row_width)
        reply_markup = {
            "keyboard": [[s for s in specialities]],
            "resize_keyboard": True,
            "row_width": row_width,
        }
        json_message = {"text": text, "reply_markup": reply_markup}
        dispatcher.utter_message(json_message=json_message)

        return []
