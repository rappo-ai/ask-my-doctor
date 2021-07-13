from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.doctor import get_doctors, print_doctor_summary


class ActionOnSearchSet(Action):
    def name(self) -> Text:
        return "action_on_search_set"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        speciality = tracker.get_slot("search__speciality")

        if not speciality:
            dispatcher.utter_message(
                json_message={
                    "text": "There are no specialities to choose from. Please use /help to contact support."
                }
            )
            return []

        doctors = get_doctors(
            speciality=speciality, onboarding_status="approved", listing_status="active"
        )
        if not doctors.count():
            dispatcher.utter_message(
                json_message={
                    "text": f"No doctors found for speciality '{speciality}'. Use /help to contact support."
                }
            )
            return []
        else:
            dispatcher.utter_message(json_message={"text": "Please choose a doctor:"})
        for d in doctors:
            reply_markup = {
                "keyboard": [
                    [
                        {
                            "title": "Book",
                            "payload": f"/EXTERNAL_create_appointment{{\"d_id\":\"{str(d['_id'])}\"}}",
                        }
                    ]
                ],
                "type": "inline",
            }
            caption = print_doctor_summary(d)

            json_message = {
                "photo": d["photo"],
                "caption": caption,
                "reply_markup": reply_markup,
            }
            dispatcher.utter_message(json_message=json_message)

        return []
