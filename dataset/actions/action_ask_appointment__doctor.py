from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.sheets import get_doctors_for_speciality


class ActionAskAppointmentDoctor(Action):
    def name(self) -> Text:
        return "action_ask_appointment__doctor"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        text = f"Please choose a doctor:"
        reply_markup = {
            "keyboard": [
                [s.get("name")]
                for s in get_doctors_for_speciality(
                    tracker.get_slot("appointment__speciality")
                )
            ],
        }
        json_message = {"text": text, "reply_markup": reply_markup}
        dispatcher.utter_message(json_message=json_message)

        return []
