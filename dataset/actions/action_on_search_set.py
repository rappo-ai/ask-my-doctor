from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.doctor import get_doctors_for_speciality, print_doctor_summary


class ActionOnSearchSet(Action):
    def name(self) -> Text:
        return "action_on_search_set"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(json_message={"text": "Please choose a doctor:"})

        speciality = tracker.get_slot("search__speciality")
        doctors = get_doctors_for_speciality(speciality)
        for d in doctors:
            reply_markup = {
                "keyboard": [
                    [
                        {
                            "title": "Book",
                            "payload": f"/EXTERNAL_create_appointment{{\"doctor_id\":{d['_id']}}}",
                        }
                    ]
                ],
                "type": "inline",
            }
            text = print_doctor_summary(d)

            json_message = {"text": text, "reply_markup": reply_markup}
            dispatcher.utter_message(json_message=json_message)

        return []